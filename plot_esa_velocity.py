#!/usr/bin/env python3
"""Plot EarthCARE CPR velocity-related products from an ESA CPR_CD file."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from lib.PyEarthCARE import (
    ESA_DEFAULT_VELOCITY_VARIABLE,
    ESA_VELOCITY_PRODUCT,
    ESA_VELOCITY_VARIABLES,
    latitude_formatter,
    read_esa_velocity,
    select_latitude_range,
)


VELOCITY_LEVELS = np.linspace(-3.6, 3.6, 200)
VELOCITY_TICKS = np.arange(-3.6, 4.4, 0.8)
ALTITUDE_MIN_KM = -0.1
ALTITUDE_MAX_KM = 20.2


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Plot a latitude-altitude cross section of an EarthCARE CPR "
            "velocity-related variable from an ESA CPR_CD file."
        )
    )
    parser.add_argument("input_file", type=Path, help="Input ESA CPR_CD HDF5 file.")
    parser.add_argument("--output", type=Path, required=True, help="Output PNG path.")
    parser.add_argument("--lat-min", type=float, required=True, help="Minimum latitude.")
    parser.add_argument("--lat-max", type=float, required=True, help="Maximum latitude.")
    parser.add_argument(
        "--variable",
        choices=ESA_VELOCITY_VARIABLES,
        default=ESA_DEFAULT_VELOCITY_VARIABLE,
        help=(
            "Velocity-related variable to plot "
            f"(default: {ESA_DEFAULT_VELOCITY_VARIABLE})."
        ),
    )
    parser.add_argument("--dpi", type=int, default=600, help="Output dpi (default: 600).")
    return parser.parse_args()


def make_plot(
    latitude: np.ndarray,
    height_m: np.ndarray,
    velocity: np.ndarray,
    variable_name: str,
    lat_min: float,
    lat_max: float,
    output_file: Path,
    dpi: int,
) -> None:
    """Create and save one latitude-altitude velocity figure."""
    height_km = height_m * 1.0e-3
    latitude_2d = np.broadcast_to(latitude[:, np.newaxis], velocity.shape)

    # ESA velocity is plotted with the sign stored in the product.
    velocity = np.where(np.isfinite(velocity), velocity, np.nan)

    fig, ax = plt.subplots(figsize=(6.0, 3.8), dpi=dpi)
    contour = ax.contourf(
        latitude_2d,
        height_km,
        velocity,
        levels=VELOCITY_LEVELS,
        cmap="RdBu",
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
    fig.suptitle(f"EarthCARE, {ESA_VELOCITY_PRODUCT}: {variable_name}", fontsize=9, y=0.97)

    fig.subplots_adjust(left=0.10, right=0.86, bottom=0.13, top=0.92)
    colorbar_ax = fig.add_axes([0.87, 0.13, 0.03, 0.79])
    colorbar = fig.colorbar(contour, cax=colorbar_ax, orientation="vertical", extend="both")
    colorbar.set_ticks(VELOCITY_TICKS)
    colorbar.set_label("Velocity (m/s)", fontsize=10)
    colorbar.ax.tick_params(labelsize=8)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_file)
    plt.close(fig)


def main() -> None:
    """Entry point for command-line execution."""
    args = parse_args()

    latitude, height, velocity, variable_name = read_esa_velocity(
        input_file=args.input_file,
        variable_name=args.variable,
    )
    latitude, height, velocity, _ = select_latitude_range(
        latitude=latitude,
        height=height,
        data=velocity,
        lat_min=args.lat_min,
        lat_max=args.lat_max,
    )

    make_plot(
        latitude=latitude,
        height_m=height,
        velocity=velocity,
        variable_name=variable_name,
        lat_min=args.lat_min,
        lat_max=args.lat_max,
        output_file=args.output,
        dpi=args.dpi,
    )

    print(f"Input:      {args.input_file}")
    print(f"Product:    {ESA_VELOCITY_PRODUCT}")
    print(f"Variable:   {variable_name}")
    print(f"Latitude:   {args.lat_min:.3f} to {args.lat_max:.3f} degrees")
    print(f"Output:     {args.output}")


if __name__ == "__main__":
    main()
