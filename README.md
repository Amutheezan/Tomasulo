# Tomasulo Algorithm Simulation

## INTRODUCTION 📖

Tomasulo’s algorithm is used for the dynamic scheduling of instructions that allows out-of-order execution and enables more efficient use of multiple execution units. It was developed by Robert Tomasulo at IBM in 1967 and was first implemented in the IBM System/360 Model 91’s floating-point unit. The major innovations of Tomasulo’s algorithm include register renaming in hardware, reservation stations for all execution units, and a common data bus (CDB) on which computed values broadcast to all reservation stations that may need them. These developments allow for improved parallel execution of instructions that would otherwise stall under the use of scoreboards or other earlier algorithms.

## EXECUTION ▶️

Steps of running the code:

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

In each folder ```memory_np``` and ```memory_p``` following structure can be found.

## TEST CASES 🧪

sample test cases and results can be found under the folder test_cases, these results are also included in the report.
Structure of each test_case folder (i.e. ```test_case_0x```, ```x = 1, 2```)
```code.in``` - text file containing instructions
```configuration.txt``` - configuration of the architecture
```result_x.txt``` - scheduling based on Tomasulo algorithm for the issue width ```x```, where ```x = 1, 2, 3, 4```.

## READING CONFIGURATION ☑️

I have implemented the reading ```configuration.txt``` file using ```read_config``` in ```util.py```.
So, we can simply change  ```configuration.txt``` and run the program, without altering any python files.

## LIMITATION 🔼

Doesn't support Branch Prediction.
