"""
structure.py — Disk scale length/height and Sersic index fitting.

- getRdHz: exponential scale length and scale height
- fit_sersic: Sersic profile fitting
"""

import numpy as np
from scipy.stats import linregress
from scipy.stats import binned_statistic_2d
from scipy.optimize import curve_fit
from typing import Tuple, Optional


def getRdHz(
    masses: np.ndarray,
    cartesian_coordinates: np.ndarray,
    Rmin: float = 0.1,
    Rmax: float = 30.0,
    RbinNum: int = 60,
    Zmax: float = 3.0,
    ZbinNum: int = 18,
) -> Tuple[float, float]:
    """Compute disk scale length (Rd) and scale height (Zd).

    Fits exponential profiles to the mid-plane and vertical density.

    Parameters
    ----------
    masses : (N,) ndarray
    cartesian_coordinates : (N, 3) ndarray
    Rmin, Rmax : float
        Radial range for Rd fit.
    RbinNum : int
    Zmax : float
        Half the vertical range.
    ZbinNum : int

    Returns
    -------
    Rd : float
        Disk scale length in kpc.
    Zd : float
        Disk scale height in kpc.
    """
    Rs = np.linalg.norm(cartesian_coordinates[:, :2], axis=1)
    Zs = cartesian_coordinates[:, 2]
    Zmin = -abs(Zmax)

    R_edges = np.linspace(Rmin, Rmax, RbinNum + 1)
    Z_edges = np.linspace(Zmin, Zmax, ZbinNum + 1)

    M_tot, _, _, _ = binned_statistic_2d(
        x=Rs, y=Zs, values=masses,
        bins=[R_edges, Z_edges],
        statistic="sum",
    )

    R_centers = (R_edges[1:] + R_edges[:-1]) / 2.0
    Z_centers = (Z_edges[1:] + Z_edges[:-1]) / 2.0
    delta_R = (Rmax - Rmin) / RbinNum
    delta_Z = (Zmax - Zmin) / ZbinNum

    # Convert to volume density rho(R,z)
    rho = M_tot.copy()
    for j in range(rho.shape[1]):
        rho[:, j] /= (delta_R * delta_Z * 2.0 * np.pi * R_centers)

    # Fit Rd from mid-plane density
    mid_idx = int(len(Z_centers) / 2)
    mask_R = rho[:, mid_idx] > 0
    if mask_R.sum() >= 3:
        res = linregress(R_centers[mask_R], np.log(rho[:, mid_idx][mask_R]))
        Rd = -1.0 / res.slope if res.slope < 0 else np.nan
    else:
        Rd = np.nan

    # Fit Zd from vertical density averaged over inner radial bins
    n_zd_bins = min(3, rho.shape[0])
    rho_Z_avg = np.nanmean(rho[:n_zd_bins, :], axis=0)
    mask_Z = rho_Z_avg > 0
    if mask_Z.sum() >= 3:
        res = linregress(np.abs(Z_centers[mask_Z]), np.log(rho_Z_avg[mask_Z]))
        Zd = -1.0 / res.slope if res.slope < 0 else np.nan
    else:
        Zd = np.nan

    return Rd, Zd


def fit_sersic(
    Rs: np.ndarray,
    surface_density: np.ndarray,
) -> Tuple[float, float]:
    """Fit a Sersic profile to the surface density.

    ln I(R) = ln I_0 - k * R^(1/n)

    Parameters
    ----------
    Rs : (N,) ndarray
        Radii in kpc.
    surface_density : (N,) ndarray
        Surface density values.

    Returns
    -------
    n : float
        Sersic index.
    n_err : float
        1-sigma uncertainty on Sersic index.
    """
    mask = surface_density > 0
    Rs_clean = Rs[mask]
    sd_clean = surface_density[mask]

    if len(Rs_clean) < 10:
        return np.nan, np.nan

    def sersic_ln(R, ln_I0, k, n):
        if n <= 0:
            return np.full_like(R, -1e20)
        return ln_I0 - k * R ** (1.0 / n)

    try:
        popt, pcov = curve_fit(
            sersic_ln, Rs_clean, np.log(sd_clean),
            p0=[np.log(sd_clean[0]), 1.0, 1.0],
            maxfev=10000,
        )
        n = popt[2]
        n_err = np.sqrt(pcov[2, 2]) if pcov[2, 2] > 0 else np.nan
        return n, n_err
    except Exception:
        return np.nan, np.nan
