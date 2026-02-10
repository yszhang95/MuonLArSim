#!/usr/bin/env python3

import numpy as np
import h5py
import argparse
import os
import re


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


def filter_file_list(infiles: list[str], pattern: str) -> list[str]:
    """Filter input file list to only include existing files.

    Args:
        infiles (list[str]): List of input file paths.
        pattern (str): Regular expression pattern that file names must match, with one capturing group for event_id.

    Returns:
        list[str]: Filtered list of existing file paths.
    """
    filtered_files = []
    pattern = re.compile(pattern)
    for f in infiles:
        if not pattern.fullmatch(os.path.basename(f)):
            raise ValueError(f"Warning: File {f} does not match the expected pattern {str(pattern)}.")
        if not os.path.isfile(f):
            raise FileNotFoundError(f"Warning: File {f} does not exist.")
        filtered_files.append((f, int(pattern.fullmatch(os.path.basename(f)).group(1))))
    return filtered_files


def main():
    parser = argparse.ArgumentParser(description="Merge multiple HDF5 files into a single file.")
    parser.add_argument('-n', help='stride for event_id; event_id_new = event_id_track * n + event_id_g4', type=int, default=100)
    parser.add_argument('--pat', help='Regular expression pattern that file names must match, with one capturing group for event_id. Default: "^.*_event_id__(\\d+).*\\.hdf5$"', type=str, default="^.*_event_id__(\\d+).*\\.hdf5$")
    parser.add_argument('output_file', help='Path to the output merged HDF5 file.')
    parser.add_argument('input_files', nargs='+', help='List of input HDF5 files to merge.')
    args = parser.parse_args()
    pattern = "^.*_event_id__(\\d+).*\\.hdf5$"
    filtered_files = files = filter_file_list(args.input_files, args.pat)
    df = np.array([], dtype=segment_dtype)
    for f in filtered_files:
        print(f"Processing file: {f[0]} with event_id {f[1]}")
        with h5py.File(f[0], 'r') as h5f:
            if 'segments' not in h5f:
                raise KeyError(f"Warning: File {f} does not contain 'segments' dataset.")
            data = h5f['segments'][:]
            data['event_id'] = f[1] * args.n + data['event_id']
            df = np.concatenate((df, data), axis=0)
    with h5py.File(args.output_file, 'w') as f:
        f.create_dataset('segments', data=df)


if __name__ == '__main__':
    main()
