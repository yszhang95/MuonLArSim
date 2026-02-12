#!/bin/bash

# edit 20250730
# xoffset 1.0
python convert.py --hdf5_source /home/yousen/Public/ndlar_shared/data_reflowv5_20250722/packet-0050015-2024_07_08_13_37_49_CDT.FLOW_selected.hdf5 \
       --eventid_as_runid --xoffset 1.0 \
       build/mu_3p00GeV_nt_MuonSteps.csv \
       build/pgun_mu_3GeV_2mm_xoffset_1p0cm.hdf5

# xoffset 2.0
python convert.py --hdf5_source /home/yousen/Public/ndlar_shared/data_reflowv5_20250722/packet-0050015-2024_07_08_13_37_49_CDT.FLOW_selected.hdf5 \
       --eventid_as_runid --xoffset 2.0 \
       build/mu_3p00GeV_nt_MuonSteps.csv \
       build/pgun_mu_3GeV_2mm_xoffset_2p0cm.hdf5

# xoffset 0.5
python convert.py --hdf5_source /home/yousen/Public/ndlar_shared/data_reflowv5_20250722/packet-0050015-2024_07_08_13_37_49_CDT.FLOW_selected.hdf5 \
       --eventid_as_runid --xoffset 0.5 \
       build/mu_3p00GeV_nt_MuonSteps.csv \
       build/pgun_mu_3GeV_2mm_xoffset_0p5cm.hdf5
