---
name: galaxy-simulation-analyzer
description: |
  Python toolkit for analyzing N-body simulation snapshots of disk galaxies.
  Computes bar strength (m=2), buckling, B/P bulge, disk structure profiles,
  coordinate transforms, and visualization (face-on/edge-on/3-panel). Built on
  numpy, scipy, matplotlib, h5py.

  Use when: galaxy simulation analysis, N-body snapshot analysis, bar strength computation, disk galaxy analysis, galaxy morphology, Gadget snapshot, HDF5 snapshot analysis, Fourier m=2 analysis, buckling analysis, B/P bulge, disk scale length fitting, Sersic fitting, galaxy visualization, 星系模拟分析, 棒旋星系, 星系形态学, 傅里叶分析
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Find
  - Ls
---

# Galaxy Simulation Analyzer

## Purpose

Provide a unified Python API for analyzing N-body simulation snapshots of disk galaxies. Cover I/O, preprocessing, coordinate transforms, morphology (bar/buckling/B/P bulge), structure profiles, and visualization in a single toolkit. Agent should use this skill as a code reference and run analyses via Bash/Python, not reproduce the code inline.

## Scope

### What this skill does

- Load Gadget-style HDF5 snapshots with PartType selection
- Recenter snapshots (shrinking-sphere COM / most-bound particle) and align disk to +Z
- Convert coordinates between Cartesian, cylindrical, and spherical frames
- Compute bar strength via m=2 Fourier amplitude, bar phase angle, and radial A2 profile
- Detect buckling events and B/P bulge strength
- Fit exponential disk scale length/height and Sersic index
- Generate face-on, edge-on, and 3-panel visualizations
- Provide a single `GalaxyAnalyzer` class as the unified interface

### What this skill does NOT do

- Does not run N-body simulations (use Gadget, Arepo, Gizmo, etc.)
- Does not perform cosmological analysis (halo finders, merger trees)
- Does not generate initial conditions
- Does not provide advanced statistical inference or MCMC fitting
- Does not replace dedicated visualization software (e.g., yt, pynbody) for general use

## Use When

### Trigger conditions

- User asks to analyze a galaxy simulation snapshot (.hdf5, Gadget-style)
- User needs bar strength, buckling, or B/P bulge metrics
- User wants face-on / edge-on / 3-panel visualizations of simulation data
- User needs disk scale length (Rd), scale height (Zd), or Sersic index fitting
- User needs coordinate transforms (Cartesian ↔ cylindrical ↔ spherical)
- User asks to preprocess a snapshot (recenter + disk alignment)
- User says "星系模拟分析", "分析这个快照", "计算棒强度", "棒旋星系傅里叶分析"

### Do NOT use when

- User just wants to view an existing plot/image (no computation needed)
- User needs cosmological context (halos, mergers, large-scale structure)
- User needs generic data exploration (use numpy/scipy directly)

## Dependencies

| Package   | Minimum | Used for                       |
|-----------|---------|--------------------------------|
| numpy     | 1.20    | Array ops, linear algebra      |
| scipy     | 1.7     | `binned_statistic_2d`, `curve_fit`, `linregress` |
| matplotlib| 3.5     | Visualization                  |
| h5py      | 3.0     | HDF5 snapshot I/O              |

Install with:

```bash
pip install numpy scipy matplotlib h5py
```

## Architecture

```
galaxy-simulation-analyzer/
├── SKILL.md
└── galaxy_analyzer/
    ├── __init__.py      # Master class GalaxyAnalyzer (unified API)
    ├── io.py            # HDF5 snapshot I/O with PartType selection
    ├── coords.py        # Cartesian ↔ Cylindrical ↔ Spherical transforms
    ├── preprocess.py    # Recenter (shrinking-sphere / most-bound) + disk alignment
    ├── profile.py       # Azimuthally averaged surface density & radial profiles
    ├── morphology.py    # Bar strength (m=2), buckling, B/P bulge
    ├── structure.py     # Disk scale length / height, Sersic index fitting
    └── vis.py           # Face-on, edge-on, and 3-panel projections
```

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| HDF5 snapshot path | ✅ | Path to Gadget-style .hdf5 file |
| PartType(s) | ❌ | Default auto-detect; specify `[1, 2]` etc. |
| Analysis parameters | ❌ | `Rmin`, `Rmax`, `binNum`, `size`, `threshold` etc. |

## Workflow

```text
1. Load snapshot → load_snapshot(path, part_types)
2. Preprocess     → preprocess_disk(...)  [recenter + align]
3. Transform      → car2cyl / car2sph / ...
4. Analyze        → A2 / getRdHz / fit_sersic / ...
5. Visualize      → view_snapshot / face_on / edge_on
```

## Quick Start

