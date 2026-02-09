#!/bin/bash

while IFS= read -r InFile; do
    echo "Processing $InFile"
    python prepare.py "$InFile"
done < run_list.txt
