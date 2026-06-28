"""
coords.py — Coordinate transformations for N-body simulations.

Supports:
- car2cyl : Cartesian (x, y, z) -> Cylindrical (R, phi, z)
- cyl2car : Cylindrical (R, phi, z) -> Cartesian (x, y, z)
- car2sph : Cartesian (x, y, z) -> Spherical (r, phi, theta)
- sph2car : Spherical (r, phi, theta) -> Cartesian (x, y, z)

All functions accept optional velocities.  When *velocities* is omitted
only the coordinate array is returned.
Convention: theta = colatitude from +Z axis.
"""

import numpy as np
from typing import Optional, Tuple, Union


def car2cyl(
    coordinates: np.ndarray,
    velocities: Optional[np.ndarray] = None,
) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
    """Transform Cartesian coordinates (and optionally velocities) to cylindrical.

    Parameters
    ----------
    coordinates : (N, 3) ndarray
        Columns (x, y, z) in kpc.
    velocities : (N, 3) ndarray or None
        Columns (vx, vy, vz) in km/s.  If None, only coordinates are
        transformed.

    Returns
    -------
    cyl_pos : (N, 3) ndarray
        Columns (R, phi, z).  If *velocities* is given, a 2-tuple
        ``(cyl_pos, cyl_vel)`` is returned.
    cyl_vel : (N, 3) ndarray
        Columns (V_R, V_phi, V_z).  Only returned when *velocities*
        is provided.
    """
    x, y, z = coordinates[:, 0], coordinates[:, 1], coordinates[:, 2]
    R = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    cyl_pos = np.column_stack((R, phi, z))

    if velocities is None:
        return cyl_pos

    vx, vy, vz = velocities[:, 0], velocities[:, 1], velocities[:, 2]
    with np.errstate(divide="ignore", invalid="ignore"):
        e_R_x = np.where(R > 0, x / R, 0.0)
        e_R_y = np.where(R > 0, y / R, 0.0)
    e_phi_x = -np.sin(phi)
    e_phi_y = np.cos(phi)
    V_R = vx * e_R_x + vy * e_R_y
    V_phi = vx * e_phi_x + vy * e_phi_y
    V_z = vz
    cyl_vel = np.column_stack((V_R, V_phi, V_z))
    return cyl_pos, cyl_vel


def cyl2car(
    coordinates: np.ndarray,
    velocities: Optional[np.ndarray] = None,
) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
    """Transform cylindrical coordinates (and optionally velocities) to Cartesian.

    Parameters
    ----------
    coordinates : (N, 3) ndarray
        Columns (R, phi, z).
    velocities : (N, 3) ndarray or None
        Columns (V_R, V_phi, V_z).  If None, only coordinates are
        transformed.

    Returns
    -------
    car_pos : (N, 3) ndarray
        Columns (x, y, z).  A 2-tuple ``(car_pos, car_vel)`` when
        *velocities* is given.
    car_vel : (N, 3) ndarray
        Columns (vx, vy, vz).  Only returned with *velocities*.
    """
    R, phi, z = coordinates[:, 0], coordinates[:, 1], coordinates[:, 2]
    cos_phi = np.cos(phi)
    sin_phi = np.sin(phi)
    x = R * cos_phi
    y = R * sin_phi
    car_pos = np.column_stack((x, y, z))

    if velocities is None:
        return car_pos

    V_R, V_phi, V_z = velocities[:, 0], velocities[:, 1], velocities[:, 2]
    vx = V_R * cos_phi - V_phi * sin_phi
    vy = V_R * sin_phi + V_phi * cos_phi
    vz = V_z
    car_vel = np.column_stack((vx, vy, vz))
    return car_pos, car_vel


