from collections import namedtuple

'''define data types'''


# reservation station
def rs_entry():
    return namedtuple('rs_entry',
                          'busy, op, counter, tag_1st, value_1st, valid_1st, tag_2nd, value_2nd, valid_2nd, dest_tag')


# functional unit 
def fu_entry():
    return namedtuple('fu_entry', 'cycle, op, value1, value2, dest_tag, counter')


# function result
def fu_result():
    return namedtuple('fu_result', 'value, dest_tag')


# ld/sd entry
def ld_sd_entry():
    return namedtuple('ld_sd_entry',
                      'ld_sd_tag, ready, op, address, data, dest_tag, immediate, reg_tag, reg_value, valid, counter')


# ld/sd exe
def ld_sd_exe():
    return namedtuple('ld_sd_exe', 'busy, cycle, value1, value2, dest_tag')


# ld/sd mem
def ld_sd_mem():
    return namedtuple('ld_sd_mem', 'busy, cycle, op, data, address, dest_tag')


# cdb
def cdb():
    return namedtuple('cdb', 'valid, value, dest_tag')


# reorder_buffer_entry
def reorder_buffer_entry():
    rob_entry = namedtuple('reorder_buffer_entry',
                           'reorder_buffer_tag, counter, value, op, tag_1st, tag_2nd, reg_tag,'
                           ' immediate, dest_tag, issue, exe, mem, cdb, commit')
    temp = rob_entry
    temp.issue = []
    temp.exe = []
    temp.mem = []
    temp.cdb = []
    temp.commit = []
    return temp


# program_counter
def program_counter():
    return namedtuple('program_counter', 'counter, valid')


# function: read instructions
def read_instruction(codefile):
    with open(codefile) as f:
        instructions = f.read().splitlines()
    return instructions


# function: build rs
def build_rs(num):
    rs = []
    for _ in range(num):
        temp = rs_entry()
        temp.busy = 0
        rs.extend([temp])
    return rs
