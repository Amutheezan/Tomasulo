# Tomasulo Algorithm Simulation

[EXECUTION]
Steps of run the code:
python main.py

[CONFIGURING ISSUE WIDTH]
by default the issue_width is set to the value ''4''.
we can change the issue_width by editing the the main.py at line 78 (which can change parameter value for the variable ''issue_width'').

[TEST CASES]
sample test cases and results can be found under the folder test_cases, these results are also included in the report.
Structure of each test_case folder (i.e. test_case_0x, x = 1, 2)
code.in - text file containing instructions
configuration.txt - configuration of the architcture
result_x.txt - scheduling based on tomasulo algorithm for the issue width x, where x = 1, 2, 3, 4.

[READING CONFIGURATION]
I have implemented reading ''configuration.txt'' file using ''read_config'' in util.py.
So, we can simply change ''configuration.txt'' and run the program, without altering any python files.