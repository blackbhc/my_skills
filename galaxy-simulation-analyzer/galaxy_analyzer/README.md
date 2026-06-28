# galaxy_analyzer — N-body Disk Galaxy Simulation Analysis Toolkit

A modular Python toolkit for analyzing Gadget-style HDF5 simulation snapshots of disk galaxies.

## Architecture

```
galaxy_analyzer/
├── __init__.py      # Master class GalaxyAnalyzer (25 methods, unified API)
├── io.py            # HDF5 snapshot I/O with PartType selection
├── coords.py        # Coordinate transforms (car2cyl, car2sph, sph2car)
├── preprocess.py    # Recenter (shrinking-sphere) + disk alignment
├── profile.py       # Azimuthally averaged surface density / radial profiles
├── morphology.py    # Bar strength (m=2), buckling, B/P bulge
├── structure.py     # Disk scale length/height, Sersic index fitting
├── vis.py           # Face-on / edge-on / 3-panel visualization
```

## Quick Start

```python
from galaxy_analyzer import GalaxyAnalyzer

ga = GalaxyAnalyzer()
data = ga.load_snapshot("snapshot.hdf5", part_types=2)
coords, vels = ga.preprocess_disk(
    data[2]["Coordinates"], data[2]["Velocities"], data[2]["Masses"],
)
A2 = ga.A2(ga.car2cyl(coords, vels)[0][:, 1], masses=data[2]["Masses"])
ga.view_snapshot(coords, masses=data[2]["Masses"])
```

## Module Summary

| Module | Key Functions | Description |
|--------|--------------|-------------|
| `io` | `load_snapshot`, `get_header_attrs` | Load Gadget HDF5 snapshots by PartType |
| `coords` | `car2cyl`, `car2sph`, `sph2car`, `anisotropy` | Cartesian ↔ cylindrical ↔ spherical |
| `preprocess` | `get_stable_center`, `align_disk`, `preprocess_disk` | Recenter via shrinking sphere, align L to +Z |
| `profile` | `radial_profile_surface_density`, `radial_profile` | Azimuthally averaged profiles of any scalar |
| `morphology` | `A2`, `m2phase`, `A2profile`, `RbarThreshold`, `Sbuckling`, `BPXstrength` | Bar / buckling / B/P bulge analysis |
| `structure` | `getRdHz`, `fit_sersic` | Exponential scale length/height, Sersic index |
| `vis` | `view_snapshot`, `face_on`, `edge_on` | 3-panel / single-panel 2D projections |

## Conventions

- Coordinates: `(N, 3)` ndarray, columns `(x, y, z)` in kpc
- Velocities: `(N, 3)` ndarray, columns `(vx, vy, vz)` in km/s
- Masses: `(N,)` ndarray, in M_sun
- Spherical: `(r, phi, theta)`, theta = colatitude from +Z
- Cylindrical: `(R, phi, z)`
- PartType: 1=halo, 2=disk, 3=bulge, 4=gas
