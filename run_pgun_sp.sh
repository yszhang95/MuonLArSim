python convert.py --no_eventid_as_runid build/pgun_muplus_3gev_nt_MuonSteps.csv pgun_muplus_3gev.hdf5
python convert.py --no_eventid_as_runid build/pgun_positron_3gev_nt_MuonSteps.csv pgun_positron_3gev.hdf5

python dump_to_bee.py pgun_muplus_3gev.hdf5 pgun_muplus_3gev_json
python dump_to_bee.py pgun_positron_3gev.hdf5 pgun_positron_3gev_json
