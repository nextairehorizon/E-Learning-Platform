# Part 1 — Satellite Data for Air Quality

This module introduces real satellite-derived air-quality
data obtained from the **Copernicus Atmosphere Data Store (ADS)**.
The material focuses on **PM₂.₅ (particulate matter smaller than 2.5
µm)** over **Croatia**, covering five cities: Zagreb, Split, Rijeka,
Osijek, and Zadar. 

---

## Learning objectives

Upon completion of this module, you will be able to:

1. Open a satellite or atmospheric NetCDF file and interpret its
   contents (dimensions, coordinates, variables, attributes).
2. Identify and select the variable of interest within a dataset.
3. Visualise the data on a map.
4. Extract pixel values at the coordinates of ground-monitoring
   stations using two distinct methods.
5. Save the extracted data as a canonical long-format CSV file
   suitable for downstream integration.

---

## Files

| File                                                     | Purpose                                                                                  |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `scripts/part1_satellite_aq/download_cams_data.py`       | Downloads the CAMS PM₂.₅ NetCDF grid for Croatia from ADS. Executed once.                |
| `scripts/part1_satellite_aq/download_era5_data.py`       | Downloads ERA5 meteorological reanalysis for Croatia from CDS. Executed once.            |
| `scripts/part1_satellite_aq/prepare_urban_atlas.py`      | Extracts the Urban Atlas FGB from a manually-downloaded ZIP archive (see Step 4 below).  |
| `scripts/part1_satellite_aq/satellite_extract_points.py` | Helper module: extracts pixel values at station coordinates (nearest pixel or N-km buffer mean). |
| `scripts/part1_satellite_aq/satellite_to_table.py`       | Helper module: converts extracted data to canonical long-format CSV with a metadata sidecar. |
| `notebooks/part1_satellite_aq/satellite_reader.ipynb`    | Primary tutorial notebook. Execute the cells in sequence once data preparation is complete. |
| `data/stations_example.csv`                              | Five Croatian air-quality monitoring stations.                                            |
| `data/cams_pm25_croatia.nc`                              | Produced by `download_cams_data.py` — the CAMS PM₂.₅ NetCDF grid.                         |
| `data/era5_meteo_croatia.nc`                             | Produced by `download_era5_data.py` — ERA5 hourly meteorology grid.                       |
| `data/*.fgb`                                             | Produced by `prepare_urban_atlas.py` — the Urban Atlas FGB for Zagreb.                    |

---

## Setup procedure

### Step 1. Install dependencies

```bash
pip install -r requirements.txt
```

### Step 2. Configure ADS access (required for CAMS data)

1. Register an account at <https://ads.atmosphere.copernicus.eu/>.
2. Navigate to **Your profile → Personal Access Token** and copy the
   token value.
3. Create a `~/.cdsapirc` file (on Windows, `C:\Users\<you>\.cdsapirc`)
   with the following contents:

   ```
   url: https://ads.atmosphere.copernicus.eu/api
   key: PASTE-YOUR-TOKEN-HERE
   ```

4. Accept the dataset licence at
   <https://ads.atmosphere.copernicus.eu/datasets/cams-europe-air-quality-forecasts>.
   This step is required only once.

### Step 3. Download the CAMS data

```bash
cd scripts/part1_satellite_aq
python download_cams_data.py
```

This command produces `data/cams_pm25_croatia.nc` (a small file of a
few megabytes, typically ready in under a minute).

### Step 4. Prepare the Urban Atlas data (required for Section 12)

The Urban Atlas dataset cannot be downloaded programmatically; a
browser session is required. Proceed as follows:

1. Log in at <https://land.copernicus.eu/en/user-corner/my-account>.
   A free Copernicus account is required.
2. Search for **"Urban Atlas Land Cover/Land Use 2021"** and select
   the Zagreb FGB tile:
   `CLMS_UA_LCU_S2021_V025ha_HR001L2_GRAD_ZAGREB_03035_V01_R01_20250321`
   (FGB format, approximately 192 MB).
3. Submit the download request. CLMS will send an e-mail when the
   ZIP archive is ready.
4. Download the archive (any filename, any location), then run:

   ```bash
   python scripts/part1_satellite_aq/prepare_urban_atlas.py --zip C:\path\to\downloaded.zip
   ```

   Use the optional `--out DIR` argument to save the FGB to a
   location other than `../data/`.

   The script handles the ZIP-inside-a-ZIP structure produced by CLMS
   and creates
   `data/CLMS_UA_LCU_S2021_V025ha_HR001L2_GRAD_ZAGREB_03035_V01_R01_20250321.fgb`.

### Step 5. Launch the notebook

```bash
jupyter notebook notebooks/part1_satellite_aq/satellite_reader.ipynb
```

Execute the cells in sequence.

---

## Data sources

**CAMS PM₂.₅** — Copernicus Atmosphere Monitoring Service, European
Air Quality Forecasts (analysis stream). Resolution: 0.1°
(approximately 10 km), hourly, surface concentrations in µg/m³. The
product combines Sentinel-5P TROPOMI observations, EU ground-station
reports, and a chemistry-transport model. The archive covers the
preceding three years on a rolling basis and is freely available with
an ADS account.
<https://ads.atmosphere.copernicus.eu/datasets/cams-europe-air-quality-forecasts>

**Copernicus Urban Atlas 2021** — Copernicus Land Monitoring Service.
The Urban Atlas provides detailed land-use and land-cover polygons
for EU and EEA Functional Urban Areas. The format is FlatGeobuf
(FGB; approximately 192 MB for the Zagreb tile), and the
`code_2021` attribute encodes the land-cover class (for example,
11100 = Continuous urban fabric, 12100 = Industrial/commercial,
31000 = Forests).
<https://land.copernicus.eu/en/products/urban-atlas>

---

## Extensions: raw satellite products

CAMS is a combined product (satellite + model + ground stations). If
you require raw satellite aerosol or PM₂.₅ proxies, two alternatives
are available:

**Sentinel-5P TROPOMI (aerosol)** — The UV Aerosol Index is provided
in the `AER_AI` product. Level-2 files use named groups and must be
opened accordingly:

```python
xr.open_dataset(file, group="PRODUCT")
```

The full archive is hosted at <https://dataspace.copernicus.eu/>; the
product browser is searchable by the identifier
`S5P_OFFL_L2__AER_AI`.

**MODIS and VIIRS Aerosol Optical Depth (AOD)** — A widely used PM₂.₅
proxy provided as daily global 0.1° gridded files (MAIAC / VIIRS
AERDB). These products are available through the NASA LAADS DAAC at
<https://ladsweb.modaps.eosdis.nasa.gov/>.

In both cases the open → inspect → extract → save workflow is
identical to the procedure demonstrated in this notebook.

---

## Next

Continue with [Part 2 — Reanalysis](../part2_reanalysis/README.md) to
add ERA5 meteorological context and construct the joint predictor
table required by a machine-learning model.
