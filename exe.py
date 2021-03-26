'''
1. calculate valid instructions
    -- for ALU instructions, write results into fu_results, remove that fu entry  
    -- for LD/SD, write address result immediately back to ld_sd_queue
2. fetch instructions into function unit with spare space
    -- remove ALU instructions from rs
    -- don't remove ld/sd instructions
'''
from init import fu_entry, fu_result

cycle_call_history = {}
cycle_insert_history = {}


# function: check rs and return valid instruction index
def check_valid_ins_in_rs(rs, reorder_buffer, cycle):
    index = -1
    if len(rs) != 0:
        possible_indices = []
        issue_counters = []
        for i in range(len(rs)):
            if (rs[i].valid_1st == 1) & \
                    (rs[i].valid_2nd == 1) \
                    & (rs[i].busy == 1):
                possible_indices.append(i)
                index_r = find_reorder_buffer_entry(reorder_buffer, rs[i].dest_tag)
                issue_counters.append(reorder_buffer[index_r].counter)

        if len(possible_indices) > 0:
            while len(issue_counters) > 0:
                dependent = False
                min_index = issue_counters.index(min(issue_counters))
                index_t = possible_indices[min_index]
                index_p = find_reorder_buffer_entry(reorder_buffer, rs[index_t].dest_tag)
                selected_rob = reorder_buffer[index_p]
                for i, rob_x in enumerate(reorder_buffer):
                    if selected_rob.op == "Addi":
                        dependent = False
                    else:
                        if rob_x.issue[0] < selected_rob.issue[0] and \
                                len(rob_x.cdb) == 0 and rob_x.counter < selected_rob.counter:
                            if selected_rob.tag_1st == rob_x.dest_tag \
                                    or selected_rob.tag_2nd == rob_x.dest_tag:
                                dependent = True
                        if rob_x.issue[0] <= selected_rob.issue[0] and \
                                len(rob_x.cdb) == 1 and rob_x.cdb[0] == cycle \
                                and rob_x.counter < selected_rob.counter:
                            if selected_rob.tag_1st == rob_x.dest_tag \
                                    or selected_rob.tag_2nd == rob_x.dest_tag:
                                dependent = True
                if not dependent:
                    index = possible_indices[min_index]
                    break
                else:
                    if len(issue_counters) >= 1:
                        issue_counters.pop(min_index)
                        possible_indices.pop(min_index)
    return index


# function: check ld_sd_queue and return valid instruction index
def check_valid_ins_in_ldsd(ldsd, reorder_buffer, cycle):
    index = -1
    if len(ldsd) != 0:
        for i in range(len(ldsd)):
            if (ldsd[i].valid == 1) & (ldsd[i].ready == 0):
                dependent = False
                index_p = find_reorder_buffer_entry(reorder_buffer, ldsd[i].dest_tag)
                selected_rob = reorder_buffer[index_p]
                for x, rob_x in enumerate(reorder_buffer):
                    if rob_x.issue[0] <= selected_rob.issue[0] \
                            and len(rob_x.cdb) == 1 and \
                            rob_x.cdb[0] == cycle:
                        if selected_rob.reg_tag == rob_x.dest_tag:
                            dependent = True
                if not dependent:
                    index = i
                    break
    return index


# function: add entry into fu
def add_entry_into_fu(fu, ins_in_rs):
    fu[-1].cycle = 0
    fu[-1].op = ins_in_rs.op
    fu[-1].value1 = ins_in_rs.value_1st
    fu[-1].value2 = ins_in_rs.value_2nd
    fu[-1].dest_tag = ins_in_rs.dest_tag
    fu[-1].counter = ins_in_rs.counter


# function: find reorder_buffer entry by tag
def find_reorder_buffer_entry(reorder_buffer, tag):
    index = -1
    for index in range(len(reorder_buffer)):
        if reorder_buffer[index].reorder_buffer_tag == tag:
            break
    return index


