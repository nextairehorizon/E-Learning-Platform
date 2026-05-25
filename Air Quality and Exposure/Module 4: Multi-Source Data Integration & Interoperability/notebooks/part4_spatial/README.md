# Part 4 - Spatial Harmonization

This module addresses the **spatial** dimension of the integration
stage: converting gridded fields (CAMS, ERA5) and contextual vector
layers (Urban Atlas, altitude, proximity indicators) into per-station
features on a defensible coordinate system, with an explicit mapping
method recorded for every value.

[Parts 1](../part1_satellite_aq/README.md) and
[2](../part2_reanalysis/README.md) extracted gridded data at the
stations using a single method choice;
[Part 3](../part3_temporal/README.md) placed every source on a shared
**time axis**. Part 4 completes the integration with the **spatial**
side, again using the five Croatian cities (Zagreb, Split, Rijeka,
Osijek, and Zadar).

---

## Learning objectives

Upon completion of this module, you will be able to:

1. Align point measurements with gridded satellite or reanalysis
   fields consistently, beginning with a **coordinate-reference-system
   (CRS) consistency check** that refuses to silently snap stations to
   the edge of a grid or zero-out coordinates after a projected join.
2. Choose a defensible **mapping method** on the basis of grid
   resolution and intended use: nearest neighbour, bilinear
   interpolation, or buffer mean.
3. Construct a documented **station registry** that records each
   site's `type` (background, traffic, industrial, and so on),
   sensor height, and free-text notes. The registry is the
   appropriate location for representativeness information (for
   example, urban-canyon effects or microenvironment notes).
4. Attach **contextual layers** (such as Urban Atlas land cover) to
   each station with a single CRS-aware spatial join.
5. Produce a single merged dataset indexed by
   `(time, location_id)` and ready for the modelling stage.

---

## Files

| File                                                          | Purpose                                                                                                          |
| ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `scripts/part4_spatial/spatial_match.py`                      | Reusable functions: `crs_check`, `nearest_grid_value`, `bilinear_grid_value`, `buffer_average`, `join_contextual_layer`. |
| `scripts/part4_spatial/station_registry_builder.py`           | Reusable functions: `build_registry`, `validate_registry`, `save_registry`, `load_registry`, `print_report`.      |
| `scripts/part4_spatial/_build_part4_notebook.py`              | One-shot generator that produces the reader notebook. Build helper; not part of the teaching pipeline.            |
| `notebooks/part4_spatial/spatial_harmonization.ipynb`         | Primary tutorial notebook. Execute the cells in sequence.                                                         |
| `data/stations_example.csv`                                   | Five Croatian air-quality monitoring stations (shared across all parts).                                          |
| `data/cams_pm25_croatia.nc`                                   | **Optional, from Part 1.** Used in Section 7 if present; otherwise skipped.                                       |
| `data/era5_meteo_croatia.nc`                                  | **Optional, from Part 2.** Used in Section 8 if present; otherwise skipped.                                       |
| `data/CLMS_UA_LCU_S2021_..._ZAGREB_..._20250321.fgb`          | **Optional, from Part 1 Section 12.** Used in Section 9 if present; otherwise skipped.                            |
| `data/outputs/aligned_long.csv`                               | **From Part 3.** Used in Section 10 to produce the final merged file.                                             |
| `data/outputs/station_registry.csv`                           | Produced by Section 3 — the validated registry.                                                                   |
| `data/outputs/spatial_temporal_long.csv`                      | Produced by Section 10 — a `(time, location_id)` table containing values and per-station context.                  |

---

## Setup procedure

### Step 1. Install dependencies

```bash
pip install -r requirements.txt
```

The function `spatial_match.join_contextual_layer` is the only
component that imports `geopandas`; the remaining helpers depend only
on pandas, xarray, and numpy. If the Urban Atlas join is not required,
geopandas may be omitted.

### Step 2. (Optional) Prepare upstream outputs

Sections 1 to 6 are **self-contained**: they construct the registry,
perform the CRS check, and demonstrate the three mapping methods on
a small synthetic grid.

Sections 7 and 8 consume the real CAMS and ERA5 NetCDF files
downloaded in Parts 1 and 2. If you have not yet completed those
parts, run:

```bash
python scripts/part1_satellite_aq/download_cams_data.py
python scripts/part1_satellite_aq/download_era5_data.py
```

Section 9 (Urban Atlas) uses the FlatGeobuf prepared in Part 1
Section 12. If the file is not present, the section prints a polite
notification and is skipped.

Section 10 (final merge) uses the file `aligned_long.csv` produced
by Part 3. If Part 3 has not yet been completed, run it first:

```bash
jupyter notebook notebooks/part3_temporal/time_harmonization.ipynb
```

### Step 3. Launch the notebook

```bash
jupyter notebook notebooks/part4_spatial/spatial_harmonization.ipynb
```

Execute the cells in sequence.

---

## Next

Continue with
[Part 5 — Auxiliary Data Integration](../part5_aux/README.md) to add
the third pillar of predictors (traffic counters, station-collocated
meteorology, energy intensity, land use) to the master table.
