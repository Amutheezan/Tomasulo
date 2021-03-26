'''
1. broadcast data on cdb 
2. fetch data from results queue 
3. remove entry in results queue
'''


# function: find reorder_buffer entry by tag
def find_reorder_buffer_entry(reorder_buffer, tag):
    index = -1
    for index in range(len(reorder_buffer)):
        if reorder_buffer[index].reorder_buffer_tag == tag:
            break
    return index


# function: broadcast
# rat_int, rat_fp, reservation stations, ld_sd_queue, reorder_buffer
def broadcast(cdb, rat_int, rat_fp,
              rs_int_adder, rs_fp_adder, rs_fp_multi,
              ld_sd_queue, reorder_buffer, cycle):
    # dest_tag
    dest_tag = cdb.dest_tag
    index = find_reorder_buffer_entry(reorder_buffer, dest_tag)
    reg_tag = reorder_buffer[index].dest_tag
    # rat_int
    if reg_tag[0] == 'R':
        rat_int[int(reg_tag[1:])] = cdb.value
    # rat_fp
    if reg_tag[0] == 'F':
        rat_fp[int(reg_tag[1:])] = cdb.value
        # rs list
    rs_list = [rs_int_adder, rs_fp_adder, rs_fp_multi]
    for rs in rs_list:
        for element in rs:
            if (element.tag_1st == dest_tag) & (element.valid_1st == 0):
                element.value_1st = cdb.value
                element.valid_1st = 1
            if (element.tag_2nd == dest_tag) & (element.valid_2nd == 0):
                element.value_2nd = cdb.value
                element.valid_2nd = 1

    # ld_sd_queue
    for element in ld_sd_queue:
        if (element.data == dest_tag) & (element.op == 'Sd'):
            element.data = cdb.value
        if (element.reg_tag == dest_tag) & (element.valid == 0):
            element.reg_value = cdb.value
            element.valid = 1
    # reorder_buffer
    for element in reorder_buffer:
        if element.reorder_buffer_tag == dest_tag:
            element.value = cdb.value
            element.cdb.append(cycle)


# function: wb
def wb(cdb, rat_int, rat_fp,
       rs_int_adder, rs_fp_adder, rs_fp_multi,
       ld_sd_queue, reorder_buffer, cycle,
       results_buffer, issue_width):
    # broadcast
    bd_count = 0
    while len(results_buffer) > 0 and (bd_count < issue_width):
        cdb.valid = 1
        cdb.value = results_buffer[0].value
        cdb.dest_tag = results_buffer[0].dest_tag
        results_buffer.popleft()
        broadcast(cdb, rat_int, rat_fp,
                  rs_int_adder, rs_fp_adder, rs_fp_multi,
                  ld_sd_queue, reorder_buffer, cycle)
        bd_count += 1
