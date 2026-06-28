"""
vis.py — Visualization tools for galaxy simulation snapshots.

Provides:
- view_snapshot: 3-panel (face-on, edge-on, side-on) projections
- face_on: single face-on projection
- edge_on: single edge-on projection
"""

import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import binned_statistic_2d
from typing import Optional


def _log_norm_matrix(matrix: np.ndarray) -> np.ndarray:
    """Log-normalize a 2D matrix for display."""
    mat = matrix.copy()
    mask = mat < 1
    mat[mask] = 1
    mat = np.log10(mat)
    mat[mask] = np.nan
    return mat


def _bin_2d_image(
    x: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    size: float,
    binNum: int,
) -> np.ndarray:
    """Create a 2D binned image."""
    image, _, _, _ = binned_statistic_2d(
        x=x, y=y, values=weights,
        range=[[-size, size], [-size, size]],
        bins=binNum,
        statistic="sum" if weights is not None else "count",
    )
    return image


def view_snapshot(
    coordinates: np.ndarray,
    masses: Optional[np.ndarray] = None,
    size: float = 20.0,
    binNum: int = 100,
    cmap: str = "inferno",
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = True,
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
) -> plt.Figure:
    """Three-panel projection: face-on (XY), edge-on (XZ), side-on (YZ).

    Parameters
    ----------
    coordinates : (N, 3) ndarray
        Cartesian positions.
    masses : (N,) ndarray or None
        Particle masses for surface density weighting.
    size : float
        Half-width of the field of view in kpc.
    binNum : int
        Number of pixels per side for XY panel.
    cmap : str
        Matplotlib colormap name.
    title : str
        Figure suptitle.
    save_path : str or None
        If provided, save figure to this path.
    show : bool
        If True, display the figure.
    vmin, vmax : float or None
        Colorbar range.

    Returns
    -------
    matplotlib.figure.Figure
    """
    ratio = 0.3  # edge-on panels thinner
    binNum_edge = int(binNum * ratio)

    if masses is None:
        weights = np.ones(len(coordinates))
    else:
        weights = masses

    fig = plt.figure(figsize=(18, 6))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, ratio, ratio],
                          wspace=0.02, hspace=0.02)

    ax_face = fig.add_subplot(gs[0])
    ax_edge = fig.add_subplot(gs[1])
    ax_side = fig.add_subplot(gs[2])

    # XY (face-on)
    im_xy = _bin_2d_image(coordinates[:, 1], coordinates[:, 0],
                          weights, size, binNum)
    im_xy = _log_norm_matrix(im_xy)

    # XZ (edge-on)
    im_xz = _bin_2d_image(coordinates[:, 2], coordinates[:, 0],
                          weights, size * ratio, binNum_edge)
    im_xz = _log_norm_matrix(im_xz)

    # YZ (side-on)
    im_yz = _bin_2d_image(coordinates[:, 1], coordinates[:, 2],
                          weights, size, binNum)
    im_yz = _log_norm_matrix(im_yz)

    # Shared color range
    all_valid = np.concatenate([
        im_xy[~np.isnan(im_xy)],
        im_xz[~np.isnan(im_xz)],
        im_yz[~np.isnan(im_yz)],
    ])
    if len(all_valid) == 0:
        all_valid = np.array([0.0, 1.0])
    if vmin is None:
        vmin = np.percentile(all_valid, 0.5)
    if vmax is None:
        vmax = np.percentile(all_valid, 99.5)

    # Face-on
    ax_face.imshow(im_xy, origin="lower", cmap=cmap,
                   vmin=vmin, vmax=vmax,
                   extent=[-size, size, -size, size])
    ax_face.set_xlabel("X [kpc]")
    ax_face.set_ylabel("Y [kpc]")

    # Edge-on
    ax_edge.imshow(im_xz, origin="lower", cmap=cmap,
                   vmin=vmin, vmax=vmax,
                   extent=[-size * ratio, size * ratio, -size, size])
    ax_edge.set_xlabel("Z [kpc]")
    ax_edge.set_ylabel("X [kpc]")
    ax_edge.yaxis.set_label_position("right")
    ax_edge.yaxis.tick_right()

    # Side-on
    ax_side.imshow(im_yz, origin="lower", cmap=cmap,
                   vmin=vmin, vmax=vmax,
                   extent=[-size, size, -size * ratio, size * ratio])
    ax_side.set_xlabel("Y [kpc]")
    ax_side.set_ylabel("Z [kpc]")
    ax_side.yaxis.set_label_position("right")
    ax_side.yaxis.tick_right()

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
    cmap: str = "inferno",
    title: str = "Face-on View",
    save_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """Single face-on (XY) projection.

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
    if masses is None:
        weights = np.ones(len(coordinates))
    else:
        weights = masses

    im = _bin_2d_image(coordinates[:, 1], coordinates[:, 0],
                       weights, size, binNum)
    im = _log_norm_matrix(im)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(im, origin="lower", cmap=cmap,
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
    cmap: str = "inferno",
    title: str = "Edge-on View",
    save_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """Single edge-on (XZ) projection.

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
    if masses is None:
        weights = np.ones(len(coordinates))
    else:
        weights = masses

    ratio = 0.3
    binNum_edge = int(binNum * ratio)

    im = _bin_2d_image(coordinates[:, 2], coordinates[:, 0],
                       weights, size * ratio, binNum_edge)
    im = _log_norm_matrix(im)

    fig, ax = plt.subplots(figsize=(6, 10))
    ax.imshow(im, origin="lower", cmap=cmap,
              extent=[-size * ratio, size * ratio, -size, size])
    ax.set_xlabel("Z [kpc]")
    ax.set_ylabel("X [kpc]")
    ax.set_title(title)

    if save_path:
        fig.savefig(save_path, bbox_inches="tight", dpi=150)
    if show:
        plt.show()
    else:
        plt.close(fig)

    return fig
