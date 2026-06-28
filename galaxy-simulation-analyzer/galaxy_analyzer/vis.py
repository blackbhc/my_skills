"""
vis.py - Visualization tools for galaxy simulation snapshots.

Provides:
- view_snapshot: 3-panel (face-on, edge-on-XZ, edge-on-YZ) projections
- face_on: single face-on (XY) projection
- edge_on: 2-panel edge-on (XZ + YZ), X-axis aligned with face-on
"""

import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import binned_statistic_2d
from typing import Optional, Tuple

def _hist2d_log(
    x: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    x_range: Tuple[float, float],
    y_range: Tuple[float, float],
    binNum: int,
    statistic: str = "sum",
) -> np.ndarray:
    """Build a log-normalised 2-D histogram for display.

    Convention: ``binned_statistic_2d(x, y, ...)`` returns
    ``stat[i, j]`` for points in x-bin *i*, y-bin *j*, so rows = *x*
    (Y axis of plot) and cols = *y* (X axis of plot).
    Returns the image directly (no transpose needed) for ``imshow``
    with ``origin="lower"``.

    Parameters
    ----------
    x : (N,) ndarray
        Data mapped to rows → Y axis of the image.
    y : (N,) ndarray
        Data mapped to columns → X axis of the image.
    weights : (N,) ndarray
        Values to aggregate (e.g. particle masses).
    x_range : (float, float)
        Physical range for *x* (Y axis).
    y_range : (float, float)
        Physical range for *y* (X axis).
    binNum : int
        Number of bins per axis (image will be ``binNum × binNum``).
    statistic : str
        Statistic passed to ``binned_statistic_2d``
        (``"sum"``, ``"mean"``, ``"std"``, etc.).
    """
    stat, _, _, _ = binned_statistic_2d(
        x, y, values=weights,
        statistic=statistic,
        bins=[binNum, binNum],
        range=[x_range, y_range],
    )
    # stat[i, j] = aggregate in (x-bin i, y-bin j)
    # rows = x (Y axis), cols = y (X axis) → directly usable by imshow
    mask_ok = stat > 0
    H_log = np.full_like(stat, np.nan, dtype=np.float64)
    H_log[mask_ok] = np.log10(stat[mask_ok])
    return H_log

def _shared_clim(*images: np.ndarray) -> Tuple[float, float]:
    """Return (vmin, vmax) covering the 0.5-99.5 percentile of all valid pixels."""
    all_vals = np.concatenate([im[np.isfinite(im)] for im in images])
    if len(all_vals) == 0:
        return 0.0, 1.0
    return float(np.percentile(all_vals, 0.5)), float(np.percentile(all_vals, 99.5))

def phys2pixel(phys, size, binNum):
    """Convert physical coordinate to pixel index for imshow with extent.

    imshow(origin='lower', extent=[-size, size, -size, size]) maps
    physical coordinate -size to pixel 0 and +size to pixel binNum-1.

    Parameters
    ----------
    phys : float
        Physical coordinate value (kpc).
    size : float
        Half-width of the field of view (kpc).
    binNum : int
        Number of pixels along this axis.

    Returns
    -------
    pixel : float
        Pixel coordinate in [0, binNum - 1].
    """
    return (phys + size) / (2.0 * size) * (binNum - 1.0)

