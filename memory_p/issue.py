"""
1. put 1 instruction in reorder_buffer
2. put this instruction in RS/ld_sd_queue
3. update RAT
"""
from init import ld_sd_entry, reorder_buffer_entry


# function: find a tag for ld_sd_entry
def find_tag_new_ldsd_entry(ld_sd_queue, size_ld_sd_queue):
    existing_tag = []
    tag_pool = []
    for i in range(len(ld_sd_queue)):
        existing_tag.append(ld_sd_queue[i].ld_sd_tag)
    for i in range(size_ld_sd_queue):
        tag_pool.append('ldsd' + str(i))
    return list(set(tag_pool) - set(existing_tag))[0]


# function put ins into reorder_buffer
def put_ins_into_reorder_buffer(reorder_buffer, size_reorder_buffer, program_counter, cycle, ins, ldsd_tag):
    reorder_buffer.append(reorder_buffer_entry())
    # reorder_buffer_tag
    if len(reorder_buffer) == 1:
        reorder_buffer[-1].reorder_buffer_tag = 'ROB0'
    else:
        index = reorder_buffer[-2].reorder_buffer_tag[3:]
        reorder_buffer[-1].reorder_buffer_tag = 'ROB' + str((int(index) + 1) % size_reorder_buffer)
    # program_counter
    reorder_buffer[-1].counter = program_counter.counter
    # dest_tag
    reorder_buffer[-1].op = ins.split(' ')[0]
    if ins.split(' ')[0] == 'Sd':  # SD
        reorder_buffer[-1].dest_tag = ldsd_tag
    elif ins.split(' ')[0] == 'Bne':  # BNE
        reorder_buffer[-1].dest_tag = int(ins.split(' ')[-1])
    elif ins.split(' ')[0] == 'Ld':
        reorder_buffer[-1].dest_tag = ins.split(' ')[1]
        final_part = ins.split(' ')[2]
        index_r = final_part.index("R")
        reorder_buffer[-1].reg_tag = final_part[index_r:-1]
    elif ins.split(' ')[0] == 'Addi':
        reorder_buffer[-1].dest_tag = ins.split(' ')[1]
        reorder_buffer[-1].tag_1st = ins.split(' ')[2]
        reorder_buffer[-1].immediate = int(ins.split(' ')[3])
    else:  # ALU and LD instructions
        reorder_buffer[-1].dest_tag = ins.split(' ')[1]
        reorder_buffer[-1].tag_1st = ins.split(' ')[2]
        reorder_buffer[-1].tag_2nd = ins.split(' ')[3]

    # issue
    reorder_buffer[-1].issue.append(cycle)


# function: put ins into reservation station
def put_ins_into_rs(station, index, ins, reorder_buffer, rat_int, rat_fp, counter):
    entry = station[index]
    entry.busy = 1
    entry.op = ins.split(' ')[0]
    entry.counter = counter
    # reg 1
    register = ins.split(' ')[2]  # register name
    if register[0] == 'F':
        if type(rat_fp[int(register[1:])]) == str:
            entry.tag_1st = rat_fp[int(register[1:])]
            entry.valid_1st = 0
        else:
            entry.value_1st = rat_fp[int(register[1:])]
            entry.valid_1st = 1
    elif register[0] == 'R':
        if type(rat_int[int(register[1:])]) == str:
            entry.tag_1st = rat_int[int(register[1:])]
            entry.valid_1st = 0
        else:
            entry.value_1st = rat_int[int(register[1:])]
            entry.valid_1st = 1
    else:
        pass
    # reg 2
    register = ins.split(' ')[3]  # register name
    if register[0] == 'F':
        if type(rat_fp[int(register[1:])]) == str:
            entry.tag_2nd = rat_fp[int(register[1:])]
            entry.valid_2nd = 0
        else:
            entry.value_2nd = rat_fp[int(register[1:])]
            entry.valid_2nd = 1
    elif register[0] == 'R':
        if type(rat_int[int(register[1:])]) == str:
            entry.tag_2nd = rat_int[int(register[1:])]
            entry.valid_2nd = 0
        else:
            entry.value_2nd = rat_int[int(register[1:])]
            entry.valid_2nd = 1
    else:  # immediate number
        entry.value_2nd = int(ins.split(' ')[3])
        entry.valid_2nd = 1
    # dest_tag
    entry.dest_tag = reorder_buffer[-1].reorder_buffer_tag


