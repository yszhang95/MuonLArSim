import h5py
import numpy as np

def load_dataset(path, dataset_name):
    """
    Load structured array from an HDF5 file.
    """
    with h5py.File(path, 'r') as f:
        data = f[dataset_name][:]
    return data

def compute_endpoints_and_direction(points):
    """
    Given array of points with fields ['x', 'y', 'z'], find two endpoints along z-axis
    and compute unit direction vector from min_z to max_z.
    """
    lower_z = points[:, 2] < points[:, 5] # False -->0 ,True --> 1
    p_min = np.where(lower_z[:,np.newaxis], points[:,:3], points[:,3:])
    p_max = np.where(~lower_z[:,np.newaxis], points[:,:3], points[:,3:])
    direction = p_max - p_min
    norm = np.linalg.norm(direction, axis=1)
    direction = np.where((norm>0)[:,None], direction/norm[:,None], np.zeros_like(direction))
    return p_min, p_max, direction

# Example usage:
if __name__ == '__main__':
    # Paths and dataset names
    path, name = '/home/yousen/Documents/NDLAr2x2/2x2_ql/filter_mc_events/check_selection/selected_data_small_angle/packet-0050015-2024_07_08_13_37_49_CDT.FLOW_selected.hdf5', 'picked/points'

    # Load data
    points = load_dataset(path, name)
    pts_min, pts_max, directions = compute_endpoints_and_direction(points)

    # Transform each group2 to corresponding group1 by position

    energy = 3

    cmd = "/run/initialize"
    for pt_min, pt_max, direction in zip(pts_min, pts_max, directions):
        # print(pt_min, pt_max, direction)
        macro = f"""
# Configure particle
/gun/particle mu-
/gun/energy {energy} GeV
/gun/position {pt_min[0]} {pt_min[1]} {pt_min[2]} cm
/gun/direction {direction[0]} {direction[1]} {direction[2]}

/run/beamOn 1
"""
        cmd += macro
    estr = "{:.2f}".format(energy).replace(".", "p")
    with open(f"pgun_mu_{estr}GeV.mac", "w") as f:
        f.write(cmd)