def _inner_product(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Row-wise dot product of two (N, 3) arrays."""
    return np.sum(a * b, axis=1)


def car2sph(
    coordinates: np.ndarray,
    velocities: Optional[np.ndarray] = None,
) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
    """Transform Cartesian coordinates (and optionally velocities) to spherical.

    Parameters
    ----------
    coordinates : (N, 3) ndarray
        Columns (x, y, z) in kpc.
    velocities : (N, 3) ndarray or None
        Columns (vx, vy, vz) in km/s.  If None, only coordinates are
        transformed.

    Returns
    -------
    sph_pos : (N, 3) ndarray
        Columns (r, phi, theta), theta = colatitude from +Z.  A 2-tuple
        ``(sph_pos, sph_vel)`` when *velocities* is given.
    sph_vel : (N, 3) ndarray
        Columns (V_r, V_phi, V_theta).  Only returned with *velocities*.
    """
    r = np.linalg.norm(coordinates, axis=1)
    phi = np.arctan2(coordinates[:, 1], coordinates[:, 0])
    theta = np.arccos(np.clip(coordinates[:, 2] / np.where(r > 0, r, 1e-20), -1.0, 1.0))
    sph_pos = np.column_stack((r, phi, theta))

    if velocities is None:
        return sph_pos

    with np.errstate(divide="ignore", invalid="ignore"):
        unit_r = coordinates / np.column_stack((r, r, r))
        unit_r = np.where(np.column_stack((r, r, r)) > 0, unit_r, 0.0)
    unit_phi = np.column_stack((-np.sin(phi), np.cos(phi), np.zeros(len(phi))))
    V_r = _inner_product(unit_r, velocities)
    V_phi = _inner_product(unit_phi, velocities)
    vec_Vr = np.column_stack((V_r, V_r, V_r)) * unit_r
    vec_Vphi = np.column_stack((V_phi, V_phi, V_phi)) * unit_phi
    residual = velocities - vec_Vr - vec_Vphi
    unit_theta = np.cross(unit_r, unit_phi)
    V_theta = _inner_product(unit_theta, residual)
    sph_vel = np.column_stack((V_r, V_phi, V_theta))
    return sph_pos, sph_vel


def sph2car(
    coordinates: np.ndarray,
    velocities: Optional[np.ndarray] = None,
) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
    """Transform spherical coordinates (and optionally velocities) to Cartesian.

    Parameters
    ----------
    coordinates : (N, 3) ndarray
        Columns (r, phi, theta).
    velocities : (N, 3) ndarray or None
        Columns (V_r, V_phi, V_theta).  If None, only coordinates are
        transformed.

    Returns
    -------
    car_pos : (N, 3) ndarray
        Columns (x, y, z).  A 2-tuple ``(car_pos, car_vel)`` when
        *velocities* is given.
    car_vel : (N, 3) ndarray
        Columns (vx, vy, vz).  Only returned with *velocities*.
    """
    r, phi, theta = coordinates[:, 0], coordinates[:, 1], coordinates[:, 2]
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)
    sin_phi = np.sin(phi)
    cos_phi = np.cos(phi)
    x = r * sin_theta * cos_phi
    y = r * sin_theta * sin_phi
    z = r * cos_theta
    car_pos = np.column_stack((x, y, z))

    if velocities is None:
        return car_pos

    V_r, V_phi, V_theta = velocities[:, 0], velocities[:, 1], velocities[:, 2]
    unit_r = np.column_stack((sin_theta * cos_phi,
                               sin_theta * sin_phi,
                               cos_theta))
    unit_phi = np.column_stack((-sin_phi, cos_phi, np.zeros(len(phi))))
    unit_theta = np.cross(unit_r, unit_phi)
    vx = V_r * unit_r[:, 0] + V_theta * unit_theta[:, 0] + V_phi * unit_phi[:, 0]
    vy = V_r * unit_r[:, 1] + V_theta * unit_theta[:, 1] + V_phi * unit_phi[:, 1]
    vz = V_r * unit_r[:, 2] + V_theta * unit_theta[:, 2] + V_phi * unit_phi[:, 2]
    car_vel = np.column_stack((vx, vy, vz))
    return car_pos, car_vel


def anisotropy(V_r: np.ndarray, V_phi: np.ndarray, V_theta: np.ndarray):
    """Compute the radial orbital anisotropy parameter.

    beta = 1 - (sigma_theta^2 + sigma_phi^2) / (2 * sigma_r^2)

    Parameters
    ----------
    V_r, V_phi, V_theta : (N,) ndarray
        Spherical velocity components.

    Returns
    -------
    float
        Anisotropy parameter beta.
    """
    sigma_r = np.nanstd(V_r)
    sigma_phi = np.nanstd(V_phi)
    sigma_theta = np.nanstd(V_theta)
    if sigma_r == 0:
        return np.nan
    beta = 1.0 - (sigma_theta**2 + sigma_phi**2) / (2.0 * sigma_r**2)
    return beta