# function: put bne into rs
def put_bne_into_rs(rs_int_adder, index, ins, rat_int, rat_fp, reorder_buffer):
    entry = rs_int_adder[index]
    entry.busy = 1
    entry.op = ins.split(' ')[0]
    # reg 1
    register = ins.split(' ')[1]  # register name
    if register[0] == 'F':
        if (type(rat_fp[int(register[1:])]) == str):
            entry.tag_1st = rat_fp[int(register[1:])]
            entry.valid_1st = 0
        else:
            entry.value_1st = rat_fp[int(register[1:])]
            entry.valid_1st = 1
    elif register[0] == 'R':
        if (type(rat_int[int(register[1:])]) == str):
            entry.tag_1st = rat_int[int(register[1:])]
            entry.valid_1st = 0
        else:
            entry.value_1st = rat_int[int(register[1:])]
            entry.valid_1st = 1
    else:
        pass
    # reg 2
    register = ins.split(' ')[2]  # register name
    if register[0] == 'F':
        if (type(rat_fp[int(register[1:])]) == str):
            entry.tag_2nd = rat_fp[int(register[1:])]
            entry.valid_2nd = 0
        else:
            entry.value_2nd = rat_fp[int(register[1:])]
            entry.valid_2nd = 1
    elif register[0] == 'R':
        if (type(rat_int[int(register[1:])]) == str):
            entry.tag_2nd = rat_int[int(register[1:])]
            entry.valid_2nd = 0
        else:
            entry.value_2nd = rat_int[int(register[1:])]
            entry.valid_2nd = 1
    # dest_tag
    entry.dest_tag = reorder_buffer[-1].reorder_buffer_tag


# function: put ins into ld_sd_queue
def put_ins_into_ldsd(ldsd_tag, ld_sd_queue, ins, reorder_buffer, rat_int, rat_fp, counter):
    ld_sd_queue.append(ld_sd_entry())
    # ld_sd_tag
    ld_sd_queue[-1].ld_sd_tag = ldsd_tag
    ld_sd_queue[-1].ready = 0
    ld_sd_queue[-1].op = ins.split(' ')[0]
    ld_sd_queue[-1].counter = counter
    if ld_sd_queue[-1].op == 'Sd':
        register = ins.split(' ')[1]  # register name
        ld_sd_queue[-1].data = rat_fp[int(register[1:])]

    ld_sd_queue[-1].dest_tag = reorder_buffer[-1].reorder_buffer_tag
    # immediate and reg value 
    ld_sd_queue[-1].immediate = int(ins.split(' ')[-1][:-4])
    register = ins.split(' ')[-1][-3:-1]  # register name
    if (type(rat_int[int(register[1:])]) == str):
        ld_sd_queue[-1].reg_tag = rat_int[int(register[1:])]
        ld_sd_queue[-1].valid = 0
    else:
        ld_sd_queue[-1].reg_value = rat_int[int(register[1:])]
        ld_sd_queue[-1].valid = 1


# function: check space of reservation station
def check_rs_space(station):
    index = -1
    for i in range(len(station)):
        if station[i].busy == 0:
            index = i
            break
    return index


# update RAT
def update_rat(reorder_buffer, rat_int, rat_fp):
    if reorder_buffer[-1].dest_tag[0] == 'F':
        rat_fp[int(reorder_buffer[-1].dest_tag[1:])] = reorder_buffer[-1].reorder_buffer_tag
    elif reorder_buffer[-1].dest_tag[0] == 'R':
        rat_int[int(reorder_buffer[-1].dest_tag[1:])] = reorder_buffer[-1].reorder_buffer_tag
    else:
        pass