def _apply_annotations(ax, annotations, panel):
    """Apply annotation commands to an axes.

    Each annotations entry is a dict::

        {
            "panel": "face-on",            # target panel
            "func": "plot",                # ax method name
            "args": ([x1, x2], [y1, y2]),  # positional args (physical coords)
            "kwargs": {"color": "red"},    # keyword args
        }

    All positional and keyword args use physical coordinates -
    imshow with extent handles the mapping to display coords automatically.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
    annotations : list of dict or None
    panel : str
        One of "face-on", "side-on", "end-on".
    """
    if not annotations:
        return
    for ann in annotations:
        if ann.get("panel") != panel:
            continue
        func_name = ann["func"]
        args = ann.get("args", ())
        kwargs = ann.get("kwargs", {})
        getattr(ax, func_name)(*args, **kwargs)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def view_snapshot(
    coordinates: np.ndarray,
    masses: Optional[np.ndarray] = None,
    size: float = 20.0,
    binNum: int = 100,
    cmap: str = "jet",
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
    interpolation: str = "none",
    annotations: Optional[list] = None,
) -> plt.Figure:
    """Three-view projection: face-on (XY) + end-on (YZ) + side-on (XZ).

    Layout (2x2 grid, bottom-right hidden for colorbar)::

        +--------+--------+
        |  XY    |  YZ    |    XY <-> YZ share Y axis (vertical)
        | face-on| end    |    XY <-> XZ share X axis (horizontal)
        +--------+--------+
        |  XZ    |        |
        | side   | (cbar) |
        +--------+--------+

    All three panels are mutually axis-aligned so the same physical
    direction maps to the same screen direction across adjacent panels.

    Parameters
    ----------
    coordinates : (N, 3) ndarray
        Cartesian positions (x, y, z) in kpc.
    masses : (N,) ndarray or None
        Particle masses.
    size : float
        Half-width of the face-on field of view (and vertical extent of
        edge-on panels) in kpc.
    binNum : int
        Number of pixels per side for the face-on panel.
    cmap : str
        Matplotlib colormap.
    title : str
        Figure suptitle.
    save_path : str or None
    show : bool
    vmin, vmax : float or None
    annotations : list of dict or None
        Annotations to draw on specific panels. Each dict::

            {"panel": "face-on", "func": "plot",
             "args": ([x1, x2], [y1, y2]), "kwargs": {"color": "red"}}

        ``panel`` one of ``"face-on"``, ``"side-on"``, ``"end-on"``;
        ``func`` is the axes method name; use physical coordinates.

    Returns
    -------
    matplotlib.figure.Figure
    """
    weights = (masses if masses is not None
               else np.ones(len(coordinates), dtype=np.float32))

    ratio = 0.3
    binNum_z = max(int(binNum * ratio), 10)
    rng_xy = (-size, size)
    rng_z = (-size * ratio, size * ratio)

    x, y, z = coordinates[:, 0], coordinates[:, 1], coordinates[:, 2]

    # XY - horizontal=X, vertical=Y
    im_xy = _hist2d_log(y, x, weights, rng_xy, rng_xy, binNum)
    # XZ - horizontal=X, vertical=Z  (X aligned with XY)
    im_xz = _hist2d_log(z, x, weights, rng_z, rng_xy, binNum_z)
    # YZ - horizontal=Z, vertical=Y  (Y aligned with XY, Z with XZ)
    im_yz = _hist2d_log(y, z, weights, rng_xy, rng_z, binNum_z)

    auto_vmin, auto_vmax = _shared_clim(im_xy, im_xz, im_yz)
    if vmin is None:
        vmin = auto_vmin
    if vmax is None:
        vmax = auto_vmax

    fig = plt.figure(figsize=(14, 14))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, ratio],
                          height_ratios=[1, ratio],
                          hspace=0.03, wspace=0.03)

    # Top-left: XY (face-on)
    ax_xy = fig.add_subplot(gs[0, 0])
    ax_xy.imshow(im_xy, origin="lower", cmap=cmap, interpolation=interpolation, vmin=vmin, vmax=vmax,
                 extent=[-size, size, -size, size])
    ax_xy.set_xlabel("X [kpc]")
    ax_xy.set_ylabel("Y [kpc]")
    ax_xy.text(0.03, 0.97, "Face-on (XY)", transform=ax_xy.transAxes,
               va="top", ha="left", fontsize=14, color="white",
               bbox=dict(boxstyle="round,pad=0.3", facecolor="black", alpha=0.5))

    # Top-right: YZ (end) - horizontal=Z, vertical=Y  (share Y with XY)
    ax_yz = fig.add_subplot(gs[0, 1], sharey=ax_xy)
    ax_yz.imshow(im_yz, origin="lower", cmap=cmap, interpolation=interpolation, vmin=vmin, vmax=vmax,
                 extent=[-size * ratio, size * ratio, -size, size])
    ax_yz.set_xlabel("Z [kpc]")
    ax_yz.set_ylabel("Y [kpc]")
    ax_yz.yaxis.set_label_position("right")
    ax_yz.yaxis.tick_right()
    ax_yz.text(0.03, 0.97, "End (YZ)", transform=ax_yz.transAxes,
               va="top", ha="left", fontsize=14, color="white",
               bbox=dict(boxstyle="round,pad=0.3", facecolor="black", alpha=0.5))

    # Bottom-left: XZ (side) - horizontal=X, vertical=Z  (share X with XY)
    ax_xz = fig.add_subplot(gs[1, 0], sharex=ax_xy)
    ax_xz.imshow(im_xz, origin="lower", cmap=cmap, interpolation=interpolation, vmin=vmin, vmax=vmax,
                 extent=[-size, size, -size * ratio, size * ratio])
    ax_xz.set_xlabel("X [kpc]")
    ax_xz.set_ylabel("Z [kpc]")
    ax_xz.text(0.03, 0.97, "Side (XZ)", transform=ax_xz.transAxes,
               va="top", ha="left", fontsize=14, color="white",
               bbox=dict(boxstyle="round,pad=0.3", facecolor="black", alpha=0.5))

    # Bottom-right: hidden (reserved for colorbar)
    ax_cb = fig.add_subplot(gs[1, 1])
    ax_cb.set_visible(False)

    # Horizontal colorbar above the face-on panel
    cbar_ax = fig.add_axes([
        ax_xy.get_position().x0,
        ax_xy.get_position().y1 + 0.01,
        ax_xy.get_position().width,
        0.015,
    ])
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation="horizontal")
    cbar.set_label(r"$\log_{10}\,\Sigma$" + "\n[M$_\odot$ / kpc$^2$]", fontsize=14, labelpad=-55)
    cbar.ax.xaxis.set_label_position("top")
    cbar.ax.xaxis.tick_top()

    # Ensure colorbar width matches face-on panel
    pos = ax_xy.get_position()
    cbar_ax.set_position([pos.x0, cbar_ax.get_position().y0,
                          pos.width, cbar_ax.get_position().height])

    _apply_annotations(ax_xy, annotations, "face-on")
    _apply_annotations(ax_xz, annotations, "side-on")
    _apply_annotations(ax_yz, annotations, "end-on")

    fig.suptitle(title, fontsize=18, y=0.98)

    if save_path:
        fig.savefig(save_path, bbox_inches="tight", dpi=150)
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig

