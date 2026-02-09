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
    python convert_pgun.py \
           --hdf5_source ${InFile} \
        ${odir}/mu_3p00GeV_nt_MuonSteps.csv \
        ${odir}/pgun_mu_3GeV_2mm.hdf5
done < run_list.txt