# function: functional units execution
def fu_exe(fus, fu_results, reorder_buffer, time_fu, cycle, program_counter):
    for fu in fus:
        if len(fu) != 0:
            for element in fu:
                if (element, cycle) not in cycle_call_history.keys():
                    element.cycle += 1
                    cycle_call_history[(element, cycle)] = 1
            # write starting cycle
            if fu[-1].cycle == 1:
                if (fu[-1], cycle) not in cycle_insert_history.keys():
                    index = find_reorder_buffer_entry(reorder_buffer, fu[-1].dest_tag)
                    reorder_buffer[index].exe.append(cycle)
                    cycle_insert_history[(fu[-1], cycle)] = 1
            # finish cycle
            if fu[0].cycle == time_fu:
                index = find_reorder_buffer_entry(reorder_buffer, fu[0].dest_tag)
                reorder_buffer[index].exe.append(cycle)
                # calculation result
                fu_results.append(fu_result())
                fu_results[-1].dest_tag = fu[0].dest_tag
                if (fu[0].op == 'Add') | (fu[0].op == 'Add.d') | (fu[0].op == 'Addi'):
                    fu_results[-1].value = fu[0].value1 + fu[0].value2
                elif (fu[0].op == 'Sub') | (fu[0].op == 'Sub.d'):
                    fu_results[-1].value = fu[0].value1 - fu[0].value2
                elif fu[0].op == 'Mult.d':
                    fu_results[-1].value = fu[0].value1 * fu[0].value2
                elif fu[0].op == 'Bne':
                    fu_results.pop()
                    if fu[0].value1 == fu[0].value2:
                        program_counter.PC += 1
                        program_counter.valid = 1
                    else:
                        index = find_reorder_buffer_entry(reorder_buffer, fu[0].dest_tag)
                        offset = reorder_buffer[index].dest_tag
                        program_counter.PC = int(program_counter.PC + 1 + offset / 4)
                        program_counter.valid = 1
                else:
                    pass
                # remove from fu
                fu.popleft()


# function: ld_sd_execution
def ld_sd_execution(ld_sd_exes, time_ld_sd_exe, ld_sd_queue, reorder_buffer, cycle):
    for ld_sd_exe in ld_sd_exes:
        if ld_sd_exe.busy == 1:
            # write down starting cycle
            if ld_sd_exe.cycle == 0:
                element = None
                for element in ld_sd_queue:
                    if element.ld_sd_tag == ld_sd_exe.dest_tag:
                        break
                index = find_reorder_buffer_entry(reorder_buffer, element.dest_tag)
                reorder_buffer[index].exe.append(cycle)
                # execute
                ld_sd_exe.cycle += 1
            # write address back to ld_sd_queue
            if ld_sd_exe.cycle == time_ld_sd_exe:
                address = ld_sd_exe.value1 + ld_sd_exe.value2
                element = None
                for element in ld_sd_queue:
                    if element.ld_sd_tag == ld_sd_exe.dest_tag:
                        element.address = address
                        element.ready = 1
                        break
                # write down finish cycle
                index = find_reorder_buffer_entry(reorder_buffer, element.dest_tag)
                reorder_buffer[index].exe.append(cycle)
                ld_sd_exe.busy = 0


# function: get functional unit
def get_fu_unit(fu_units):
    lengths = [len(fu_unit) for fu_unit in fu_units]
    return lengths.index(min(lengths))


def get_free_ld(ld_sd_exes):
    index = -1
    for i, ld_sd_exe in enumerate(ld_sd_exes):
        if ld_sd_exe.busy == 0:
            index = i
            break
    return index


