import pandas as pd
import numpy as np
import h5py

# Define the structured dtype
segment_dtype = np.dtype([
    # 8-byte float64
    ('t0_start',     np.float64),  # 8 bytes
    ('t0_end',       np.float64),
    ('t0',           np.float64),
    ('t_start',      np.float64),
    ('t_end',        np.float64),
    ('t',            np.float64),

    # 8-byte uint64
    ('vertex_id',    np.uint64),

    # 4-byte uint32 / int32
    ('event_id',     np.uint32),
    ('segment_id',   np.uint32),
    ('traj_id',      np.uint32),
    ('file_traj_id', np.uint32),
    ('n_electrons',  np.uint32),
    ('pdg_id',       np.int32),
    ('pixel_plane',  np.int32),

    # 4-byte float32
    ('x_end',        np.float32),
    ('y_end',        np.float32),
    ('z_end',        np.float32),
    ('x_start',      np.float32),
    ('y_start',      np.float32),
    ('z_start',      np.float32),
    ('dx',           np.float32),
    ('tran_diff',    np.float32),
    ('long_diff',    np.float32),
    ('dEdx',         np.float32),
    ('dE',           np.float32),
    ('n_photons',    np.float32),
    ('x',            np.float32),
    ('y',            np.float32),
    ('z',            np.float32),
], align=True)

def convert_csv_to_hdf5(csv_file, hdf5_file):
    df = pd.read_csv(csv_file)

    # Filter for muons (|PDG_ID| == 13)
    df = df[df['PDG_ID'].abs() == 13].copy()

    # Calculated fields
    df['vertex_id'] = df['EventID'] + 1000
    df['segment_id'] = df['StepID']
    df['traj_id'] = df['TrackID']
    df['file_traj_id'] = df['traj_id']
    df['t0_start'] = df['t0_start(us)'] + df['EventID'] * 1.2e6
    df['t0_end'] = df['t0_end(us)'] + df['EventID'] * 1.2e6
    df['t0'] = (df['t0_start'] + df['t0_end']) / 2.0
    df['x'] = (df['x_start(cm)'] + df['x_end(cm)']) / 2.0
    df['y'] = (df['y_start(cm)'] + df['y_end(cm)']) / 2.0
    df['z'] = (df['z_start(cm)'] + df['z_end(cm)']) / 2.0
    df['dx'] = df['StepLength(cm)']
    df['dE'] = df['Edep(MeV)']
    df['dEdx'] = df['dE'] / df['dx']

    # Add preallocated zeros
    df['tran_diff'] = 0.0
    df['long_diff'] = 0.0
    df['n_electrons'] = 0
    df['n_photons'] = 0.0
    df['pixel_plane'] = 0
    df['t'] = 0.0
    df['t_start'] = 0.0
    df['t_end'] = 0.0

    # Map to structured array
    data = np.zeros(len(df), dtype=segment_dtype)
    data['event_id']     = df['EventID'].astype(np.uint32)
    data['segment_id']   = df['segment_id'].astype(np.uint32)
    data['vertex_id']    = df['vertex_id'].astype(np.uint64)
    data['traj_id']      = df['traj_id'].astype(np.uint32)
    data['file_traj_id'] = df['file_traj_id'].astype(np.uint32)
    data['n_electrons']  = df['n_electrons'].astype(np.uint32)
    data['pdg_id']       = df['PDG_ID'].astype(np.int32)
    data['pixel_plane']  = df['pixel_plane'].astype(np.int32)
    data['x_end']        = df['x_end(cm)'].astype(np.float32)
    data['y_end']        = df['y_end(cm)'].astype(np.float32)
    data['z_end']        = df['z_end(cm)'].astype(np.float32)
    data['x_start']      = df['x_start(cm)'].astype(np.float32)
    data['y_start']      = df['y_start(cm)'].astype(np.float32)
    data['z_start']      = df['z_start(cm)'].astype(np.float32)
    data['dx']           = df['dx'].astype(np.float32)
    data['tran_diff']    = df['tran_diff'].astype(np.float32)
    data['long_diff']    = df['long_diff'].astype(np.float32)
    data['dEdx']         = df['dEdx'].astype(np.float32)
    data['dE']           = df['dE'].astype(np.float32)
    data['n_photons']    = df['n_photons'].astype(np.float32)
    data['x']            = df['x'].astype(np.float32)
    data['y']            = df['y'].astype(np.float32)
    data['z']            = df['z'].astype(np.float32)
    data['t0_start']     = df['t0_start'].astype(np.float64)
    data['t0_end']       = df['t0_end'].astype(np.float64)
    data['t0']           = df['t0'].astype(np.float64)
    data['t_start']      = df['t_start'].astype(np.float64)
    data['t_end']        = df['t_end'].astype(np.float64)
    data['t']            = df['t'].astype(np.float64)

    # Write to HDF5
    with h5py.File(hdf5_file, 'w') as f:
        f.create_dataset('segments', data=data)

# Example usage:
convert_csv_to_hdf5('muon_steps.csv', 'particle_gun_mu_only.hdf5')