```python
from galaxy_analyzer import GalaxyAnalyzer

ga = GalaxyAnalyzer()

# 1. Load a snapshot (PartType 2 = disk stars)
data = ga.load_snapshot("snapshot.hdf5", part_types=[2])

# 2. Preprocess: recenter + align disk angular momentum to +Z
coords, vels = ga.preprocess_disk(
    data[2]["Coordinates"],
    data[2]["Velocities"],
    data[2]["Masses"],
    align_disk=True,
)

# 3. Convert to cylindrical coordinates
cyl_pos, cyl_vel = ga.car2cyl(coords, vels)

# 4. Compute bar strength (m=2 Fourier amplitude)
A2 = ga.A2(cyl_pos[:, 1], masses=data[2]["Masses"])

# 5. Face-on surface density profile
rs, sigma = ga.radial_profile_surface_density(coords, data[2]["Masses"])

# 6. Disk scale length and height
Rd, Zd = ga.getRdHz(data[2]["Masses"], coords)

# 7. Visualize
ga.view_snapshot(coords, masses=data[2]["Masses"], size=20)
```

## Module Summary

| Module | Key Functions | Description |
|--------|--------------|-------------|
| `io` | `load_snapshot`, `get_header_attrs` | Load Gadget-style HDF5 snapshots; auto-detects non-empty PartTypes |
| `coords` | `car2cyl`, `cyl2car`, `car2sph`, `sph2car`, `anisotropy` | Cartesian ↔ cylindrical ↔ spherical with velocity transforms |
| `preprocess` | `get_stable_center`, `get_most_bound_particle`, `get_principal_axes`, `align_disk`, `preprocess_disk` | Shrinking-sphere COM, most-bound center, +Z alignment via Rodrigues rotation |
| `profile` | `radial_profile_surface_density`, `radial_profile` | Azimuthally averaged profiles via `scipy.stats.binned_statistic_2d` |
| `morphology` | `A2`, `m2phase`, `A2profile`, `RbarThreshold`, `Sbuckling`, `BPXstrength`, `monotonize_bar_angle` | Bar, buckling, and B/P bulge analysis |
| `structure` | `getRdHz`, `fit_sersic` | Exponential scale length Rd & scale height Zd; Sersic n-index fitting |
| `vis` | `view_snapshot`, `face_on`, `edge_on` | Log-scaled 2D histograms; 3-panel or single projections |

## Conventions

| Array | Shape | Columns | Unit |
|-------|-------|---------|------|
| Coordinates | `(N, 3)` | `(x, y, z)` | kpc |
| Velocities | `(N, 3)` | `(vx, vy, vz)` | km/s |
| Masses | `(N,)` | — | M☉ |
| Cylindrical position | `(N, 3)` | `(R, φ, z)` | kpc |
| Cylindrical velocity | `(N, 3)` | `(V_R, V_φ, V_z)` | km/s |
| Spherical position | `(N, 3)` | `(r, φ, θ)` | kpc, rad, rad (θ = colatitude from +Z) |
| Spherical velocity | `(N, 3)` | `(V_r, V_φ, V_θ)` | km/s |

**PartType convention** (Gadget-style):

| Type | Content |
|------|---------|
| 0 | Gas |
| 1 | Dark matter / halo |
| 2 | Disk stars |
| 3 | Bulge stars (if present) |
| 4 | Additional stars / gas |
| 5 | Boundary particles |

## Full API Reference

### I/O — `io.py`

```python
data = ga.load_snapshot("snap.hdf5", part_types=None)    # auto-detect
data = ga.load_snapshot("snap.hdf5", part_types=[1, 2])  # explicit
# Returns {part_type: {"Coordinates": ndarray, "Velocities": ndarray, ...}}

ga.get_header_attrs("snap.hdf5")  # dict of Header group attributes
ga.get_num_part("snap.hdf5")      # NumPart_ThisFile array
```

### Coordinates — `coords.py`

```python
cyl_pos = ga.car2cyl(coords)                     # (N, 3) cyldindrical
cyl_pos, cyl_vel = ga.car2cyl(coords, vels)      # with velocities
car_pos, car_vel = ga.cyl2car(cyl_pos, cyl_vel)  # inverse

sph_pos = ga.car2sph(coords)                     # (N, 3) spherical
car_pos, car_vel = ga.sph2car(sph_pos, sph_vel)  # inverse

beta = ga.anisotropy(V_r, V_phi, V_theta)        # orbital anisotropy
```

### Preprocessing — `preprocess.py`

```python
# Center via shrinking-sphere COM
center = ga.get_stable_center(coords, masses)

# Center via most-bound halo particle (recommended)
center = ga.get_most_bound_particle(halo_coords, halo_potential)

# Align disk angular momentum to +Z axis
coords_rot, vels_rot = ga.align_disk(coords, vels, masses)

# Full pipeline: recenter + optionally align
coords, vels = ga.preprocess_disk(coords, vels, masses,
                                   halo_data=data[1],   # uses halo most-bound
                                   align_disk=True,     # rotates L to +Z
                                   enclose_radius=100.0)
```