def exe(fu_int_adders, time_fu_int_adder,
        fu_fp_adders, time_fu_fp_adder,
        fu_fp_multis, time_fu_fp_multi, results_buffer,
        rs_int_adder, rs_fp_adder, rs_fp_multi,
        ld_sd_exes, time_ld_sd_exe, ld_sd_queue,
        cycle, reorder_buffer, program_counter):
    '''execution in fu and ld_sd address calculation'''
    ld_sd_execution(ld_sd_exes, time_ld_sd_exe, ld_sd_queue, reorder_buffer, cycle)
    # functional units
    fu_exe(fu_int_adders, results_buffer, reorder_buffer, time_fu_int_adder, cycle, program_counter)
    fu_exe(fu_fp_adders, results_buffer, reorder_buffer, time_fu_fp_adder, cycle, program_counter)
    fu_exe(fu_fp_multis, results_buffer, reorder_buffer, time_fu_fp_multi, cycle, program_counter)
    '''fetch instructions from rs and ld_sd_queue'''
    # from ld_sd_queue
    # check valid ins in ld_sd_queue
    index = check_valid_ins_in_ldsd(ld_sd_queue, reorder_buffer, cycle)
    # put ins into ld_sd_exe
    ld_index = get_free_ld(ld_sd_exes)
    if (index >= 0) & (ld_index >= 0):
        ld_sd_exe = ld_sd_exes[ld_index]
        ld_sd_exe.busy = 1
        ld_sd_exe.cycle = 0
        ld_sd_exe.value1 = ld_sd_queue[index].reg_value
        ld_sd_exe.value2 = ld_sd_queue[index].immediate
        ld_sd_exe.dest_tag = ld_sd_queue[index].ld_sd_tag
        reorder_buffer_idx = find_reorder_buffer_entry(reorder_buffer, ld_sd_queue[index].dest_tag)
        if reorder_buffer[reorder_buffer_idx].issue[0] < cycle:
            ld_sd_execution(ld_sd_exes, time_ld_sd_exe, ld_sd_queue, reorder_buffer, cycle)
    # from rs
    # int_adder
    # fetch valid instruction
    for _ in range(len(fu_int_adders)):
        index = check_valid_ins_in_rs(rs_int_adder, reorder_buffer, cycle)
        if index >= 0:
            fu_index = get_fu_unit(fu_int_adders)
            fu_int_adder = fu_int_adders[fu_index]
            fu_int_adder.append(fu_entry())
            add_entry_into_fu(fu_int_adder, rs_int_adder[index])
            # check if it's a waiting instruction
            reorder_buffer_idx = find_reorder_buffer_entry(reorder_buffer, rs_int_adder[index].dest_tag)
            if reorder_buffer[reorder_buffer_idx].issue[0] < cycle:
                fu_exe(fu_int_adders, results_buffer, reorder_buffer, time_fu_int_adder, cycle, program_counter)
            # remove ins from rs
            rs_int_adder[index].busy = 0

    # fp_adder
    for _ in range(len(fu_fp_adders)):
        index = check_valid_ins_in_rs(rs_fp_adder, reorder_buffer, cycle)
        if index >= 0:
            fu_index = get_fu_unit(fu_fp_adders)
            fu_fp_adder = fu_fp_adders[fu_index]
            fu_fp_adder.append(fu_entry())
            add_entry_into_fu(fu_fp_adder, rs_fp_adder[index])
            reorder_buffer_idx = find_reorder_buffer_entry(reorder_buffer, rs_fp_adder[index].dest_tag)
            if reorder_buffer[reorder_buffer_idx].issue[0] < cycle:
                fu_exe(fu_fp_adders, results_buffer, reorder_buffer, time_fu_fp_adder, cycle, program_counter)
            # remove ins from rs
            rs_fp_adder[index].busy = 0

    # fp_multi
    for _ in range(len(fu_fp_multis)):
        index = check_valid_ins_in_rs(rs_fp_multi, reorder_buffer, cycle)
        if index >= 0:
            fu_index = get_fu_unit(fu_fp_multis)
            fu_fp_multi = fu_fp_multis[fu_index]
            fu_fp_multi.append(fu_entry())
            add_entry_into_fu(fu_fp_multi, rs_fp_multi[index])
            reorder_buffer_idx = find_reorder_buffer_entry(reorder_buffer, rs_fp_multi[index].dest_tag)
            if reorder_buffer[reorder_buffer_idx].issue[0] < cycle:
                fu_exe(fu_fp_multis, results_buffer, reorder_buffer, time_fu_fp_multi, cycle, program_counter)
                # remove ins from rs
            rs_fp_multi[index].busy = 0
