"""
profile.py — Surface density and radial profiles.

Provides azimuthally averaged surface density profiles and
radial profiles of arbitrary scalar quantities.
"""

import numpy as np
from scipy.stats import binned_statistic_2d
from typing import Tuple, Optional


def radial_profile_surface_density(
    coordinates: np.ndarray,
    masses: Optional[np.ndarray] = None,
    Rmin: float = 0.1,
    Rmax: float = 20.0,
    RbinNum: int = 50,
    PhiBinNum: int = 32,
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute azimuthally averaged surface density profile.

    Parameters
    ----------
    coordinates : (N, 3) ndarray
        Cartesian positions (x, y, z). Only x,y are used for R.
    masses : (N,) ndarray or None
        Particle masses. Equal-mass if None.
    Rmin, Rmax : float
        Radial range in kpc.
    RbinNum : int
        Number of radial bins.
    PhiBinNum : int
        Number of azimuthal bins.

    Returns
    -------
    rs : (RbinNum,) ndarray
        Radial bin centers.
    surface_density : (RbinNum,) ndarray
        Azimuthally averaged surface density in M_sun / kpc^2.
    """
    if masses is None:
        masses = np.ones(len(coordinates))

    R = np.linalg.norm(coordinates[:, :2], axis=1)
    phi = np.arctan2(coordinates[:, 1], coordinates[:, 0])

    mass_sum, R_edges, phi_edges, _ = binned_statistic_2d(
        x=R, y=phi, values=masses,
        range=[[Rmin, Rmax], [0.0, 2.0 * np.pi]],
        bins=[RbinNum, PhiBinNum],
        statistic="sum",
    )

    r_centers = (R_edges[1:] + R_edges[:-1]) / 2.0
    delta_R = (Rmax - Rmin) / RbinNum
    # Area of each bin sector
    areas = 2.0 * np.pi * r_centers * delta_R / PhiBinNum

    surface_density = np.nanmean(mass_sum, axis=1) / areas
    return r_centers, surface_density


def radial_profile(
    coordinates: np.ndarray,
    values: np.ndarray,
    Rmin: float = 0.1,
    Rmax: float = 20.0,
    RbinNum: int = 50,
    PhiBinNum: int = 32,
    statistic: str = "mean",
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute azimuthally averaged radial profile of any scalar.

    Parameters
    ----------
    coordinates : (N, 3) ndarray
    values : (N,) ndarray
        Scalar values to profile.
    Rmin, Rmax : float
    RbinNum : int
    PhiBinNum : int
    statistic : str
        Statistic to compute ('mean', 'median', 'sum', 'std', etc.).

    Returns
    -------
    rs : (RbinNum,) ndarray
    profile : (RbinNum,) ndarray
    """
    R = np.linalg.norm(coordinates[:, :2], axis=1)
    phi = np.arctan2(coordinates[:, 1], coordinates[:, 0])

    result, R_edges, phi_edges, _ = binned_statistic_2d(
        x=R, y=phi, values=values,
        range=[[Rmin, Rmax], [0.0, 2.0 * np.pi]],
        bins=[RbinNum, PhiBinNum],
        statistic=statistic,
    )

    r_centers = (R_edges[1:] + R_edges[:-1]) / 2.0
    profile = np.nanmean(result, axis=1)
    return r_centers, profile
