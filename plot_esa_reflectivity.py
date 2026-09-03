#!/usr/bin/env python3
"""Plot EarthCARE CPR corrected radar reflectivity from an ESA CPR_FMR file."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.colors import ListedColormap
import numpy as np

from lib.PyEarthCARE import (
    ESA_REFLECTIVITY_PRODUCT,
    latitude_formatter,
    read_esa_reflectivity,
    select_latitude_range,
)


REFLECTIVITY_LEVELS = np.linspace(-13.0, 23.0, 10)
REFLECTIVITY_TICKS = np.arange(-13.0, 27.0, 4.0)
LOW_REFLECTIVITY_THRESHOLD_DBZ = -21.0
ALTITUDE_MIN_KM = -0.1
ALTITUDE_MAX_KM = 20.2

_ALPHA = 0.6
REFLECTIVITY_COLORS = [
    [242 / 256, 242 / 256, 255 / 256, _ALPHA],
    [153 / 256, 203 / 256, 255 / 256, _ALPHA],
    [255 / 256, 255 / 256, 190 / 256, _ALPHA],
    [250 / 256, 245 / 256, 0 / 256, _ALPHA],
    [255 / 256, 200 / 256, 0 / 256, _ALPHA],
    [255 / 256, 140 / 256, 0 / 256, _ALPHA],
    [250 / 256, 90 / 256, 0 / 256, _ALPHA],
    [255 / 256, 20 / 256, 0 / 256, _ALPHA],
    [165 / 256, 0 / 256, 33 / 256, _ALPHA],
    [181 / 256, 0 / 256, 91 / 256, _ALPHA],
]

REFLECTIVITY_CMAP = ListedColormap(REFLECTIVITY_COLORS)
def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Plot a latitude-altitude cross section of EarthCARE CPR "
            "corrected radar reflectivity from an ESA CPR_FMR file."
        )
    )
    parser.add_argument("input_file", type=Path, help="Input ESA CPR_FMR HDF5 file.")
    parser.add_argument("--output", type=Path, required=True, help="Output PNG path.")
    parser.add_argument("--lat-min", type=float, required=True, help="Minimum latitude.")
    parser.add_argument("--lat-max", type=float, required=True, help="Maximum latitude.")
    parser.add_argument("--dpi", type=int, default=600, help="Output dpi (default: 600).")
    return parser.parse_args()


def make_plot(
    latitude: np.ndarray,
    height_m: np.ndarray,
    reflectivity: np.ndarray,
    variable_name: str,
    lat_min: float,
    lat_max: float,
    output_file: Path,
    dpi: int,
) -> None:
    """Create and save one latitude-altitude reflectivity figure."""
    height_km = height_m * 1.0e-3
    latitude_2d = np.broadcast_to(latitude[:, np.newaxis], reflectivity.shape)
    reflectivity = np.asarray(reflectivity, dtype=float)
    plot_mask = ~np.isfinite(reflectivity)
    plot_mask |= np.isfinite(reflectivity) & (reflectivity < LOW_REFLECTIVITY_THRESHOLD_DBZ)


    reflectivity_plot = np.ma.array(
        reflectivity,
        mask=plot_mask,
        copy=False,
    )

    fig, ax = plt.subplots(figsize=(6.0, 3.8), dpi=dpi)
    contour = ax.contourf(
        latitude_2d,
        height_km,
        reflectivity_plot,
        levels=REFLECTIVITY_LEVELS,
        cmap=REFLECTIVITY_CMAP,
        alpha=0.7,
        extend="both",
        zorder=20,
    )

    ax.set_xlim(lat_min - 0.03, lat_max + 0.03)
    ax.set_ylim(ALTITUDE_MIN_KM, ALTITUDE_MAX_KM)

    x_tick_start = np.ceil(lat_min * 2.0) / 2.0
    x_ticks = np.arange(x_tick_start, lat_max + 0.001, 0.5)
    y_major_ticks = np.arange(2.0, 20.1, 2.0)
    y_grid_ticks = np.arange(1.0, 20.1, 1.0)

    ax.set_xticks(x_ticks)
    ax.set_yticks(y_major_ticks)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(latitude_formatter))
    ax.tick_params(axis="both", labelsize=8)

    for x_value in x_ticks:
        ax.axvline(x_value, linestyle=":", linewidth=1.0, color="gray", alpha=0.4, zorder=30)
    for y_value in y_grid_ticks:
        ax.axhline(y_value, linestyle=":", linewidth=1.0, color="gray", alpha=0.4, zorder=30)

    ax.set_xlabel("Latitude", fontsize=10)
    ax.set_ylabel("Altitude (km)", fontsize=10)
    fig.suptitle(
        f"EarthCARE, {ESA_REFLECTIVITY_PRODUCT}: {variable_name}",
        fontsize=9,
        y=0.97,
    )

    fig.subplots_adjust(left=0.10, right=0.86, bottom=0.13, top=0.92)
    colorbar_ax = fig.add_axes([0.87, 0.13, 0.03, 0.79])
    colorbar = fig.colorbar(contour, cax=colorbar_ax, orientation="vertical", extend="both")
    colorbar.set_ticks(REFLECTIVITY_TICKS)
    colorbar.set_label("Reflectivity (dBZ)", fontsize=10)
    colorbar.ax.tick_params(labelsize=8)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_file)
    plt.close(fig)


def main() -> None:
    """Entry point for command-line execution."""
    args = parse_args()

    latitude, height, reflectivity, variable_name = read_esa_reflectivity(
        input_file=args.input_file,
    )
    latitude, height, reflectivity, _ = select_latitude_range(
        latitude=latitude,
        height=height,
        data=reflectivity,
        lat_min=args.lat_min,
        lat_max=args.lat_max,
    )

    make_plot(
        latitude=latitude,
        height_m=height,
        reflectivity=reflectivity,
        variable_name=variable_name,
        lat_min=args.lat_min,
        lat_max=args.lat_max,
        output_file=args.output,
        dpi=args.dpi,
    )

    print(f"Input:      {args.input_file}")
    print(f"Product:    {ESA_REFLECTIVITY_PRODUCT}")
    print(f"Variable:   {variable_name}")
    print(f"Latitude:   {args.lat_min:.3f} to {args.lat_max:.3f} degrees")
    print(f"Output:     {args.output}")


if __name__ == "__main__":
    main()
