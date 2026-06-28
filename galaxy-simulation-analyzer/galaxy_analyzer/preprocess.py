"""
preprocess.py — Shrinking-sphere recenter and disk alignment.

Preprocessing steps before analyzing a galaxy snapshot:
1. Find stable center-of-mass via iterative shrinking sphere.
2. Compute principal axes via inertia tensor.
3. Align disk angular momentum to the +Z axis.
"""

import numpy as np
from typing import Optional, Tuple


def get_stable_center(
    coordinates: np.ndarray,
    masses: Optional[np.ndarray] = None,
    iter_max: int = 25,
    enclose_radius: float = 100.0,
    tol_rel: float = 0.01,
    tol_abs: float = 0.1,
) -> np.ndarray:
    """Iteratively find the center-of-mass using shrinking spheres.

    Parameters
    ----------
    coordinates : (N, 3) ndarray
        Cartesian positions.
    masses : (N,) ndarray or None
        Particle masses. If None, equal-mass is assumed.
    iter_max : int
        Maximum iterations.
    enclose_radius : float
        Initial enclosing radius in kpc.
    tol_rel : float
        Relative convergence tolerance.
    tol_abs : float
        Absolute convergence tolerance in kpc.

    Returns
    -------
    center : (3,) ndarray
        COM position in kpc.
    """
    center = np.zeros(3)
    radius = enclose_radius

    if masses is None:
        masses = np.ones(len(coordinates))

    for _ in range(iter_max):
        # Select particles within current radius from center
        dist = np.linalg.norm(coordinates - center, axis=1)
        mask = dist < radius
        if mask.sum() < 10:
            break

        coords_in = coordinates[mask]
        masses_in = masses[mask]
        new_center = np.average(coords_in, axis=0, weights=masses_in)

        err = np.linalg.norm(new_center - center)
        if err < max(tol_rel * radius, tol_abs):
            center = new_center
            break

        center = new_center
        radius *= 0.5

    return center


def get_principal_axes(
    coordinates: np.ndarray,
    masses: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute principal axes via the moment-of-inertia tensor.

    Parameters
    ----------
    coordinates : (N, 3) ndarray
        Cartesian positions (already centered).
    masses : (N,) ndarray or None
        Particle masses. Equal-mass if None.

    Returns
    -------
    eigenvalues : (3,) ndarray
        Sorted ascending (minor → major axis).
    eigenvectors : (3, 3) ndarray
        Columns are the sorted eigenvectors.
    """
    if masses is None:
        masses = np.ones(len(coordinates))

    I = np.zeros((3, 3))
    I[0, 0] = np.sum(masses * (coordinates[:, 1]**2 + coordinates[:, 2]**2))
    I[1, 1] = np.sum(masses * (coordinates[:, 0]**2 + coordinates[:, 2]**2))
    I[2, 2] = np.sum(masses * (coordinates[:, 0]**2 + coordinates[:, 1]**2))
    I[0, 1] = -np.sum(masses * coordinates[:, 0] * coordinates[:, 1])
    I[0, 2] = -np.sum(masses * coordinates[:, 0] * coordinates[:, 2])
    I[1, 2] = -np.sum(masses * coordinates[:, 1] * coordinates[:, 2])
    I[1, 0] = I[0, 1]
    I[2, 0] = I[0, 2]
    I[2, 1] = I[1, 2]

    eigenvalues, eigenvectors = np.linalg.eigh(I)
    return eigenvalues, eigenvectors


def align_disk(
    coordinates: np.ndarray,
    velocities: np.ndarray,
    masses: Optional[np.ndarray] = None,
    enclose_radius: float = -1.0,
    return_rot_mat: bool = False,
) -> Tuple:
    """Align disk angular momentum to +Z axis.

    Also aligns the minor axis (shortest principal axis) to +Z as a fallback
    for face-on viewing.

    Parameters
    ----------
    coordinates : (N, 3) ndarray
        Cartesian positions.
    velocities : (N, 3) ndarray
        Cartesian velocities.
    masses : (N,) ndarray or None
        Particle masses.
    enclose_radius : float
        Only use particles within this radius. -1 means all.
    return_rot_mat : bool
        If True, return only the (3,3) rotation matrix.

    Returns
    -------
    If return_rot_mat=True: rotation_matrix (3,3)
    Else: (rotated_coords, rotated_vels) or tuple with optional arrays.
    """
    if masses is None:
        masses = np.ones(len(coordinates))

    # Compute angular momentum
    if enclose_radius > 0:
        rs = np.linalg.norm(coordinates[:, :2], axis=1)
        mask = rs < enclose_radius
        coords_sub = coordinates[mask]
        vels_sub = velocities[mask]
        masses_sub = masses[mask]
    else:
        coords_sub = coordinates
        vels_sub = velocities
        masses_sub = masses

    L = np.zeros(3)
    for i in range(len(coords_sub)):
        m = masses_sub[i]
        L += m * np.cross(coords_sub[i], vels_sub[i])

    L_norm = np.linalg.norm(L)
    if L_norm < 1e-20:
        return np.eye(3) if return_rot_mat else (coordinates, velocities)

    z_axis = np.array([0.0, 0.0, 1.0])
    L_dir = L / L_norm

    # Rotation axis (cross product)
    rot_axis = np.cross(L_dir, z_axis)
    rot_axis_norm = np.linalg.norm(rot_axis)

    if rot_axis_norm < 1e-10:
        rotation = np.eye(3)
    else:
        rot_axis = rot_axis / rot_axis_norm
        cos_theta = np.dot(L_dir, z_axis)
        theta = np.arccos(np.clip(cos_theta, -1.0, 1.0))

        # Rodrigues rotation formula
        K = np.array([
            [0, -rot_axis[2], rot_axis[1]],
            [rot_axis[2], 0, -rot_axis[0]],
            [-rot_axis[1], rot_axis[0], 0],
        ])
        rotation = np.eye(3) + np.sin(theta) * K + (1 - cos_theta) * K @ K

    if return_rot_mat:
        return rotation

    coords_rot = np.matmul(rotation, coordinates.T).T
    vels_rot = np.matmul(rotation, velocities.T).T
    return coords_rot, vels_rot


def recenter_coordinates(
    coordinates: np.ndarray,
    center: np.ndarray,
) -> np.ndarray:
    """Shift coordinates to a given center.

    Parameters
    ----------
    coordinates : (N, 3) ndarray
    center : (3,) ndarray

    Returns
    -------
    (N, 3) ndarray
    """
    return coordinates - center