def issue(cycle, program_counter, instructions, reorder_buffer, size_of_reorder_buffer,
          rs_int_adder,
          rs_fp_adder,
          rs_fp_multi,
          ld_sd_queue, size_ld_sd_queue,
          rat_int, rat_fp, issue_width):
    # fetch instruction same as issue-width
    for i in range(min(issue_width, len(instructions) - program_counter.counter)):

        ins = instructions[program_counter.counter]
        op = ins.split(' ')[0]
        '''decode'''
        # LD/SD instructions
        if (op == 'Ld') | (op == 'Sd'):
            # check space
            if (len(reorder_buffer) < size_of_reorder_buffer) & (len(ld_sd_queue) < size_ld_sd_queue):
                # find ldsd_tag
                ldsd_tag = find_tag_new_ldsd_entry(ld_sd_queue, size_ld_sd_queue)
                # put ins into reorder_buffer
                put_ins_into_reorder_buffer(reorder_buffer, size_of_reorder_buffer, program_counter, cycle, ins,
                                            ldsd_tag)
                # put ins into ld_sd_queue
                put_ins_into_ldsd(ldsd_tag, ld_sd_queue, ins, reorder_buffer, rat_int, rat_fp, program_counter.counter)
                # update RAT
                update_rat(reorder_buffer, rat_int, rat_fp)
                # program_counter
                program_counter.counter += 1
        # integer adder instructions
        elif (op == 'Add') | (op == 'Addi') | (op == 'Sub'):
            # check space
            if (len(reorder_buffer) < size_of_reorder_buffer) & (check_rs_space(rs_int_adder) >= 0):
                # put ins into reorder_buffer
                put_ins_into_reorder_buffer(reorder_buffer, size_of_reorder_buffer, program_counter, cycle, ins, '')
                # put ins into rs_int_adder
                index = check_rs_space(rs_int_adder)
                put_ins_into_rs(rs_int_adder, index, ins, reorder_buffer, rat_int, rat_fp, program_counter.counter)
                # update RAT
                update_rat(reorder_buffer, rat_int, rat_fp)
                # program_counter
                program_counter.counter += 1
        # fp adder instructions
        elif (op == 'Add.d') | (op == 'Sub.d'):
            # check space
            if (len(reorder_buffer) < size_of_reorder_buffer) & (check_rs_space(rs_fp_adder) >= 0):
                # put ins into reorder_buffer
                put_ins_into_reorder_buffer(reorder_buffer, size_of_reorder_buffer, program_counter, cycle, ins, '')
                # put ins into rs_fp_adder
                index = check_rs_space(rs_fp_adder)
                put_ins_into_rs(rs_fp_adder, index, ins, reorder_buffer, rat_int, rat_fp, program_counter.counter)
                # update RAT
                update_rat(reorder_buffer, rat_int, rat_fp)
                # program_counter
                program_counter.counter += 1
        # fp multiplier instructions
        elif op == 'Mult.d':
            # check space
            if (len(reorder_buffer) < size_of_reorder_buffer) & (check_rs_space(rs_fp_multi) >= 0):
                # put ins into reorder_buffer
                put_ins_into_reorder_buffer(reorder_buffer, size_of_reorder_buffer, program_counter, cycle, ins, '')
                # put ins into rs_fp_multi
                index = check_rs_space(rs_fp_multi)
                put_ins_into_rs(rs_fp_multi, index, ins, reorder_buffer, rat_int, rat_fp, program_counter.counter)
                # update RAT
                update_rat(reorder_buffer, rat_int, rat_fp)
                # program_counter
                program_counter.counter += 1
        # Bne
        elif op == 'Bne':
            # check space
            if (len(reorder_buffer) < size_of_reorder_buffer) & (check_rs_space(rs_int_adder) >= 0):
                # put ins into reorder_buffer
                put_ins_into_reorder_buffer(reorder_buffer, size_of_reorder_buffer, program_counter, cycle, ins, '')
                # put ins into rs_int_adder
                index = check_rs_space(rs_int_adder)
                put_bne_into_rs(rs_int_adder, index, ins, rat_int, rat_fp, reorder_buffer)
                # program_counter
                program_counter.valid = 0
        else:
            pass
