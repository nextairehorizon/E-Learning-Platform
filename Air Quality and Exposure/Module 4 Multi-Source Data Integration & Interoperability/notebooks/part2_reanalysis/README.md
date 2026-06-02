# Part 2 - Reanalysis Data for Air Quality

This module combines **ERA5 meteorological reanalysis** with the
**CAMS PM₂.₅ analysis** produced in Part 1, yielding a single
machine-learning-ready predictor table for the five Croatian cities
(Zagreb, Split, Rijeka, Osijek, and Zadar).

---

## Learning objectives

Upon completion of this module, you will be able to:

1. Download and open the ZIP-bundled NetCDF files that the Climate
   Data Store delivers for ERA5.
2. Distinguish reanalysis data from direct observations and recognise
   the principal pitfalls (time-zone conventions, cadence,
   accumulated quantities, vertical levels).
3. Extract gridded values at station coordinates using both nearest-
   neighbour and bilinear interpolation, and compare the two methods.
4. Align the hourly ERA5 axis with the six-hourly CAMS axis.
5. Construct and save a joint predictor table indexed by
   `(time, location_id)`.

---

## Files

| File                                                    | Purpose                                                                                            |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `scripts/part1_satellite_aq/download_era5_data.py`      | Downloads ERA5 hourly single-level fields for Croatia from the Climate Data Store (CDS). Executed once. |
| `scripts/part2_reanalysis/reanalysis_extract_points.py` | Helper module: extracts values at station coordinates (nearest or bilinear) and aligns time axes.   |
| `scripts/part2_reanalysis/reanalysis_to_table.py`       | Helper module: saves the combined long-format CSV with a provenance sidecar.                        |
| `notebooks/part2_reanalysis/reanalysis_reader.ipynb`    | Primary tutorial notebook. Execute the cells in sequence once data preparation is complete.         |
| `data/era5_meteo_croatia.nc`                            | Produced by `download_era5_data.py` — ERA5 hourly fields for June 2024 over Croatia.                |
| `data/cams_pm25_croatia.nc`                             | **Required from Part 1** — produced by `scripts/part1_satellite_aq/download_cams_data.py`.          |
| `data/stations_example.csv`                             | Five Croatian air-quality monitoring stations (shared with Part 1).                                 |

---

## Setup procedure

### Step 1. Install dependencies

```bash
pip install -r requirements.txt
```

### Step 2. Complete Part 1 first (CAMS prerequisite)

The file `data/cams_pm25_croatia.nc` must exist before this notebook
can be executed. If you have not yet completed Part 1, run:

```bash
cd scripts/part1_satellite_aq
python download_cams_data.py
```

### Step 3. Configure CDS access (required for ERA5)

ERA5 is distributed through the **Climate Data Store (CDS)**, which
is a separate service from the **Atmosphere Data Store (ADS)** used
in Part 1. Each service has its own URL and access token.

1. Register an account at <https://cds.climate.copernicus.eu/>.
2. Navigate to **Your profile → Personal Access Token** and copy the
   token value.
3. Accept the dataset licence at
   <https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels>.
4. Provide the credentials. If `~/.cdsapirc` already points to ADS
   (from Part 1), supply the CDS credentials through environment
   variables instead to avoid a conflict:

   ```powershell
   setx CDSAPI_URL https://cds.climate.copernicus.eu/api
   setx CDSAPI_KEY PASTE-YOUR-CDS-TOKEN-HERE
   ```

   Open a new PowerShell session after running `setx`, because the
   variables take effect only in newly created sessions.

### Step 4. Download the ERA5 data

```bash
cd scripts/part1_satellite_aq
python download_era5_data.py
```

This produces `data/era5_meteo_croatia.nc` (1–2 MB).

### Step 5. Launch the notebook

```bash
jupyter notebook notebooks/part2_reanalysis/reanalysis_reader.ipynb
```

Execute the cells in sequence.

---

## Next

Continue with
[Part 3 — Temporal Harmonization](../part3_temporal/README.md) to
align the joint table on a single hourly index.
