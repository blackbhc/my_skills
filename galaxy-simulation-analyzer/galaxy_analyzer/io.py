"""
io.py — HDF5 snapshot I/O with PartType selection.

Handles loading Gadget-style HDF5 snapshots.
Each PartType group contains: Coordinates, Velocities, Masses, ParticleIDs, Potential.
"""

import h5py
import numpy as np
from typing import Optional, List, Dict, Union


def load_snapshot(
    path: str,
    part_types: Optional[Union[int, List[int]]] = None,
) -> Dict[int, Dict[str, np.ndarray]]:
    """Load a Gadget-style HDF5 snapshot.

    Parameters
    ----------
    path : str
        Path to the .hdf5 snapshot file.
    part_types : int or list of int, optional
        PartType(s) to load. Default None loads all.

    Returns
    -------
    dict
        Nested dict: {part_type: {field: ndarray}}.
        Field names: Coordinates, Velocities, Masses, ParticleIDs, Potential.
    """
    if part_types is None:
        part_types = [1, 2, 3, 4]
    elif isinstance(part_types, int):
        part_types = [part_types]

    result = {}
    with h5py.File(path, "r") as f:
        for pt in part_types:
            grp_name = f"PartType{pt}"
            if grp_name not in f:
                continue
            grp = f[grp_name]
            entry = {}
            for field in ["Coordinates", "Velocities", "Masses",
                          "ParticleIDs", "Potential"]:
                if field in grp:
                    entry[field] = grp[field][:]
            if entry:
                result[pt] = entry
    return result


def get_header_attrs(path: str) -> dict:
    """Read top-level attributes (e.g. time, redshift) from the snapshot.

    Parameters
    ----------
    path : str
        Path to the .hdf5 file.

    Returns
    -------
    dict
        Header attributes.
    """
    with h5py.File(path, "r") as f:
        return dict(f.attrs)
