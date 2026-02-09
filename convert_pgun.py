import pandas as pd
import numpy as np
import h5py
import argparse
import os

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

# hard coded TPC borders and directions
tpc_borders = [
  [3.069, 33.34125, -62.076, 62.076, 2.462, 64.538],
  [33.65875, 63.931, -62.076, 62.076, 2.462, 64.538],
  [3.069, 33.34125, -62.076, 62.076, -64.538, -2.462],
  [33.65875, 63.931, -62.076, 62.076, -64.538, -2.462],
  [-63.931, -33.65875, -62.076, 62.076, 2.462, 64.538],
  [-33.34125, -3.069, -62.076, 62.076, 2.462, 64.538],
  [-63.931, -33.65875, -62.076, 62.076, -64.538, -2.462],
  [-33.34125, -3.069, -62.076, 62.076, -64.538, -2.462]
] # xmin, max, ymin, ymax, zmin, zmax
tpc_direction = [-1, 1, -1, 1, -1, 1, -1, 1]


def is_row_all_strings(row):
    return all(isinstance(x, str) and not x.strip().isdigit() for x in row)


def convert_csv_to_hdf5(csv_file, **kwargs):
    first_row = pd.read_csv(csv_file, nrows=1, comment='#', names=None)\
                  .iloc[0].tolist()

    if is_row_all_strings(first_row):
        df = pd.read_csv(csv_file, comment='#')
    else:
        names = ['EventID', 'TrackID', 'StepID',
                 'x_start(cm)', 'y_start(cm)', 'z_start(cm)', 't0_start(us)',
                 'x_end(cm)', 'y_end(cm)', 'z_end(cm)', 't0_end(us)',
                 'Edep(MeV)', 'KineticE(MeV)', 'StepLength(cm)',
                 'PDG_ID', 'ParentID', 'ProcessName']
        df = pd.read_csv(csv_file, comment='#', names=names)

    # Filter for muons and electrons
    df = df[(df['PDG_ID'].abs() == 13) | (df['PDG_ID'].abs() == 11)].copy()


    direction = np.zeros(len(df), dtype=np.int8)
    x = (df['x_start(cm)'] + df['x_end(cm)']) / 2.
    tol = 1E-4
    for i, border in enumerate(tpc_borders):
        # Check which segments are within this border range
        mask = (x >= border[0]-tol) & (x <= border[1]+tol) # tolerance
        direction[mask] = tpc_direction[i]
    if np.any(direction == 0):
        raise ValueError("Some segments are not within TPC borders. "
                         "Check the x_start and x_end values.")

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

    return data


def main():
    parser = argparse.ArgumentParser(description="Process data from csv.")
    parser.add_argument("csv_file", help="Path to the CSV file.")
    parser.add_argument("h5out", help="Path to the output HDF5 file (required).")
    parser.add_argument("--hdf5_source", required=False,
                        help="Path to the source HDF5 file (optional).")

    args = parser.parse_args()
    fh5 = args.h5out
    csv = args.csv_file


    if args.hdf5_source:
        try:
            fin = h5py.File(args.hdf5_source)
            event_ids = fin['/picked/event_id/data'][:]
            io_group = fin['/picked/io_group/data'][:]
            event_ids = event_ids*10 + io_group
        except FileNotFoundError:
            print(f"Error: HDF5 file not found at {args.hdf5_file}")
            return
    else:
        raise NotImplementedError("Please provide a source HDF5 file ")

    data = []
    for i in event_ids:
        csvin = os.path.join(os.path.dirname(csv),
                             "run_" + str(i) + "_"
                             + os.path.basename(csv))
        # print("Processing file:", csvin, fh5out, "for event_id", i)
        ds = convert_csv_to_hdf5(csvin)
        mult = np.power(10, np.ceil(np.log10(np.max(ds["event_id"]))))
        # print(f"Multiple is {mult}")
        ds["event_id"] = int(mult) * i + ds["event_id"]
        if ds is not None and len(ds) > 0:
            data.append(ds)
        else:
            raise ValueError(f"No data found for event_id {i} in file {csvin}")
    data = np.concatenate(data, axis=0)
    # Write to HDF5
    with h5py.File(fh5, 'w') as f:
        f.create_dataset('segments', data=data)


if __name__ == "__main__":
    main()
