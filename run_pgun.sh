#!/bin/bash

while IFS= read -r InFile; do
    echo "Processing $InFile"
    # python prepare.py "$InFile"
    bname=$(basename "$InFile")
    odir="${bname%.hdf5}"
    if [[ -d $odir ]]; then
        echo "Output directory $odir already exists."
    else
        mkdir "$odir"
    fi
    build/MuonLArSim "${odir}/pgun_mu_3p00GeV.mac"
done < run_list.txt
