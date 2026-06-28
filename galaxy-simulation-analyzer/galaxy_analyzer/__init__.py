"""
GalaxyAnalyzer — Master class for N-body galaxy simulation analysis.

Provides a unified interface to all sub-modules:
- io: HDF5 snapshot I/O
- preprocess: recenter + disk alignment
- coords: coordinate transformations (cartesian ↔ cylindrical ↔ spherical)
- profile: surface density & radial profiles
- morphology: bar strength, m=2, buckling
- structure: scale length/height, Sersic index
- vis: visualization (face-on, edge-on, 3-panel)

All methods can be called directly on GalaxyAnalyzer instances.
"""

import numpy as np
from typing import Optional, Tuple, List, Dict

# Import all sub-modules
from . import io
from . import preprocess as _preprocess
from . import coords as _coords
from . import profile as _profile
from . import morphology as _morphology
from . import structure as _structure
from . import vis as _vis

# Matplotlib defaults (user can override)
import matplotlib as mpl
mpl.rcParams.update({
    "font.family": "Times New Roman",
    "font.size": 26,
    "mathtext.fontset": "cm",
})


class GalaxyAnalyzer:
    """Master class for analyzing galaxy N-body simulation snapshots.

    Usage
    -----
    >>> ga = GalaxyAnalyzer()
    >>> data = ga.load_snapshot("snapshot.hdf5", part_types=2)
    >>> coords = data[2]['Coordinates']
    >>> masses = data[2]['Masses']
    >>> coords, vels = ga.preprocess_disk(coords, masses=masses)
    >>> A2 = ga.A2(coords[:, 1])  # bar strength
    >>> ga.view_snapshot(coords, masses=masses)
    """

    # ---- I/O ----
    @staticmethod
    def load_snapshot(
        path: str,
        part_types: Optional[List[int]] = None,
    ) -> Dict[int, Dict[str, np.ndarray]]:
        """Load a Gadget-style HDF5 snapshot. See `io.load_snapshot`."""
        return io.load_snapshot(path, part_types)

    @staticmethod
    def get_num_part(path: str) -> np.ndarray:
        """Return NumPart_ThisFile array. See `io.get_num_part`."""
        return io.get_num_part(path)

    @staticmethod
    def get_header_attrs(path: str) -> dict:
        """Read Header group attributes. See `io.get_header_attrs`."""
        return io.get_header_attrs(path)

    # ---- Preprocessing ----
    @staticmethod
    def get_stable_center(
        coordinates: np.ndarray,
        masses: Optional[np.ndarray] = None,
        iter_max: int = 25,
        enclose_radius: float = 100.0,
        tol_rel: float = 0.01,
        tol_abs: float = 0.1,
    ) -> np.ndarray:
        """Find stable COM. See `preprocess.get_stable_center`."""
        return _preprocess.get_stable_center(
            coordinates, masses, iter_max, enclose_radius, tol_rel, tol_abs)

    @staticmethod
    def get_principal_axes(
        coordinates: np.ndarray,
        masses: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Compute principal axes. See `preprocess.get_principal_axes`."""
        return _preprocess.get_principal_axes(coordinates, masses)

    @staticmethod
    def align_disk(
        coordinates: np.ndarray,
        velocities: np.ndarray,
        masses: Optional[np.ndarray] = None,
        enclose_radius: float = -1.0,
        return_rot_mat: bool = False,
    ) -> Tuple:
        """Align disk to +Z. See `preprocess.align_disk`."""
        return _preprocess.align_disk(
            coordinates, velocities, masses, enclose_radius, return_rot_mat)

    @staticmethod
    def recenter_coordinates(
        coordinates: np.ndarray,
        center: np.ndarray,
    ) -> np.ndarray:
        """Shift coordinates to center. See `preprocess.recenter_coordinates`."""
        return _preprocess.recenter_coordinates(coordinates, center)

    def preprocess_disk(
        self,
        coordinates: np.ndarray,
        velocities: Optional[np.ndarray] = None,
        masses: Optional[np.ndarray] = None,
        enclose_radius: float = 100.0,
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Full preprocessing pipeline: recenter + align disk.

        Parameters
        ----------
        coordinates : (N, 3) ndarray
        velocities : (N, 3) ndarray or None
        masses : (N,) ndarray or None
        enclose_radius : float
            Initial radius for COM search.

        Returns
        -------
        coords_aligned : (N, 3) ndarray
        vels_aligned : (N, 3) ndarray or None
        """
        center = self.get_stable_center(
            coordinates, masses, enclose_radius=enclose_radius)
        coords_centered = self.recenter_coordinates(coordinates, center)

        if velocities is not None:
            coords_aligned, vels_aligned = self.align_disk(
                coords_centered, velocities, masses)
            return coords_aligned, vels_aligned
        else:
            return coords_centered, None

    # ---- Coordinate Transformations ----
    @staticmethod
    def car2cyl(coordinates, velocities):
        """Cartesian → Cylindrical. See `coords.car2cyl`."""
        return _coords.car2cyl(coordinates, velocities)

    @staticmethod
    def cyl2car(coordinates, velocities):
        """Cylindrical → Cartesian. See `coords.cyl2car`."""
        return _coords.cyl2car(coordinates, velocities)

    @staticmethod
    def car2sph(coordinates, velocities):
        """Cartesian → Spherical. See `coords.car2sph`."""
        return _coords.car2sph(coordinates, velocities)

    @staticmethod
    def sph2car(coordinates, velocities):
        """Spherical → Cartesian. See `coords.sph2car`."""
        return _coords.sph2car(coordinates, velocities)

    @staticmethod
    def anisotropy(V_r, V_phi, V_theta):
        """Compute orbital anisotropy. See `coords.anisotropy`."""
        return _coords.anisotropy(V_r, V_phi, V_theta)

    # ---- Profiles ----
    @staticmethod
    def radial_profile_surface_density(
        coordinates, masses=None,
        Rmin=0.1, Rmax=20.0, RbinNum=50, PhiBinNum=32,
    ):
        """Azimuthally averaged surface density. See `profile.radial_profile_surface_density`."""
        return _profile.radial_profile_surface_density(
            coordinates, masses, Rmin, Rmax, RbinNum, PhiBinNum)

    @staticmethod
    def radial_profile(
        coordinates, values,
        Rmin=0.1, Rmax=20.0, RbinNum=50, PhiBinNum=32,
        statistic="mean",
    ):
        """Azimuthally averaged radial profile. See `profile.radial_profile`."""
        return _profile.radial_profile(
            coordinates, values, Rmin, Rmax, RbinNum, PhiBinNum, statistic)

    # ---- Morphology ----
    @staticmethod
    def A2(phis, masses=None, normalize=True):
        """m=2 Fourier amplitude. See `morphology.A2`."""
        return _morphology.A2(phis, masses, normalize)

    @staticmethod
    def m2phase(phis, masses=None):
        """m=2 phase angle. See `morphology.m2phase`."""
        return _morphology.m2phase(phis, masses)

    @staticmethod
    def A2profile(phis, Rs, masses=None,
                   Rmin=0.1, Rmax=20.0, RbinNum=40, normalize=True):
        """Radial profile of A2. See `morphology.A2profile`."""
        return _morphology.A2profile(
            phis, Rs, masses, Rmin, Rmax, RbinNum, normalize)

    @staticmethod
    def RbarThreshold(phis, Rs, masses=None,
                       Rmin=0.01, Rmax=20.0, RbinNum=40, threshold=1.0):
        """Bar radius estimate. See `morphology.RbarThreshold`."""
        return _morphology.RbarThreshold(
            phis, Rs, masses, Rmin, Rmax, RbinNum, threshold)

    @staticmethod
    def Sbuckling(phis, Zs, masses=None, normalize=True):
        """Buckling amplitude. See `morphology.Sbuckling`."""
        return _morphology.Sbuckling(phis, Zs, masses, normalize)

    @staticmethod
    def BPXstrength(Zs, masses=None):
        """B/P bulge strength. See `morphology.BPXstrength`."""
        return _morphology.BPXstrength(Zs, masses)

    @staticmethod
    def monotonize_bar_angle(bar_angles, threshold=np.deg2rad(90)):
        """Unwrap bar angles. See `morphology.monotonize_bar_angle`."""
        return _morphology.monotonize_bar_angle(bar_angles, threshold)

    # ---- Structure ----
    @staticmethod
    def getRdHz(masses, cartesian_coordinates,
                 Rmin=0.1, Rmax=30.0, RbinNum=60, Zmax=3.0, ZbinNum=18):
        """Disk scale length and height. See `structure.getRdHz`."""
        return _structure.getRdHz(
            masses, cartesian_coordinates, Rmin, Rmax, RbinNum, Zmax, ZbinNum)

    @staticmethod
    def fit_sersic(Rs, surface_density):
        """Fit Sersic index. See `structure.fit_sersic`."""
        return _structure.fit_sersic(Rs, surface_density)

    # ---- Visualization ----
    @staticmethod
    def view_snapshot(coordinates, masses=None, size=20.0, binNum=100,
                      cmap="inferno", title="", save_path=None, show=True,
                      vmin=None, vmax=None):
        """3-panel projection. See `vis.view_snapshot`."""
        return _vis.view_snapshot(
            coordinates, masses, size, binNum, cmap, title,
            save_path, show, vmin, vmax)

    @staticmethod
    def face_on(coordinates, masses=None, size=20.0, binNum=200,
                cmap="inferno", title="Face-on View", save_path=None,
                show=True):
        """Face-on projection. See `vis.face_on`."""
        return _vis.face_on(
            coordinates, masses, size, binNum, cmap, title, save_path, show)

    @staticmethod
    def edge_on(coordinates, masses=None, size=20.0, binNum=200,
                cmap="inferno", title="Edge-on View", save_path=None,
                show=True):
        """Edge-on projection. See `vis.edge_on`."""
        return _vis.edge_on(
            coordinates, masses, size, binNum, cmap, title, save_path, show)
