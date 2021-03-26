#!/bin/bash

for dir in "memory_np" "memory_p"; do
  cd "$dir" || exit
  for i in 2 1; do
    cp test_cases/test_case_0"$i"/configuration.txt .
    cp test_cases/test_case_0"$i"/code.in .
    for j in 1 2 3 4; do
      python main.py "$j" > test_cases/test_case_0"$i"/result_"$j".txt
    done
  done
  cd ..
done