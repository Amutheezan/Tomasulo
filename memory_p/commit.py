'''
1. commit ROB_buffer
2. fetch header into ROB_buffer
'''


# function: print reorder_buffer entry
def print_reorder_buffer(entry, instructions):
    item = instructions[entry.counter].ljust(20)
    item += str(entry.issue).ljust(10)
    item += str(entry.exe).ljust(15)
    item += str(entry.mem).ljust(15)
    item += str(entry.cdb).ljust(10)
    item += str(entry.commit)
    print(item)


# function: modify architectual reg
def modify_arch_reg(entry, reg_int, reg_fp):
    if entry.dest_tag[0] == 'F':
        reg_fp[int(entry.dest_tag[1:])] = entry.value
    elif entry.dest_tag[0] == 'R':
        reg_int[int(entry.dest_tag[1:])] = entry.value
    else:
        pass


# function: commit
def commit(reorder_buffer, reg_int, reg_fp, cycle, instructions, issue_width):
    for i in range(issue_width):
        if len(reorder_buffer) > 0:
            if instructions[reorder_buffer[0].counter].split(' ')[0] == 'Bne':
                if len(reorder_buffer[0].exe) != 0:
                    entry = reorder_buffer.popleft()
                    print_reorder_buffer(entry, instructions)
            if (len(reorder_buffer) > 0) & (instructions[reorder_buffer[0].counter].split(' ')[0] != 'Bne'):
                if len(reorder_buffer[0].cdb) != 0:  # broadcasted instructions
                    reorder_buffer[0].commit.append(cycle)
                    entry = reorder_buffer.popleft()
                    modify_arch_reg(entry, reg_int, reg_fp)
                    print_reorder_buffer(entry, instructions)
                elif len(reorder_buffer[0].commit) != 0:  # Sd
                    entry = reorder_buffer.popleft()
                    print_reorder_buffer(entry, instructions)
                    if len(reorder_buffer) > 0:
                        if len(reorder_buffer[0].cdb) != 0:  # broadcasted instructions
                            reorder_buffer[0].commit.append(cycle)
                            entry = reorder_buffer.popleft()
                            modify_arch_reg(entry, reg_int, reg_fp)
                            print_reorder_buffer(entry, instructions)
                else:
                    pass
