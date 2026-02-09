import h5py
import numpy as np
import sys
import os

def load_dataset(path, dataset_name):
    """
    Load structured array from an HDF5 file.
    """
    with h5py.File(path, 'r') as f:
        data = f[dataset_name][:]
    return data


def compute_endpoints_and_direction(points):
    """
    Given array of points with fields ['x', 'y', 'z'], find two endpoints along
    z-axis and compute unit direction vector from min_z to max_z.
    """
    lower_z = points[:, 2] < points[:, 5]  # False -->0 ,True --> 1
    p_min = np.where(lower_z[:, np.newaxis], points[:, :3], points[:, 3:])
    p_max = np.where(~lower_z[:, np.newaxis], points[:, :3], points[:, 3:])
    direction = p_max - p_min
    norm = np.linalg.norm(direction, axis=1)
    direction = np.where((norm > 0)[:, None], direction / norm[:, None],
                         np.zeros_like(direction))
    return p_min, p_max, direction


# Example usage:
if __name__ == '__main__':
    # Paths and dataset names
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if path is None:
        print("Please provide the HDF5 file path as a command line argument.")
        sys.exit(1)
    name = sys.argv[2] if len(sys.argv) > 2 else "picked/points/data"
    # odir = sys.argv[3] if len(sys.argv) > 3 else "."
    odir = os.path.basename(path)
    odir = os.path.splitext(odir)[0]
    os.makedirs(odir, exist_ok=True)

    # Load data
    points = load_dataset(path, name)
    event_ids = load_dataset(path, "picked/event_id/data")
    io_group = load_dataset(path, "picked/io_group/data")
    eids = event_ids*10 + io_group
    pts_min, pts_max, directions = compute_endpoints_and_direction(points)

    # Transform each group2 to corresponding group1 by position

    energy = 3
    estr = "{:.2f}".format(energy).replace(".", "p")

    cmd = "/run/initialize"
    for pt_min, pt_max, direction, event_id in \
            zip(pts_min, pts_max, directions, eids):
        # print(pt_min, pt_max, direction)
        macro = f"""
# Configure particle
/gun/particle mu-
/gun/energy {energy} GeV
/gun/position {pt_min[0]} {pt_min[1]} {pt_min[2]} cm
/gun/direction {direction[0]} {direction[1]} {direction[2]}

/analysis/setFileName {odir}/run_{event_id}_mu_{estr}GeV
/run/beamOn 30
"""
        cmd += macro
    with open(os.path.join(odir, f"pgun_mu_{estr}GeV.mac"), "w") as f:
        f.write(cmd)
