"""
morphology.py — Bar strength, m=2 Fourier mode, buckling analysis.

Key functions:
- A2: amplitude of m=2 Fourier mode (bar strength)
- m2phase: phase angle of m=2 mode
- A2profile: radial profile of A2
- RbarThreshold: bar radius estimate
- Sbuckling: buckling amplitude
- BPXstrength: boxy/peanut bulge strength
- monotonize_bar_angle: unwrap bar angle time series
"""

import numpy as np
from scipy.interpolate import interp1d
from typing import Optional, Tuple


def A2(
    phis: np.ndarray,
    masses: Optional[np.ndarray] = None,
    normalize: bool = True,
) -> float:
    """Compute m=2 Fourier amplitude (bar strength indicator).

    A2 = |Σ m_j * exp(2i * φ_j)| / Σ m_j   (if normalize)
       = |Σ exp(2i * φ_j)|                  (if not)

    Parameters
    ----------
    phis : (N,) ndarray
        Azimuthal angles in radians.
    masses : (N,) ndarray or None
        Particle masses. Equal-mass if None.
    normalize : bool
        If True, divide by total mass (or count).

    Returns
    -------
    float
        m=2 amplitude.
    """
    exponents = np.exp(2j * phis)
    if masses is None or len(masses) == 0:
        numerator = np.abs(np.sum(exponents))
        denominator = len(phis)
    else:
        numerator = np.abs(np.sum(masses * exponents))
        denominator = np.sum(masses)

    if normalize and denominator > 0:
        return numerator / denominator
    return numerator


def m2phase(
    phis: np.ndarray,
    masses: Optional[np.ndarray] = None,
) -> float:
    """Compute phase angle of the m=2 mode (bar position angle).

    Parameters
    ----------
    phis : (N,) ndarray
        Azimuthal angles in radians.
    masses : (N,) ndarray or None

    Returns
    -------
    float
        Phase angle in radians, range [-pi/2, pi/2].
    """
    exponents = np.exp(2j * phis)
    if masses is None or len(masses) == 0:
        A2_complex = np.sum(exponents)
    else:
        A2_complex = np.sum(masses * exponents)
    return np.arctan2(A2_complex.imag, A2_complex.real) / 2.0


def A2profile(
    phis: np.ndarray,
    Rs: np.ndarray,
    masses: Optional[np.ndarray] = None,
    Rmin: float = 0.1,
    Rmax: float = 20.0,
    RbinNum: int = 40,
    normalize: bool = True,
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute radial profile of m=2 amplitude.

    Parameters
    ----------
    phis : (N,) ndarray
        Azimuthal angles.
    Rs : (N,) ndarray
        Cylindrical radii.
    masses : (N,) ndarray or None
    Rmin, Rmax : float
    RbinNum : int
    normalize : bool

    Returns
    -------
    A2s : (RbinNum,) ndarray
    R_centers : (RbinNum,) ndarray
    """
    R_edges = np.linspace(Rmin, Rmax, RbinNum + 1)
    R_centers = (R_edges[1:] + R_edges[:-1]) / 2.0
    A2s = np.zeros(RbinNum)

    for i in range(RbinNum):
        mask = (Rs >= R_edges[i]) & (Rs < R_edges[i + 1])
        if mask.sum() > 0:
            A2s[i] = A2(phis[mask],
                        masses[mask] if masses is not None else None,
                        normalize=normalize)
        else:
            A2s[i] = np.nan

    return A2s, R_centers


def RbarThreshold(
    phis: np.ndarray,
    Rs: np.ndarray,
    masses: Optional[np.ndarray] = None,
    Rmin: float = 0.01,
    Rmax: float = 20.0,
    RbinNum: int = 40,
    threshold: float = 1.0,
) -> float:
    """Estimate bar radius where A2 drops to threshold fraction of peak-to-min.

    Parameters
    ----------
    phis, Rs, masses : ndarray
    Rmin, Rmax : float
    RbinNum : int
    threshold : float
        1.0 = peak A2 location, 0.0 = outer minimum.

    Returns
    -------
    float
        Bar radius in kpc.
    """
    profile, R_centers = A2profile(phis, Rs, masses, Rmin, Rmax, RbinNum)

    finterp = interp1d(R_centers, profile, kind="linear")
    finer_Rs = np.linspace(R_centers.min(), R_centers.max(), 5 * RbinNum)
    interp_profile = finterp(finer_Rs)

    max_id = np.argmax(interp_profile)
    peak = interp_profile[max_id]
    outer_min = np.min(interp_profile[max_id:])
    outer_range = peak - outer_min

    if outer_range <= 0:
        return finer_Rs[max_id]

    threshold_A2 = outer_min + outer_range * threshold
    beyond_peak = interp_profile[max_id:]
    idx = np.where(beyond_peak <= threshold_A2)[0]
    if len(idx) == 0:
        return finer_Rs[-1]

    return finer_Rs[max_id:][idx[0]]


def Sbuckling(
    phis: np.ndarray,
    Zs: np.ndarray,
    masses: Optional[np.ndarray] = None,
    normalize: bool = True,
) -> float:
    """Compute buckling (banana mode) amplitude.

    S_buckle = |Σ m_j * Z_j * exp(2i * φ_j)| / Σ m_j

    Parameters
    ----------
    phis : (N,) ndarray
    Zs : (N,) ndarray
    masses : (N,) ndarray or None
    normalize : bool

    Returns
    -------
    float
    """
    exponents = np.exp(2j * phis)
    if masses is None or len(masses) == 0:
        numerator = np.abs(np.sum(Zs * exponents))
        denominator = len(Zs)
    else:
        numerator = np.abs(np.sum(masses * Zs * exponents))
        denominator = np.sum(masses)

    if normalize and denominator > 0:
        return numerator / denominator
    return numerator


def BPXstrength(
    Zs: np.ndarray,
    masses: Optional[np.ndarray] = None,
) -> float:
    """Compute boxy/peanut (B/P) bulge strength.

    B/P = Σ m_j * Z_j^2 / Σ m_j

    Parameters
    ----------
    Zs : (N,) ndarray
    masses : (N,) ndarray or None

    Returns
    -------
    float
    """
    if masses is None or len(masses) == 0:
        return np.mean(Zs**2)
    return np.sum(masses * Zs**2) / np.sum(masses)


def monotonize_bar_angle(
    bar_angles: np.ndarray,
    threshold: float = np.deg2rad(90),
) -> np.ndarray:
    """Unwrap bar angle time series to remove π-periodic jumps.

    Parameters
    ----------
    bar_angles : (N,) ndarray
        Bar angles in radians, range [-pi/2, pi/2].
    threshold : float
        Jump threshold in radians.

    Returns
    -------
    (N,) ndarray
        Monotonized bar angles.
    """
    assert bar_angles.min() >= -np.pi / 2 and bar_angles.max() <= np.pi / 2

    sign = np.sign(np.mean(np.sign(bar_angles[1:] - bar_angles[:-1])))
    result = bar_angles.copy()
    for i in range(len(result) - 1):
        if (result[i + 1] - result[i]) / sign <= -threshold:
            result[i + 1:] += np.pi * sign
    return result
