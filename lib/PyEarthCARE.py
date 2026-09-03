#!/usr/bin/env python3
"""Shared EarthCARE CPR readers and array utilities.

This module contains the data-reading and common preprocessing logic used by
plot_jaxa_reflectivity.py, plot_jaxa_velocity.py, plot_esa_reflectivity.py,
and plot_esa_velocity.py.

The plotting scripts keep their own figure settings so users can modify color
scales, axis limits, and labels without changing the data-reading library.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import xarray as xr


# JAXA EarthCARE groups.
JAXA_GEO_GROUP = "/ScienceData/Geo"
JAXA_DATA_GROUP = "/ScienceData/Data"

# ESA EarthCARE group used by the supplied CPR notebooks.
ESA_SCIENCE_GROUP = "/ScienceData"

JAXA_RESOLUTIONS = ("1km", "10km")

JAXA_REFLECTIVITY_PRODUCT = "CPR_ECO"
JAXA_REFLECTIVITY_VARIABLES = {
    "1km": "integrated_radar_reflectivity_1km",
    "10km": "integrated_radar_reflectivity_10km",
}

# Base variable names are exposed to the command line. The resolution suffix
# is appended automatically when the HDF5 variable name is constructed.
JAXA_VELOCITY_VARIABLES = {
    "integrated_doppler_velocity": {
        "product": "CPR_ECO",
        "height": "bin_height",
        "style": "diverging",
    },
    "cloud_air_velocity": {
        "product": "CPR_CLP",
        "height": "height",
        "style": "diverging",
    },
    "cloud_terminal_velocity1": {
        "product": "CPR_CLP",
        "height": "height",
        "style": "diverging",
    },
    "cloud_terminal_velocity2": {
        "product": "CPR_CLP",
        "height": "height",
        "style": "diverging",
    },
    "total_cloud_terminal_velocity": {
        "product": "CPR_CLP",
        "height": "height",
        "style": "terminal",
    },
}

ESA_REFLECTIVITY_PRODUCT = "CPR_FMR"
ESA_REFLECTIVITY_VARIABLE = "reflectivity_corrected"

ESA_VELOCITY_PRODUCT = "CPR_CD"
ESA_VELOCITY_VARIABLES = (
    "doppler_velocity_best_estimate",
    "sedimentation_velocity_best_estimate",
    "doppler_velocity_integrated",
)
ESA_DEFAULT_VELOCITY_VARIABLE = "doppler_velocity_best_estimate"


def latitude_formatter(value: float, _position: float | None = None) -> str:
    """Format a latitude tick using N/S notation."""
    if value < 0:
        return f"{abs(value):.1f}°S"
    return f"{value:.1f}°N"


def _check_input_file(input_file: Path) -> None:
    """Raise an informative error if the input file does not exist."""
    if not input_file.is_file():
        raise FileNotFoundError(f"Input file not found: {input_file}")


def _validate_latitude(latitude: np.ndarray) -> np.ndarray:
    """Return latitude as a one-dimensional NumPy array."""
    latitude = np.asarray(latitude).squeeze()
    if latitude.ndim != 1:
        raise ValueError(
            "'latitude' must be one-dimensional after squeezing; "
            f"got shape {latitude.shape}."
        )
    return latitude


def _align_profile_bin_array(
    array: np.ndarray,
    n_profiles: int,
    name: str,
) -> np.ndarray:
    """Return a two-dimensional array with shape (profile, vertical_bin)."""
    array = np.asarray(array).squeeze()

    if array.ndim != 2:
        raise ValueError(
            f"{name!r} must be two-dimensional after squeezing; "
            f"got shape {array.shape}."
        )

    if array.shape[0] == n_profiles:
        return array

    if array.shape[1] == n_profiles:
        return array.T

    raise ValueError(
        f"Cannot match {name!r} shape {array.shape} to "
        f"{n_profiles} latitude profiles."
    )


def _prepare_height(
    height: np.ndarray,
    data_shape: tuple[int, int],
    height_name: str,
) -> np.ndarray:
    """Return height with the same two-dimensional shape as the data."""
    height = np.asarray(height).squeeze()

    if height.ndim == 1:
        if height.size != data_shape[1]:
            raise ValueError(
                f"One-dimensional {height_name!r} does not match the number "
                f"of vertical bins: {height.size} != {data_shape[1]}."
            )
        return np.broadcast_to(height[np.newaxis, :], data_shape)

    if height.ndim == 2:
        if height.shape == data_shape:
            return height
        if height.T.shape == data_shape:
            return height.T

    raise ValueError(
        f"Cannot match {height_name!r} shape {height.shape} "
        f"to data shape {data_shape}."
    )


def _require_variable(
    dataset: xr.Dataset,
    variable_name: str,
    group_name: str,
    product_name: str,
) -> None:
    """Check that a requested variable exists in an opened xarray dataset."""
    if variable_name not in dataset:
        available = ", ".join(sorted(dataset.variables))
        raise KeyError(
            f"{variable_name!r} is not found in {group_name}.\n"
            f"This reader expects an EarthCARE {product_name} file.\n"
            f"Available variables: {available}"
        )


def read_jaxa_reflectivity(
    input_file: Path,
    resolution: str = "1km",
) -> tuple[np.ndarray, np.ndarray, np.ndarray, str]:
    """Read JAXA CPR_ECO integrated radar reflectivity.

    Returns
    -------
    latitude, height, reflectivity, variable_name
        Latitude is one-dimensional. Height and reflectivity are aligned to
        shape ``(profile, vertical_bin)``. Height is returned in metres.
    """
    if resolution not in JAXA_REFLECTIVITY_VARIABLES:
        raise ValueError(
            f"Unsupported resolution {resolution!r}. "
            f"Choose from {JAXA_RESOLUTIONS}."
        )

    _check_input_file(input_file)
    variable_name = JAXA_REFLECTIVITY_VARIABLES[resolution]

    with xr.open_dataset(input_file, group=JAXA_GEO_GROUP) as geo_ds:
        _require_variable(
            geo_ds,
            "latitude",
            JAXA_GEO_GROUP,
            JAXA_REFLECTIVITY_PRODUCT,
        )
        _require_variable(
            geo_ds,
            "bin_height",
            JAXA_GEO_GROUP,
            JAXA_REFLECTIVITY_PRODUCT,
        )
        latitude = _validate_latitude(geo_ds["latitude"].values)
        height = np.asarray(geo_ds["bin_height"].values)

    with xr.open_dataset(input_file, group=JAXA_DATA_GROUP) as data_ds:
        _require_variable(
            data_ds,
            variable_name,
            JAXA_DATA_GROUP,
            JAXA_REFLECTIVITY_PRODUCT,
        )
        reflectivity = np.asarray(data_ds[variable_name].values)

    reflectivity = _align_profile_bin_array(
        reflectivity,
        n_profiles=latitude.size,
        name=variable_name,
    ).astype(float, copy=False)

    height = _prepare_height(
        height,
        data_shape=reflectivity.shape,
        height_name="bin_height",
    ).astype(float, copy=False)

    return latitude, height, reflectivity, variable_name


def read_jaxa_velocity(
    input_file: Path,
    resolution: str = "1km",
    variable: str = "integrated_doppler_velocity",
) -> tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray | None,
    str,
    str,
    str,
]:
    """Read a JAXA CPR velocity-related variable.

    The selected resolution suffix is appended to ``variable`` automatically.
    For ``integrated_doppler_velocity``, the corresponding integrated radar
    reflectivity is also returned when it exists so the plotting script can
    apply the original -21 dBZ echo mask.

    Returns
    -------
    latitude, height, velocity, reflectivity, variable_name, product_name,
    style_name
        Height is returned in metres. ``reflectivity`` is ``None`` for
        variables that do not use the CPR_ECO echo mask.
    """
    if resolution not in JAXA_RESOLUTIONS:
        raise ValueError(
            f"Unsupported resolution {resolution!r}. "
            f"Choose from {JAXA_RESOLUTIONS}."
        )
    if variable not in JAXA_VELOCITY_VARIABLES:
        raise ValueError(
            f"Unsupported JAXA velocity variable {variable!r}. "
            f"Choose from {tuple(JAXA_VELOCITY_VARIABLES)}."
        )

    _check_input_file(input_file)

    config = JAXA_VELOCITY_VARIABLES[variable]
    product_name = str(config["product"])
    height_name = str(config["height"])
    style_name = str(config["style"])
    variable_name = f"{variable}_{resolution}"

    with xr.open_dataset(input_file, group=JAXA_GEO_GROUP) as geo_ds:
        _require_variable(
            geo_ds,
            "latitude",
            JAXA_GEO_GROUP,
            product_name,
        )
        _require_variable(
            geo_ds,
            height_name,
            JAXA_GEO_GROUP,
            product_name,
        )
        latitude = _validate_latitude(geo_ds["latitude"].values)
        height = np.asarray(geo_ds[height_name].values)

    reflectivity: np.ndarray | None = None
    with xr.open_dataset(input_file, group=JAXA_DATA_GROUP) as data_ds:
        _require_variable(
            data_ds,
            variable_name,
            JAXA_DATA_GROUP,
            product_name,
        )
        velocity = np.asarray(data_ds[variable_name].values)

        if variable == "integrated_doppler_velocity":
            reflectivity_name = f"integrated_radar_reflectivity_{resolution}"
            if reflectivity_name in data_ds:
                reflectivity = np.asarray(data_ds[reflectivity_name].values)

    velocity = _align_profile_bin_array(
        velocity,
        n_profiles=latitude.size,
        name=variable_name,
    ).astype(float, copy=False)

    height = _prepare_height(
        height,
        data_shape=velocity.shape,
        height_name=height_name,
    ).astype(float, copy=False)

    if reflectivity is not None:
        reflectivity_name = f"integrated_radar_reflectivity_{resolution}"
        reflectivity = _align_profile_bin_array(
            reflectivity,
            n_profiles=latitude.size,
            name=reflectivity_name,
        ).astype(float, copy=False)
        if reflectivity.shape != velocity.shape:
            raise ValueError(
                "Reflectivity and velocity shapes do not match: "
                f"{reflectivity.shape} != {velocity.shape}."
            )

    return (
        latitude,
        height,
        velocity,
        reflectivity,
        variable_name,
        product_name,
        style_name,
    )


def read_esa_reflectivity(
    input_file: Path,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, str]:
    """Read ESA CPR_FMR corrected radar reflectivity."""
    _check_input_file(input_file)

    with xr.open_dataset(input_file, group=ESA_SCIENCE_GROUP) as ds:
        for variable_name in (
            "latitude",
            "height",
            ESA_REFLECTIVITY_VARIABLE,
        ):
            _require_variable(
                ds,
                variable_name,
                ESA_SCIENCE_GROUP,
                ESA_REFLECTIVITY_PRODUCT,
            )

        latitude = _validate_latitude(ds["latitude"].values)
        height = np.asarray(ds["height"].values)
        reflectivity = np.asarray(ds[ESA_REFLECTIVITY_VARIABLE].values)

    reflectivity = _align_profile_bin_array(
        reflectivity,
        n_profiles=latitude.size,
        name=ESA_REFLECTIVITY_VARIABLE,
    ).astype(float, copy=False)

    height = _prepare_height(
        height,
        data_shape=reflectivity.shape,
        height_name="height",
    ).astype(float, copy=False)

    return latitude, height, reflectivity, ESA_REFLECTIVITY_VARIABLE


def read_esa_velocity(
    input_file: Path,
    variable_name: str = ESA_DEFAULT_VELOCITY_VARIABLE,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, str]:
    """Read an ESA CPR_CD velocity-related variable."""
    if variable_name not in ESA_VELOCITY_VARIABLES:
        raise ValueError(
            f"Unsupported ESA velocity variable {variable_name!r}. "
            f"Choose from {ESA_VELOCITY_VARIABLES}."
        )

    _check_input_file(input_file)

    with xr.open_dataset(input_file, group=ESA_SCIENCE_GROUP) as ds:
        for required_name in ("latitude", "height", variable_name):
            _require_variable(
                ds,
                required_name,
                ESA_SCIENCE_GROUP,
                ESA_VELOCITY_PRODUCT,
            )

        latitude = _validate_latitude(ds["latitude"].values)
        height = np.asarray(ds["height"].values)
        velocity = np.asarray(ds[variable_name].values)

    velocity = _align_profile_bin_array(
        velocity,
        n_profiles=latitude.size,
        name=variable_name,
    ).astype(float, copy=False)

    height = _prepare_height(
        height,
        data_shape=velocity.shape,
        height_name="height",
    ).astype(float, copy=False)

    return latitude, height, velocity, variable_name


def select_latitude_range(
    latitude: np.ndarray,
    height: np.ndarray,
    data: np.ndarray,
    lat_min: float,
    lat_max: float,
    auxiliary_data: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray | None]:
    """Select EarthCARE profiles between ``lat_min`` and ``lat_max``.

    ``height`` and ``data`` must already be aligned to
    ``(profile, vertical_bin)``. An optional auxiliary array with the same
    shape can be selected with the same latitude mask.
    """
    if lat_min >= lat_max:
        raise ValueError("--lat-min must be smaller than --lat-max.")

    latitude = _validate_latitude(latitude)
    height = np.asarray(height)
    data = np.asarray(data)

    if height.ndim != 2 or data.ndim != 2:
        raise ValueError("'height' and 'data' must be two-dimensional arrays.")
    if height.shape != data.shape:
        raise ValueError(
            f"Height and data shapes do not match: {height.shape} != {data.shape}."
        )
    if height.shape[0] != latitude.size:
        raise ValueError(
            "Latitude profile count does not match the data: "
            f"{latitude.size} != {height.shape[0]}."
        )

    if auxiliary_data is not None:
        auxiliary_data = np.asarray(auxiliary_data)
        if auxiliary_data.shape != data.shape:
            raise ValueError(
                "Auxiliary data shape does not match the primary data: "
                f"{auxiliary_data.shape} != {data.shape}."
            )

    selected = (
        np.isfinite(latitude)
        & (latitude >= lat_min)
        & (latitude <= lat_max)
    )

    if not np.any(selected):
        finite_lat = latitude[np.isfinite(latitude)]
        if finite_lat.size:
            data_range = (
                f"{finite_lat.min():.3f} to {finite_lat.max():.3f} degrees"
            )
        else:
            data_range = "no finite latitude values"
        raise ValueError(
            f"No EarthCARE profiles are present between {lat_min} and "
            f"{lat_max} degrees. File latitude range: {data_range}."
        )

    selected_auxiliary = None
    if auxiliary_data is not None:
        selected_auxiliary = auxiliary_data[selected, :]

    return (
        latitude[selected],
        height[selected, :],
        data[selected, :],
        selected_auxiliary,
    )
