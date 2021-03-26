# Qing
# 21st May 2017
import sys
from collections import deque
from copy import deepcopy

from commit import commit
from exe import exe
from init import read_instruction, build_rs, ld_sd_exe, ld_sd_mem, cdb, PC
from issue import issue
from mem import mem
from wb import wb
from util import read_config

'''initialize'''
# read instructions into a list 
instructions = read_instruction('code.in')
int_a_config, fp_a_config, fp_m_config, ls_config, number_of_rob, reg_int, reg_fp, memory = read_config("configuration.txt")
'''initialize regs, RAT, memory'''
rat_int = deepcopy(reg_int)
rat_fp = deepcopy(reg_fp)

'''intialize reservation stations'''
size_rs_int_adder = int_a_config.no_of_rs
rs_int_adder = build_rs(size_rs_int_adder)

size_rs_fp_adder = fp_a_config.no_of_rs
rs_fp_adder = build_rs(size_rs_fp_adder)

size_rs_fp_multi = fp_m_config.no_of_rs
rs_fp_multi = build_rs(size_rs_fp_multi)

'''initilize function unit'''
fu_int_adders = []
for _ in range(int_a_config.functional_unit):
    fu_int_adder = deque()
    fu_int_adders.append(fu_int_adder)
time_fu_int_adder = int_a_config.cycles_in_exe

fu_fp_adders = []
for _ in range(fp_a_config.functional_unit):
    fu_fp_adder = deque()
    fu_fp_adders.append(fu_fp_adder)
time_fu_fp_adder = fp_a_config.cycles_in_exe

fu_fp_multis = []
for _ in range(fp_m_config.functional_unit):
    fu_fp_multi = deque()
    fu_fp_multis.append(fu_fp_multi)
time_fu_fp_multi = fp_m_config.cycles_in_exe

'''initialize load/store queue'''
ld_sd_queue = deque()
size_ld_sd_queue = ls_config.no_of_rs

ld_sd_exes = []
for _ in range(ls_config.functional_unit):
    ld_sd_exe_obj = ld_sd_exe()
    ld_sd_exe_obj.busy = 0
    ld_sd_exes.append(ld_sd_exe_obj)
time_ld_sd_exe = ls_config.cycles_in_exe

ld_sd_mems = []
for _ in range(ls_config.functional_unit):
    ld_sd_mem_obj = ld_sd_mem()
    ld_sd_mem_obj.busy = 0
    ld_sd_mems.append(ld_sd_mem_obj)
time_ld_sd_mem = ls_config.cycles_in_mem

'''initialize ROB'''
ROB = deque()
size_ROB = number_of_rob
'''initialize CDB'''
results_buffer = deque()
cdb = cdb()
cdb.valid = 0
"""issue first instruction"""
# instruction pointer 
PC = PC()
PC.PC = 0
PC.valid = 1
cycle = 1

# print title 
item = ''.ljust(20)
item += 'ISSUE'.ljust(10)
item += 'EXE'.ljust(15)
item += 'MEM'.ljust(15)
item += 'WB'.ljust(10)
item += 'COMMIT'.ljust(10)
print(item)

# obtaining the issue_width
# by default, providing the issue-width as 1
if len(sys.argv) == 1:
    issue_width = 1
else:
    # obtain the custom issue-width
    issue_width = int(sys.argv[1])
    # reset to default, if the issue width is not in limit
    if not(1 <= issue_width <= 4):
        issue_width = 1

# main
while (len(ROB) > 0) | (cycle == 1):

    '''COMMIT stage'''
    commit(ROB, reg_int, reg_fp, cycle, instructions, issue_width)

    '''CDB stage'''
    wb(cdb, rat_int, rat_fp,
       rs_int_adder, rs_fp_adder, rs_fp_multi,
       ld_sd_queue, ROB, cycle,
       results_buffer, issue_width)

    '''MEM stage'''
    mem(ld_sd_queue, ld_sd_mems, time_ld_sd_mem, results_buffer, memory, ROB, cycle)

    '''EXE stage'''
    exe(fu_int_adders, time_fu_int_adder,
        fu_fp_adders, time_fu_fp_adder,
        fu_fp_multis, time_fu_fp_multi, results_buffer,
        rs_int_adder, rs_fp_adder, rs_fp_multi,
        ld_sd_exes, time_ld_sd_exe, ld_sd_queue,
        cycle, ROB, PC)

    '''ISSUE stage'''
    if (PC.PC < len(instructions)) & (PC.valid == 1):
        issue(cycle, PC, instructions, ROB, size_ROB,
              rs_int_adder,
              rs_fp_adder,
              rs_fp_multi,
              ld_sd_queue, size_ld_sd_queue,
              rat_int, rat_fp, issue_width)

    # cycle number
    cycle += 1
