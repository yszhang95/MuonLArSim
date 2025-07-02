import h5py
import numpy as np

def load_dataset(path, dataset_name):
    """
    Load structured array from an HDF5 file.
    """
    with h5py.File(path, 'r') as f:
        data = f[dataset_name][:]
    return data

def group_by_event(data):
    """
    Group structured array by 'event_id'.
    Returns a list of subarrays, in sorted order of event_id.
    """
    ids = np.unique(data['event_id'])
    groups = [data[data['event_id'] == eid] for eid in ids]
    return groups

def filter_points_by_z_range(points, z_min=2.462, z_max=64.538):
    """
    Filter structured array so that both z_start and z_end lie within
    either [z_min, z_max] or [-z_max, -z_min].
    Returns a boolean mask of valid rows.
    """
    z_start = points['z_start']
    z_end = points['z_end']
    # Check positive range
    pos_mask = (z_start >= z_min) & (z_start <= z_max) & \
               (z_end   >= z_min) & (z_end   <= z_max)
    # Check negative range
    neg_mask = (z_start <= -z_min) & (z_start >= -z_max) & \
               (z_end   <= -z_min) & (z_end   >= -z_max)
    return pos_mask | neg_mask

def compute_endpoints_and_direction(points):
    """
    Given array of points with fields ['x', 'y', 'z'], find two endpoints along z-axis
    and compute unit direction vector from min_z to max_z.
    """
    coords = np.vstack((points['x'], points['y'], points['z'])).T
    min_idx = np.argmin(coords[:, 2])
    max_idx = np.argmax(coords[:, 2])
    p_min = coords[min_idx]
    p_max = coords[max_idx]
    direction = p_max - p_min
    norm = np.linalg.norm(direction)
    if norm > 0:
        direction /= norm
    return p_min, p_max, direction

def rotation_matrix_from_vectors(v1, v2):
    """
    Compute rotation matrix that aligns v1 to v2.
    """
    a = v1 / np.linalg.norm(v1)
    b = v2 / np.linalg.norm(v2)
    v = np.cross(a, b)
    c = np.dot(a, b)
    if np.allclose(v, 0) and c > 0.9999:
        return np.eye(3)
    vx = np.array([[    0, -v[2],  v[1]],
                   [ v[2],     0, -v[0]],
                   [-v[1],  v[0],    0]])
    R = np.eye(3) + vx + vx.dot(vx) * ((1 - c) / (np.linalg.norm(v)**2))
    return R

def transform_group2_to_group1(group1_points, group2_points):
    """
    Align group2 start points to group1 endpoints and directions.
    """
    # group1 endpoints and direction
    p1_min, _, dir1 = compute_endpoints_and_direction(group1_points)

    # Extract start and end coords from group2
    start_coords = np.vstack((group2_points['x_start'],
                               group2_points['y_start'],
                               group2_points['z_start'])).T
    end_coords = np.vstack((group2_points['x_end'],
                             group2_points['y_end'],
                             group2_points['z_end'])).T

    # Identify group2's orientation from start points
    min_idx_start = np.argmin(start_coords[:, 2])
    max_idx_start = np.argmax(start_coords[:, 2])
    p2_min_start = start_coords[min_idx_start]
    p2_max_start = start_coords[max_idx_start]
    dir2 = p2_max_start - p2_min_start
    dir2 /= (np.linalg.norm(dir2) + 1e-8)

    # Identify separate origin for end points
    min_idx_end = np.argmin(end_coords[:, 2])
    p2_min_end = end_coords[min_idx_end]

    # Compute rotation matrix once
    R = rotation_matrix_from_vectors(dir2, dir1)

    # Apply translation+rotation to start coords using p2_min_start
    aligned_start = (start_coords - p2_min_start).dot(R.T) + p1_min
    # Apply translation+rotation to end coords using p2_min_end
    aligned_end = (end_coords - p2_min_start).dot(R.T) + p1_min

    # Update structured fields in-place
    group2_points['x_start'] = aligned_start[:, 0]
    group2_points['y_start'] = aligned_start[:, 1]
    group2_points['z_start'] = aligned_start[:, 2]
    group2_points['x_end']   = aligned_end[:,   0]
    group2_points['y_end']   = aligned_end[:,   1]
    group2_points['z_end']   = aligned_end[:,   2]
    group2_points['x'] = (group2_points['x_start'] + group2_points['x_end'])/2.
    group2_points['y'] = (group2_points['y_start'] + group2_points['y_end'])/2.
    group2_points['z'] = (group2_points['z_start'] + group2_points['z_end'])/2.

    min_idx2_new = np.argmin(aligned_start[:, 2])
    max_idx2_new = np.argmax(aligned_start[:, 2])
    p2_min_new = aligned_start[min_idx2_new]
    p2_max_new = aligned_start[max_idx2_new]
    dir2_new = p2_max_new - p2_min_new
    dir2_new /= (np.linalg.norm(dir2_new) + 1e-8)

    print(p1_min, p2_min_start, p2_min_new, dir1, dir2, dir2_new)
    assert np.all(np.abs(group2_points['x_start'][1:] - group2_points['x_end'][:-1])<1E-5),  'next start, previous end, not close enough in x'
    assert np.all(np.abs(group2_points['y_start'][1:] - group2_points['y_end'][:-1])<1E-5),  'next start, previous end, not close enough in y'
    assert np.all(np.abs(group2_points['z_start'][1:] - group2_points['z_end'][:-1])<1E-5),  'next start, previous end, not close enough in z'

    return group2_points

# Example usage:
if __name__ == '__main__':
    # Paths and dataset names
    path1, name1 = '/home/yousen/Public/ndlar_shared/data/data_reflowv5_20250510/packet-0050015-2024_07_08_13_37_49_CDT.FLOW_selected.hdf5', 'selected/hits/data'
    path2, name2 = '/home/yousen/Public/ndlar_shared/data/tred_particle_gun_20250625/particle_gun_mu_only.hdf5', 'segments'

    # Load data
    data1 = load_dataset(path1, name1)
    data2 = load_dataset(path2, name2)

    # Group by event_id into lists (order by sorted event_id)
    groups1 = group_by_event(data1)
    groups2 = group_by_event(data2)

    # Transform each group2 to corresponding group1 by position
    transformed_groups2 = []
    for pts1, pts2 in zip(groups1, groups2):
        aligned = transform_group2_to_group1(pts1, pts2)
        m = filter_points_by_z_range(aligned)
        aligned = aligned[m]
        transformed_groups2.append(aligned)
        # print(np.max(aligned['z_start']), np.max(aligned['z_end']))

    with h5py.File("pgun_mu_only_transformed.hdf5", "w") as f:
        f.create_dataset('segments', data=np.concatenate(transformed_groups2))

    # transformed_groups2 now contains arrays of aligned start points for each paired event
    # Further processing or saving can follow here.

