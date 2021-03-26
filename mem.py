'''
1. Ld forward check from Sd in ld_sd_queue
    -- only check nearest Sd instruction
2. execute LD/SD instruction in ld_sd_mem
    -- once LD instruction gets data, write back to ld_sd_queue
    -- LD instruction should be removed after get data  
    -- SD instruction should be removed at commit stage 
3. fetch new LD/SD instruction into ld_sd_mem
    -- if first element is SD, ready and has valid data, only SD to be committed can be fetched into ld_sd_mem 
    -- else put the first no-matched Ld into ld_sd_mem    
'''
from init import fu_result, ld_sd_mem


# function: forward check from sd
# only check nearest sd
def forward_check_from_sd(ld_sd_queue, index):
    data = []
    for i in reversed(range(index)):
        if (ld_sd_queue[i].op == 'Sd'):
            if (ld_sd_queue[i].address == ld_sd_queue[index].address):
                if (type(ld_sd_queue[i].data) == int) | (type(ld_sd_queue[i].data) == float):
                    data.append(ld_sd_queue[i].data)
            break
    return data


# function: check if previous all Sds are ready and un-matched
def check_all_previous_Sd_no_match(ld_sd_queue, index):
    flag = True
    for i in range(index):
        # all Sd instructions
        if (ld_sd_queue[i].op == 'Sd'):
            if ld_sd_queue[i].ready == 0:
                flag = False
                break
            elif (ld_sd_queue[i].address == ld_sd_queue[index].address):
                flag = False
                break
            else:
                pass
    return flag


# function: find reorder_buffer entry by tag
def find_ROB_entry(reorder_buffer, tag):
    index = -1
    for index in range(len(reorder_buffer)):
        if reorder_buffer[index].reorder_buffer_tag == tag:
            break
    return index


# function: put entry into ld_sd_mem
def put_entry_into_ld_sd_mem(ld_sd_mem, entry):
    ld_sd_mem.busy = 1
    ld_sd_mem.cycle = 0
    ld_sd_mem.address = entry.address
    ld_sd_mem.dest_tag = entry.dest_tag
    ld_sd_mem.op = entry.op
    if ld_sd_mem.op == 'Sd':
        ld_sd_mem.data = entry.data


# function: check if Sd to be committed in next cycle
def check_if_sd_committable(ld_sd_queue, reorder_buffer):
    flag = False
    if ld_sd_queue[0].ldsd_tag == reorder_buffer[0].dest_tag:
        flag = True
    if ld_sd_queue[0].ldsd_tag == reorder_buffer[1].dest_tag:
        # previous ins has been broadcasted
        if len(reorder_buffer[0].cdb) != 0:
            flag = True
    return flag


# function: mem
def mem(ld_sd_queue, ld_sd_mems, time_ld_sd_mem, results_buffer, memory, reorder_buffer, cycle):
    '''look forward check for all Ld instructions'''
    index = -1
    remove_list = []
    for element in ld_sd_queue:
        index += 1
        if (index >= 1) & (element.op == 'Ld') & (element.ready == 1):
            data = forward_check_from_sd(ld_sd_queue, index)
            if len(data) > 0:
                # Ld gets data 
                results_buffer.append(fu_result())
                results_buffer[-1].value = data[0]
                results_buffer[-1].dest_tag = element.dest_tag
                # remove the Ld instruction
                remove_list.append(element)
                # write mem cylce in reorder_buffer
                index = find_ROB_entry(reorder_buffer, element.dest_tag)
                reorder_buffer[index].mem.append(cycle)
    # remove lookforwared Ld
    for element in remove_list:
        ld_sd_queue.remove(element)

    for ld_sd_mem_queue in ld_sd_mems:
        ld_sd_mem_obj = ld_sd_mem()
        ld_sd_mem_obj.busy = 0
        '''fetch new instruction into ld_sd_mem'''
        if (len(ld_sd_queue) > 0):
            # flag_1st_ldsd
            flag_1st_ldsd_sent = False
            # fetch the ld_sd_queue header if it's Sd, ready and to be committed
            if (ld_sd_queue[0].op == 'Sd'):
                # check if this Sd is ready and to be commited
                if (ld_sd_queue[0].ready == 1):
                    # check to be committed in next cycle
                    if (check_if_sd_committable):
                        # already have data in Sd
                        if (type(ld_sd_queue[0].data) == int) | (type(ld_sd_queue[0].data) == float):
                            # put the Sd entry into ld_sd_mem
                            entry = ld_sd_queue.popleft()
                            put_entry_into_ld_sd_mem(ld_sd_mem_obj, entry)
                            flag_1st_ldsd_sent = True
                            ld_sd_mem_obj.busy = 1

            # if the 1st Sd is not sent to ld_sd_mem, or the 1st is not Sd
            if (flag_1st_ldsd_sent == False):
                for index in range(len(ld_sd_queue)):
                    # ready Ld
                    if (ld_sd_queue[index].op == 'Ld') & (ld_sd_queue[index].ready == 1):
                        # haven't got data
                        if (type(ld_sd_queue[0].data) != int) & (type(ld_sd_queue[0].data) != float):
                            # all previous Sd instructions are ready but no address match
                            if check_all_previous_Sd_no_match(ld_sd_queue, index):
                                put_entry_into_ld_sd_mem(ld_sd_mem_obj, ld_sd_queue[index])
                                ld_sd_queue.remove(ld_sd_queue[index])
                                ld_sd_mem_obj.busy = 1
                                break
        ld_sd_mem_queue.append(ld_sd_mem_obj)

    for ld_sd_mem_queue in ld_sd_mems:
        for ld_sd_mem_obj in ld_sd_mem_queue:
            '''ld_sd_mem execution'''
            if ld_sd_mem_obj.busy == 1:
                # write mem starting cycle
                if ld_sd_mem_obj.cycle == 0:
                    index = find_ROB_entry(reorder_buffer, ld_sd_mem_obj.dest_tag)
                    reorder_buffer[index].mem.extend([cycle, cycle + time_ld_sd_mem - 1])
                    # for Sd, write commit cycle
                    if ld_sd_mem_obj.op == 'Sd':
                        reorder_buffer[index].commit.append(cycle)

                # cycle ++
                ld_sd_mem_obj.cycle += 1
                # get the data for Ld or reach the memory for Sd
                if ld_sd_mem_obj.cycle == time_ld_sd_mem:
                    ld_sd_mem.busy = 0
                    if ld_sd_mem_obj.op == 'Ld':
                        # put Ld data into results_buffer
                        address = ld_sd_mem_obj.address
                        data = memory[address]
                        results_buffer.append(fu_result())
                        results_buffer[-1].value = data
                        results_buffer[-1].dest_tag = ld_sd_mem_obj.dest_tag
                    # put data into memory for Sd
                    else:
                        memory[ld_sd_mem_obj.address] = ld_sd_mem_obj.data
