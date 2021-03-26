from collections import namedtuple

IntAdderConfig = namedtuple("IntAdderConfig", ["no_of_rs", "cycles_in_exe", "functional_unit"])
FpAdderConfig = namedtuple("FpAdderConfig", ["no_of_rs", "cycles_in_exe", "functional_unit"])
FpMulConfig = namedtuple("FpMulConfig", ["no_of_rs", "cycles_in_exe", "functional_unit"])
LdSdConfig = namedtuple("LdSdConfig", ["no_of_rs", "cycles_in_exe", "cycles_in_mem", "functional_unit"])


def read_config(file_name):
    config_file = open(file_name, "r+")
    # skip header
    config_file.readline()

    # fetch functional unit, rs and other configurations
    int_adder_details = config_file.readline()
    fp_adder_details = config_file.readline()
    fp_multiplier_details = config_file.readline()
    load_store_details = config_file.readline()
    int_adder_items = ' '.join(int_adder_details.split()).split(' ')
    fp_adder_items = ' '.join(fp_adder_details.split()).split(' ')
    fp_multiplier_items = ' '.join(fp_multiplier_details.split()).split(' ')
    ls_items = ' '.join(load_store_details.split()).split(' ')
    int_a_config = IntAdderConfig(int(int_adder_items[-3]), int(int_adder_items[-2]),
                                  int(int_adder_items[-1]))
    fp_a_config = FpAdderConfig(int(fp_adder_items[-3]), int(fp_adder_items[-2]), int(fp_adder_items[-1]))
    fp_m_config = FpMulConfig(int(fp_multiplier_items[-3]), int(fp_multiplier_items[-2]),
                              int(fp_multiplier_items[-1]))
    ls_config = LdSdConfig(int(ls_items[-4]), int(ls_items[-3]), int(ls_items[-2]), int(ls_items[-1]))

    config_file.readline()
    rob_line = config_file.readline()[:-1]
    number_of_rob = int(rob_line.split(" = ")[1])
    register_file_lines = config_file.readline()[:-1]

    # integer REG
    reg_int = [0 for _ in range(32)]

    # fp REG
    reg_fp = [0.0 for _ in range(32)]

    entries = register_file_lines.split(", ")
    for entry in entries:
        if entry.startswith("R"):
            idx, value = entry[1:].split("=")
            reg_int[int(idx)] = int(value)
        elif entry.startswith("F"):
            idx, value = entry[1:].split("=")
            reg_fp[int(idx)] = float(value)

    # memory
    memory = [0.0 for _ in range(256)]
    memory_line = config_file.readline()[:-1]
    memory_values = memory_line.split(", ")
    for memory_val in memory_values:
        memory_val = memory_val.replace("Mem", "")
        idx, value = memory_val.split("=")
        memory[int(idx[1:-1])] = float(value)

    return int_a_config, fp_a_config, fp_m_config, ls_config, number_of_rob, reg_int, reg_fp, memory