def face_on(
    coordinates: np.ndarray,
    masses: Optional[np.ndarray] = None,
    size: float = 20.0,
    binNum: int = 200,
    cmap: str = "jet",
    title: str = "Face-on View",
    save_path: Optional[str] = None,
    show: bool = True,
    interpolation: str = "none",
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
    annotations: Optional[list] = None,
) -> plt.Figure:
    """Single face-on (XY) projection.

    Horizontal = X,  Vertical = Y.

    Parameters
    ----------
    coordinates : (N, 3) ndarray
    masses : (N,) ndarray or None
    size : float
    binNum : int
    cmap : str
    title : str
    save_path : str or None
    show : bool
    annotations : list of dict or None
        See :func:`view_snapshot`.

    Returns
    -------
    matplotlib.figure.Figure
    """
    weights = (masses if masses is not None
               else np.ones(len(coordinates), dtype=np.float32))
    rng = (-size, size)

    im = _hist2d_log(coordinates[:, 1], coordinates[:, 0],
                     weights, rng, rng, binNum)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(im, origin="lower", cmap=cmap, interpolation=interpolation,
              extent=[-size, size, -size, size])
    ax.set_xlabel("X [kpc]")
    ax.set_ylabel("Y [kpc]")
    ax.set_title(title, fontsize=18)

    _apply_annotations(ax, annotations, "face-on")

    if save_path:
        fig.savefig(save_path, bbox_inches="tight", dpi=150)
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig

