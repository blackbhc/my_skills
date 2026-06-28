"""
vis.py — Visualization tools for galaxy simulation snapshots.

Provides:
- view_snapshot: 3-panel (face-on, edge-on-XZ, edge-on-YZ) projections
- face_on: single face-on (XY) projection
- edge_on: 2-panel edge-on (XZ + YZ), X-axis aligned with face-on
"""

import numpy as np
from matplotlib import pyplot as plt
from typing import Optional, Tuple


def _hist2d_log(
    x: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    x_range: Tuple[float, float],
    y_range: Tuple[float, float],
    binNum: int,
) -> np.ndarray:
    """Build a log-normalised 2-D histogram for display.

    ``histogram2d(x, y)`` returns ``H[i, j]`` = value in x-bin *i*
    and y-bin *j*.  For ``imshow`` with ``origin="lower"`` we need
    columns ↔ y and rows ↔ x, so the image is **transposed** before
    return.
    """
    H, _, _ = np.histogram2d(x, y, bins=binNum,
                              range=[x_range, y_range],
                              weights=weights)
    # Remember empty bins before clamping
    mask_empty = H <= 0
    H = np.where(mask_empty, 1.0, H)
    H = np.log10(H)
    H = np.where(mask_empty, np.nan, H)
    return H.T  # columns=y, rows=x  →  imshow horizontal=y, vertical=x


def _shared_clim(*images: np.ndarray) -> Tuple[float, float]:
    """Return (vmin, vmax) covering the 0.5–99.5 percentile of all valid pixels."""
    all_vals = np.concatenate([im[np.isfinite(im)] for im in images])
    if len(all_vals) == 0:
        return 0.0, 1.0
    return float(np.percentile(all_vals, 0.5)), float(np.percentile(all_vals, 99.5))


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
) -> plt.Figure:
    """Three-panel projection: face-on (XY) | edge-on (XZ) | edge-on (YZ).

    All panels share the same X-axis direction: the face-on horizontal
    axis is *X*, and the first edge-on panel (XZ) also places *X* on
    the vertical axis so the two stay aligned.

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

    Returns
    -------
    matplotlib.figure.Figure
    """
    ratio = 0.3
    binNum_edge = max(int(binNum * ratio), 10)

    weights = (masses if masses is not None
               else np.ones(len(coordinates), dtype=np.float32))

    x, y, z = coordinates[:, 0], coordinates[:, 1], coordinates[:, 2]
    xy_range = (-size, size)
    z_range = (-size * ratio, size * ratio)

    im_xy = _hist2d_log(y, x, weights, xy_range, xy_range, binNum)
    im_xz = _hist2d_log(z, x, weights, z_range, xy_range, binNum_edge)
    im_yz = _hist2d_log(z, y, weights, z_range, xy_range, binNum_edge)

    auto_min, auto_max = _shared_clim(im_xy, im_xz, im_yz)
    if vmin is None:
        vmin = auto_min
    if vmax is None:
        vmax = auto_max

    fig = plt.figure(figsize=(18, 6))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, ratio, ratio],
                          wspace=0.02, hspace=0.02)

    # -- XY (face-on): horizontal=Y, vertical=X, label X↔Y flipped --
    ax_xy = fig.add_subplot(gs[0])
    ax_xy.imshow(im_xy, origin="lower", cmap=cmap, interpolation=interpolation, vmin=vmin, vmax=vmax,
                 extent=[-size, size, -size, size])
    ax_xy.set_xlabel("X [kpc]")
    ax_xy.set_ylabel("Y [kpc]")

    # -- XZ: horizontal=Z, vertical=X (X stays vertical, aligned with face-on) --
    ax_xz = fig.add_subplot(gs[1])
    ax_xz.imshow(im_xz, origin="lower", cmap=cmap, interpolation=interpolation, vmin=vmin, vmax=vmax,
                 extent=[-size * ratio, size * ratio, -size, size])
    ax_xz.set_xlabel("Z [kpc]")
    ax_xz.set_ylabel("X [kpc]")
    ax_xz.yaxis.set_label_position("right")
    ax_xz.yaxis.tick_right()

    # -- YZ: horizontal=Z, vertical=Y --
    ax_yz = fig.add_subplot(gs[2])
    ax_yz.imshow(im_yz, origin="lower", cmap=cmap, interpolation=interpolation, vmin=vmin, vmax=vmax,
                 extent=[-size * ratio, size * ratio, -size, size])
    ax_yz.set_xlabel("Z [kpc]")
    ax_yz.set_ylabel("Y [kpc]")
    ax_yz.yaxis.set_label_position("right")
    ax_yz.yaxis.tick_right()

    if title:
        fig.suptitle(title, fontsize=18)

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
    ax.set_title(title)

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

    # XY — horizontal=X, vertical=Y
    im_xy = _hist2d_log(y, x, weights, rng_xy, rng_xy, binNum)
    # XZ — horizontal=X, vertical=Z  (X aligned with XY)
    im_xz = _hist2d_log(z, x, weights, rng_z, rng_xy, binNum_z)
    # YZ — horizontal=Z, vertical=Y  (Y aligned with XY, Z with XZ)
    im_yz = _hist2d_log(z, y, weights, rng_z, rng_xy, binNum_z)

    vmin, vmax = _shared_clim(im_xy, im_xz, im_yz)

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

    # Top-right: YZ (end) — horizontal=Z, vertical=Y  (share Y with XY)
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

    # Bottom-left: XZ (side) — horizontal=X, vertical=Z  (share X with XY)
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

    fig.suptitle(title, fontsize=18, y=0.98)

    if save_path:
        fig.savefig(save_path, bbox_inches="tight", dpi=150)
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig
