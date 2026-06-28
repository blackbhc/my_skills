# Galaxy Simulation Analyzer

A Python toolkit for analyzing N-body simulation snapshots of disk galaxies. Built on numpy, scipy, matplotlib, and h5py.

## Triggers

Use this skill when the user asks to:
- Analyze a galaxy simulation snapshot (.hdf5)
- Compute bar strength, buckling, m=2 Fourier modes
- Generate face-on / edge-on visualizations
- Fit disk scale length/height or Sersic profiles
- Transform coordinates (cartesian ↔ cylindrical ↔ spherical)
- Preprocess snapshots (recenter, disk alignment)

## Architecture

```
galaxy-simulation-analyzer/
├── SKILL.md
└── galaxy_analyzer/
    ├── __init__.py      # Master class GalaxyAnalyzer
    ├── io.py            # HDF5 snapshot I/O with PartType selection
    ├── coords.py        # Coordinate transformations
    ├── preprocess.py    # Recenter + disk alignment
    ├── profile.py       # Surface density & radial profiles
    ├── morphology.py    # Bar strength, m=2, buckling
    ├── structure.py     # Scale length/height, Sersic index
    └── vis.py           # Visualization (face-on, edge-on)
```

## Quick Start

```python
import sys
sys.path.append("/Users/chenbinhui/codes/my_skills/galaxy-simulation-analyzer/")
from galaxy_analyzer import GalaxyAnalyzer

ga = GalaxyAnalyzer()

# Load snapshot
data = ga.load_snapshot("snapshot.hdf5", part_types=[2])

# Preprocess: recenter + align disk
coords, vels = ga.preprocess_disk(
    data['PartType2']['Coordinates'],
    data['PartType2']['Velocities'],
    data['PartType2']['Masses'],
)

# Convert to cylindrical
cyl_pos, cyl_vel = ga.car2cyl(coords, vels)

# Compute bar strength
A2 = ga.A2(cyl_pos[:, 1], masses=data['PartType2']['Masses'])

# Face-on surface density profile
rs, sigma = ga.radial_profile_surface_density(coords, data['PartType2']['Masses'])

# Visualize
ga.view_snapshot(coords, size=20)
```

## Conventions

- **Coordinate arrays**: `np.ndarray` of shape `(N, 3)`, columns = `(x, y, z)` in kpc.
- **Velocity arrays**: `np.ndarray` of shape `(N, 3)`, columns = `(vx, vy, vz)` in km/s.
- **Mass arrays**: `np.ndarray` of shape `(N,)`, in M_sun.
- **Spherical coordinates**: `(r, phi, theta)` where `theta` = colatitude from +Z.
- **Cylindrical coordinates**: `(R, phi, z)`.
- **PartType convention**: 1=halo, 2=disk, 3=bulge, 4=gas (Gadget-style).
