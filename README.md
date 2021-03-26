# Tomasulo Algorithm Simulation

## EXECUTION

Steps of run the code:

For memory unit without pipeline

```bash
cd memory_np
python main.py
```

For memory unit with pipeline

```bash
cd memory_p
python main.py
```

## TEST CASES

sample test cases and results can be found under the folder test_cases, these results are also included in the report.
Structure of each test_case folder (i.e. test_case_0x, x = 1, 2)
code.in - text file containing instructions
configuration.txt - configuration of the architcture
result_x.txt - scheduling based on tomasulo algorithm for the issue width x, where x = 1, 2, 3, 4.

## READING CONFIGURATION

I have implemented reading ''configuration.txt'' file using ''read_config'' in util.py.
So, we can simply change ''configuration.txt'' and run the program, without altering any python files.