def edge_on(
    coordinates: np.ndarray,
    masses: Optional[np.ndarray] = None,
    size: float = 20.0,
    binNum: int = 200,
    cmap: str = "jet",
    title: str = "Three-View Projection",
    save_path: Optional[str] = None,
    show: bool = True,
    interpolation: str = "none",
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
) -> plt.Figure:
    """Three-view projection: face-on (XY) + end-on (YZ) + side-on (XZ).

    Layout (2×2 grid, bottom-right empty):

        +--------+--------+
        |  XY    |  YZ    |    XY ↔ YZ share Y axis (vertical)
        | face-on| end    |    XY ↔ XZ share X axis (horizontal)
        +--------+--------+
        |  XZ    |        |
        | side   | (cbar) |
        +--------+--------+

    All three panels are mutually axis-aligned so the same physical
    direction maps to the same screen direction across adjacent panels.

    Parameters
    ----------
    coordinates : (N, 3) ndarray
    masses : (N,) ndarray or None
    size : float
        Half-width for the in-plane (X / Y) axes in kpc.
    binNum : int
        Number of pixels for the in-plane dimension.
    cmap : str
    title : str
    save_path : str or None
    show : bool

    Returns
    -------
    matplotlib.figure.Figure
    """
    weights = (masses if masses is not None
               else np.ones(len(coordinates), dtype=np.float32))

    ratio = 0.3
    binNum_z = max(int(binNum * ratio), 10)
    rng_xy = (-size, size)
    rng_z = (-size * ratio, size * ratio)

    x, y, z = coordinates[:, 0], coordinates[:, 1], coordinates[:, 2]

    # XY - horizontal=X, vertical=Y
    im_xy = _hist2d_log(y, x, weights, rng_xy, rng_xy, binNum)
    # XZ - horizontal=X, vertical=Z  (X aligned with XY)
    im_xz = _hist2d_log(z, x, weights, rng_z, rng_xy, binNum_z)
    # YZ - horizontal=Z, vertical=Y  (Y aligned with XY, Z with XZ)
    im_yz = _hist2d_log(y, z, weights, rng_xy, rng_z, binNum_z)

    auto_vmin, auto_vmax = _shared_clim(im_xy, im_xz, im_yz)
    if vmin is None:
        vmin = auto_vmin
    if vmax is None:
        vmax = auto_vmax

    fig = plt.figure(figsize=(14, 14))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, ratio],
                          height_ratios=[1, ratio],
                          hspace=0.03, wspace=0.03)

    # Top-left: XY (face-on)
    ax_xy = fig.add_subplot(gs[0, 0])
    ax_xy.imshow(im_xy, origin="lower", cmap=cmap, interpolation=interpolation, vmin=vmin, vmax=vmax,
                 extent=[-size, size, -size, size])
    ax_xy.set_xlabel("X [kpc]")
    ax_xy.set_ylabel("Y [kpc]")
    ax_xy.text(0.03, 0.97, "Face-on (XY)", transform=ax_xy.transAxes,
               va="top", ha="left", fontsize=14, color="white",
               bbox=dict(boxstyle="round,pad=0.3", facecolor="black", alpha=0.5))

    # Top-right: YZ (end) - horizontal=Z, vertical=Y  (share Y with XY)
    ax_yz = fig.add_subplot(gs[0, 1], sharey=ax_xy)
    ax_yz.imshow(im_yz, origin="lower", cmap=cmap, interpolation=interpolation, vmin=vmin, vmax=vmax,
                 extent=[-size * ratio, size * ratio, -size, size])
    ax_yz.set_xlabel("Z [kpc]")
    ax_yz.set_ylabel("Y [kpc]")
    ax_yz.yaxis.set_label_position("right")
    ax_yz.yaxis.tick_right()
    ax_yz.text(0.03, 0.97, "End (YZ)", transform=ax_yz.transAxes,
               va="top", ha="left", fontsize=14, color="white",
               bbox=dict(boxstyle="round,pad=0.3", facecolor="black", alpha=0.5))

    # Bottom-left: XZ (side) - horizontal=X, vertical=Z  (share X with XY)
    ax_xz = fig.add_subplot(gs[1, 0], sharex=ax_xy)
    ax_xz.imshow(im_xz, origin="lower", cmap=cmap, interpolation=interpolation, vmin=vmin, vmax=vmax,
                 extent=[-size, size, -size * ratio, size * ratio])
    ax_xz.set_xlabel("X [kpc]")
    ax_xz.set_ylabel("Z [kpc]")
    ax_xz.text(0.03, 0.97, "Side (XZ)", transform=ax_xz.transAxes,
               va="top", ha="left", fontsize=14, color="white",
               bbox=dict(boxstyle="round,pad=0.3", facecolor="black", alpha=0.5))

    # Bottom-right: hidden (reserved for colorbar)
    ax_cb = fig.add_subplot(gs[1, 1])
    ax_cb.set_visible(False)

    # Horizontal colorbar above the face-on panel
    cbar_ax = fig.add_axes([
        ax_xy.get_position().x0,
        ax_xy.get_position().y1 + 0.01,
        ax_xy.get_position().width,
        0.015,
    ])
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation="horizontal")
    cbar.set_label(r"$\log_{10}\,\Sigma$" + "\n[M$_\\odot$ / kpc$^2$]",
                   fontsize=14, labelpad=-55)
    cbar.ax.xaxis.set_label_position("top")
    cbar.ax.xaxis.tick_top()

    # Ensure colorbar width matches face-on panel
    pos = ax_xy.get_position()
    cbar_ax.set_position([pos.x0, cbar_ax.get_position().y0,
                          pos.width, cbar_ax.get_position().height])

    _apply_annotations(ax_xy, annotations, "face-on")
    _apply_annotations(ax_xz, annotations, "side-on")
    _apply_annotations(ax_yz, annotations, "end-on")

    fig.suptitle(title, fontsize=18, y=0.98)

    if save_path:
        fig.savefig(save_path, bbox_inches="tight", dpi=150)
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig
