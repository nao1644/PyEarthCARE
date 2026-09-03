# PyEarthCARE

PyEarthCARE is a small Python toolkit for reading selected **EarthCARE Cloud Profiling Radar (CPR)** Level-2 products distributed by JAXA and ESA and plotting latitude-altitude cross sections of radar reflectivity and velocity-related quantities.

The current repository structure is:

```text
PyEarthCARE/
├── README.md
├── README_JP.md
├── lib/
│   └── PyEarthCARE.py
├── plot_jaxa_reflectivity.py
├── plot_jaxa_velocity.py
├── plot_esa_reflectivity.py
└── plot_esa_velocity.py
```

This repository is intended for research and visualization of EarthCARE CPR products. It is not official JAXA or ESA software.

[日本語版 README](README_JP.md)

## 1. Features

The current scripts can:

- read a single EarthCARE HDF5 file;
- select a latitude interval using `--lat-min` and `--lat-max`;
- plot one latitude-altitude cross section per input file;
- save the figure as a PNG file;
- handle selected JAXA and ESA CPR Level-2 products;
- switch between 1-km and 10-km JAXA variables where supported;
- select among several velocity-related variables with `--variable`.

The horizontal axis is **latitude** and the vertical axis is **altitude in km**.

The plotted x-axis range is slightly wider than the selected data interval:

```python
ax.set_xlim(lat_min - 0.03, lat_max + 0.03)
```

## 2. Supported products and variables

### 2.1 JAXA reflectivity

Script:

```text
plot_jaxa_reflectivity.py
```

Expected product:

```text
CPR_ECO
```

Supported variables:

| Option | HDF5 variable |
|---|---|
| `--resolution 1km` | `integrated_radar_reflectivity_1km` |
| `--resolution 10km` | `integrated_radar_reflectivity_10km` |

The default resolution is `1km`.

The reader uses:

```text
/ScienceData/Geo/latitude
/ScienceData/Geo/bin_height
/ScienceData/Data/integrated_radar_reflectivity_1km
```

or the corresponding `10km` reflectivity variable.

### 2.2 JAXA velocity-related variables

Script:

```text
plot_jaxa_velocity.py
```

The default variable is:

```text
integrated_doppler_velocity
```

The resolution suffix is appended automatically. For example,

```bash
--variable integrated_doppler_velocity --resolution 1km
```

selects:

```text
integrated_doppler_velocity_1km
```

Available command-line variable names are:

| `--variable` value | Expected JAXA product | Height variable |
|---|---|---|
| `integrated_doppler_velocity` | `CPR_ECO` | `bin_height` |
| `cloud_air_velocity` | `CPR_CLP` | `height` |
| `cloud_terminal_velocity1` | `CPR_CLP` | `height` |
| `cloud_terminal_velocity2` | `CPR_CLP` | `height` |
| `total_cloud_terminal_velocity` | `CPR_CLP` | `height` |

Both `1km` and `10km` suffixes can be requested from the command line. The requested variable must actually exist in the input product.

For `integrated_doppler_velocity`, the script also reads the corresponding integrated radar reflectivity when available and masks velocity where reflectivity is below `-21 dBZ`.

The JAXA velocity plotting script follows the sign convention used in the source analysis notebooks and plots:

```python
plot_velocity = -1.0 * velocity
```

### 2.3 ESA reflectivity

Script:

```text
plot_esa_reflectivity.py
```

Expected product:

```text
CPR_FMR
```

Variable:

```text
reflectivity_corrected
```

The reader expects the following variables under `/ScienceData`:

```text
latitude
height
reflectivity_corrected
```

### 2.4 ESA velocity-related variables

Script:

```text
plot_esa_velocity.py
```

Expected product:

```text
CPR_CD
```

Default variable:

```text
doppler_velocity_best_estimate
```

Selectable variables are currently:

```text
doppler_velocity_best_estimate
sedimentation_velocity_best_estimate
doppler_velocity_integrated
```

Use `--variable` to select one of them. A selected variable must be present in the input file.

Unlike the JAXA velocity script, the ESA velocity script plots the sign stored in the ESA product without applying an additional sign reversal.

## 3. Requirements

The code uses Python syntax that requires **Python 3.10 or later**.

Required Python packages are:

```text
numpy
matplotlib
xarray
```

An xarray backend capable of opening the EarthCARE HDF5 files is also required. A typical installation is:

```bash
python3 -m pip install numpy matplotlib xarray h5netcdf h5py
```

Depending on the local environment and file encoding, another xarray-compatible HDF5/netCDF backend may be used.

## 4. Installation

Clone or download this repository and move to the repository directory.

```bash
git clone [<repository-url>](https://github.com/nao1644/PyEarthCARE)
cd PyEarthCARE
```

The plotting scripts import the shared reader from:

```text
lib/PyEarthCARE.py
```

No installation of the library as a Python package is currently required.

To check the available command-line options:

```bash
python3 plot_jaxa_reflectivity.py --help
python3 plot_jaxa_velocity.py --help
python3 plot_esa_reflectivity.py --help
python3 plot_esa_velocity.py --help
```

## 5. Usage

### 5.1 JAXA reflectivity: 1 km

```bash
python3 plot_jaxa_reflectivity.py \
    input_file.h5 \
    --output output_1km.png \
    --lat-min 36.0 \
    --lat-max 37.0 \
    --resolution 1km
```

### 5.2 JAXA reflectivity: 10 km

```bash
python3 plot_jaxa_reflectivity.py \
    input_file.h5 \
    --output output_10km.png \
    --lat-min 36.0 \
    --lat-max 37.0 \
    --resolution 10km
```

### 5.3 JAXA integrated Doppler velocity

```bash
python3 plot_jaxa_velocity.py \
    input_file.h5 \
    --output jaxa_velocity.png \
    --lat-min 36.0 \
    --lat-max 37.0 \
    --resolution 1km \
    --variable integrated_doppler_velocity
```

### 5.4 JAXA cloud air velocity

Use a JAXA `CPR_CLP` input file:

```bash
python3 plot_jaxa_velocity.py \
    input_file.h5 \
    --output jaxa_cloud_air_velocity.png \
    --lat-min 36.0 \
    --lat-max 37.0 \
    --resolution 1km \
    --variable cloud_air_velocity
```

### 5.5 ESA corrected reflectivity

```bash
python3 plot_esa_reflectivity.py \
    input_file.h5 \
    --output esa_reflectivity.png \
    --lat-min 36.0 \
    --lat-max 37.0
```

### 5.6 ESA Doppler velocity

```bash
python3 plot_esa_velocity.py \
    input_file.h5 \
    --output esa_velocity.png \
    --lat-min 36.0 \
    --lat-max 37.0 \
    --variable doppler_velocity_best_estimate
```

## 6. Common command-line options

| Option | Description |
|---|---|
| `input_file` | Input EarthCARE HDF5 file |
| `--output` | Output PNG filename/path |
| `--lat-min` | Minimum latitude included in the data selection |
| `--lat-max` | Maximum latitude included in the data selection |
| `--resolution` | JAXA variable resolution: `1km` or `10km` |
| `--variable` | Velocity-related variable to plot |
| `--dpi` | Figure resolution in dpi; default is 600 |

`--resolution` is used only by the JAXA scripts.  
`--variable` is used by the velocity scripts.

## 7. Plot settings

The current plotting scripts use the following common settings:

- one input file produces one figure;
- one figure contains one latitude-altitude panel;
- latitude is used as the horizontal coordinate;
- altitude is shown in km;
- default vertical plot range is approximately `-0.1` to `20.2 km`;
- output is saved as PNG;
- default output resolution is `600 dpi`.

The reflectivity scripts retain the original low-reflectivity treatment using a threshold of `-21 dBZ`.

The standard diverging velocity plot uses approximately `-3.6` to `3.6 m s-1`.

## 8. Library structure

`lib/PyEarthCARE.py` contains the common data-reading and preprocessing functions.

Main public reader functions:

```python
read_jaxa_reflectivity()
read_jaxa_velocity()
read_esa_reflectivity()
read_esa_velocity()
select_latitude_range()
```

The module also:

- checks input-file existence;
- checks required HDF5 variables;
- aligns arrays to `(profile, vertical_bin)`;
- handles one- or two-dimensional height arrays;
- applies the requested latitude selection;
- reports available variables when an expected variable is missing.

The plotting scripts contain figure-specific settings, labels, color maps, levels, and output handling.

## 9. Notes and limitations

- JAXA `integrated_doppler_velocity` is expected in `CPR_ECO`.
- JAXA cloud-velocity variables are expected in `CPR_CLP`.
- ESA corrected reflectivity is expected in `CPR_FMR`.
- ESA velocity-related variables are expected in `CPR_CD`.
- The scripts currently use latitude rather than along-track distance or time as the horizontal coordinate.

## 10. Recommended official references and data resources

The following additional official pages are useful for checking product definitions, current versions, release notes, and data access:

- JAXA EarthCARE product list:  
  https://www.eorc.jaxa.jp/EARTHCARE/data/prd_list_e.html
- JAXA EarthCARE documents, ATBDs, PDDs, and release notes:  
  https://www.eorc.jaxa.jp/EARTHCARE/document/doc_index_e.html
- JAXA G-Portal for Earth observation data search and download:  
  https://gportal.jaxa.jp/gpr/
- ESA Earth Online EarthCARE mission/data gateway:  
  https://earth.esa.int/eogateway/missions/earthcare

The following pages were specifically selected as core references for this repository:

- JAXA EarthCARE:  
  https://www.eorc.jaxa.jp/EARTHCARE/index_j.html
- ESA EarthCARE Product Handbook:  
  https://earthcarehandbook.earth.esa.int/
- JAXA A-Train introduction/monitoring page:  
  https://www.eorc.jaxa.jp/EARTHCARE/A-train/A-train_monitor_documents_j.html
