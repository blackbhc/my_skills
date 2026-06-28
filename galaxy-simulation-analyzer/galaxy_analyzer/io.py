"""
io.py — HDF5 snapshot I/O driven by Header NumPart_ThisFile.

Handles loading Gadget-style HDF5 snapshots.  By default, reads
``Header/NumPart_ThisFile`` to discover which PartTypes are present
and how many particles each contains; the user may optionally override
with an explicit PartType list.

Each PartType group contains: Coordinates, Velocities, Masses,
ParticleIDs, Potential.
"""

import h5py
import numpy as np
from typing import Optional, List, Dict, Union


# Fields that may be present inside each PartType group.
_EXPECTED_FIELDS = [
    "Coordinates",
    "Velocities",
    "Masses",
    "ParticleIDs",
    "Potential",
]


def _get_num_part_this_file(f: h5py.File) -> np.ndarray:
    """Return ``NumPart_ThisFile`` from the Header group.

    Returns an (NTYPES,) int array; element *i* is the particle count
    for PartType *i* in this file.  A Gadget snapshot always has
    exactly 6 PartTypes (0–5).
    """
    header = f["Header"]
    return np.asarray(header.attrs["NumPart_ThisFile"], dtype=int)


def get_num_part(path: str) -> np.ndarray:
    """Return ``NumPart_ThisFile`` as a 1-D int array.

    Parameters
    ----------
    path : str
        Path to the .hdf5 snapshot file.

    Returns
    -------
    num_part : ndarray of int
        Particle counts per PartType (index = PartType).
    """
    with h5py.File(path, "r") as f:
        return _get_num_part_this_file(f)


def load_snapshot(
    path: str,
    part_types: Optional[Union[int, List[int]]] = None,
) -> Dict[int, Dict[str, np.ndarray]]:
    """Load a Gadget-style HDF5 snapshot.

    Parameters
    ----------
    path : str
        Path to the .hdf5 snapshot file.
    part_types : int, list of int, or None
        PartType(s) to load.  If *None* (default), every PartType
        whose ``NumPart_ThisFile`` count is > 0 is loaded.

    Returns
    -------
    dict
        Nested dict: ``{part_type: {field: ndarray}}``.
        Field names: Coordinates, Velocities, Masses, ParticleIDs,
        Potential.  PartTypes with no particles are omitted.
    """
    with h5py.File(path, "r") as f:
        num_part = _get_num_part_this_file(f)

        if part_types is None:
            part_types = [i for i, n in enumerate(num_part) if n > 0]
        elif isinstance(part_types, int):
            part_types = [part_types]

        result: Dict[int, Dict[str, np.ndarray]] = {}
        for pt in part_types:
            if pt < 0 or pt >= len(num_part):
                continue
            if num_part[pt] <= 0:
                continue

            grp_name = f"PartType{pt}"
            if grp_name not in f:
                continue

            grp = f[grp_name]
            entry: Dict[str, np.ndarray] = {}
            for field in _EXPECTED_FIELDS:
                if field in grp:
                    data = grp[field][:]
                    expected_n = num_part[pt]
                    if len(data) != expected_n:
                        # Truncate or pad to match NumPart_ThisFile
                        data = data[:expected_n]
                    entry[field] = data
            if entry:
                result[pt] = entry

    return result


def get_header_attrs(path: str) -> dict:
    """Read Header group attributes from the snapshot.

    Parameters
    ----------
    path : str
        Path to the .hdf5 file.

    Returns
    -------
    dict
        Header attributes (NumPart_ThisFile, NumPart_Total, Time,
        Redshift, BoxSize, MassTable, …).
    """
    with h5py.File(path, "r") as f:
        return dict(f["Header"].attrs)