### Profiles — `profile.py`

```python
rs, sigma = ga.radial_profile_surface_density(coords, masses,
                                               Rmin=0.1, Rmax=20.0)

rs, profile = ga.radial_profile(coords, values, statistic="mean")
```

### Morphology — `morphology.py`

```python
A2 = ga.A2(phis, masses)                                      # bar strength
phi2 = ga.m2phase(phis, masses)                                # bar phase angle
A2s, Rcenters = ga.A2profile(phis, Rs, masses)                 # radial A2
Rbar = ga.RbarThreshold(phis, Rs, masses, threshold=1.0)       # bar radius
Sbuckle = ga.Sbuckling(phis, Zs, masses)                       # buckling
BP = ga.BPXstrength(Zs, masses)                                # B/P bulge
angles_unwrapped = ga.monotonize_bar_angle(bar_angles)          # unwrap time series
```

### Structure — `structure.py`

```python
Rd, Zd = ga.getRdHz(masses, coords, Rmin=0.1, Rmax=30.0)       # scale len/ht
n, n_err = ga.fit_sersic(Rs, surface_density)                   # Sersic index
```

### Visualization — `vis.py`

```python
fig = ga.view_snapshot(coords, masses, size=20, binNum=100)     # 3-panel
fig = ga.face_on(coords, masses, size=20, binNum=200)           # single face-on
fig = ga.edge_on(coords, masses, size=20, binNum=200)           # 3-view (2x2 grid)
```

All visualisation functions accept `cmap`, `title`, `save_path`, `vmin`/`vmax`,
and `show` arguments.

**Annotations** — add extra elements (lines, circles, text) to specific panels
via the `annotations` parameter::

    annotations = [
        {"panel": "face-on", "func": "plot",
         "args": ([-5, 5], [0, 0]),  # horizontal line at y=0
         "kwargs": {"color": "white", "linestyle": "--"}},
        {"panel": "side-on", "func": "axhline",
         "args": (0,), "kwargs": {"color": "cyan"}},
    ]
    ga.view_snapshot(coords, masses, annotations=annotations)

**Panel names:** ``"face-on"`` (XY), ``"side-on"`` (XZ), ``"end-on"`` (YZ).
All coordinates are in physical kpc — ``imshow`` with ``extent`` handles the
mapping to display pixels automatically.

**`phys2pixel`** — convert a physical coordinate to pixel index::

    from galaxy_analyzer.vis import phys2pixel
    pixel_x = phys2pixel(phys_x, size=20.0, binNum=200)   # 0 … 199

## Outputs

| Output | Format | Description |
|--------|--------|-------------|
| Analysis results | Python dict / ndarray | A2, Rd, Zd, Sersic n, bar phase angle, etc. |
| Plots | Matplotlib Figure | Face-on, edge-on, 3-panel; save to disk or display |
| Processed data | ndarray | Translated/rotated coordinates and velocities |

## Examples

### Example 1: Basic bar strength analysis

```
Input: "Analyze bar strength for snapshot_020.hdf5 using PartType 2"
Agent:
  → imports GalaxyAnalyzer
  → loads snapshot data[2]
  → preprocesses (recenter + align)
  → converts to cylindrical
  → computes A2
  → visualizes face-on
Output: A2 value + face-on plot
```

### Example 2: Full morphology pipeline

```
Input: "Give me Rd, Zd, A2, and 3-panel view for this snapshot"
Agent:
  → same as above + getRdHz + view_snapshot(3-panel)
Output: Rd (kpc), Zd (kpc), A2, 3-panel plot saved to disk
```

## Limitations

- Requires snapshot in Gadget-style HDF5 format (not tipsy, ascii, binary)
- Particle mass resolution limits the smallest measurable bar amplitude (~0.01)
- Scale length/height fitting assumes axisymmetric exponential disk; deviations in strongly barred galaxies may bias results
- Visualization uses simple 2D histogram projections; no ray-tracing or dust rendering
- No built-in support for time-series analysis across multiple snapshots (user must loop externally)

## Checklist

Agent should verify after analysis:

**Input:**
- [ ] Snapshot path exists and is readable
- [ ] HDF5 file contains expected PartType groups
- [ ] Particle arrays have correct shapes (N, 3) or (N,)

**Preprocessing:**
- [ ] Disk correctly recentered (center ≈ 0 after transform)
- [ ] Disk angular momentum aligned to +Z (face-on view shows circular distribution)

**Analysis:**
- [ ] A2 computed at correct radial range (typically 0–2 scale lengths)
- [ ] Fit parameters (Rd, Sersic n) checked for physical reasonableness
- [ ] No NaN/inf in profile arrays

**Visualization:**
- [ ] Bin number appropriate for particle count
- [ ] Colormap clearly shows density structure
- [ ] Axes labeled with units
