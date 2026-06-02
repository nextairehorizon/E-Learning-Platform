# Part 5 - Auxiliary Datasets Integration

This module folds **auxiliary predictors** - traffic counters,
station-collocated meteorology, and static spatial context - into the
canonical schema used for the air-quality, satellite, and reanalysis
streams. The output of this module is a single **model-ready master
dataset**.

[Parts 1](../part1_satellite_aq/README.md) and
[2](../part2_reanalysis/README.md) produced the satellite (CAMS
PM₂.₅) and reanalysis (ERA5 plus CAMS) tables.
[Part 3](../part3_temporal/README.md) placed every source on a shared
time axis. [Part 4](../part4_spatial/README.md) added CRS-aware
spatial matching and per-station context. Part 5 brings every
remaining auxiliary feed under the same treatment and produces the
**final** output of the integration stage: one merged dataset indexed
by `(time, location_id)`, containing both the air-quality targets and
the predictor variables.

The guiding principle: **the integration stage prepares structure;
it does not make modelling decisions.** No lag features are selected,
no predictors are discarded, and no train/test split is taken at
this stage. Those decisions belong to the modelling notebook.

---

## Learning objectives

Upon completion of this module, you will be able to:

1. Convert any auxiliary dataset (traffic counts, station meteo,
   energy use, static context) into the project's canonical
   long-format schema using a declarative **DatasetContract** that
   specifies required columns, units, version tag, and source label.
2. Align auxiliary predictors in time and space with the
   air-quality, satellite, and reanalysis backbone established in
   Parts 1 to 4.
3. Produce a single merged **model-ready** dataset
   (`master_wide.csv`), together with a **predictor-readiness**
   report that flags sparse features without discarding them
   silently.

---

## Files

| File                                                          | Purpose                                                                                                            |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `scripts/part5_aux/aux_data_ingest.py`                        | Synthetic data factories (`synth_traffic`, `synth_station_meteo`, `synth_static_context`) used by the teaching notebook. |
| `scripts/part5_aux/aux_to_table.py`                           | `DatasetContract`, `validate_contract`, `to_canonical_long`. Pre-defined contracts for traffic, station meteorology, and static context. |
| `scripts/part5_aux/join_master_table.py`                      | `stack_sources`, `to_model_ready`, `add_lag_features`.                                                              |
| `scripts/part5_aux/coverage_report.py`                        | `coverage_by_source_variable`, `coverage_by_station_variable`, `predictor_readiness`, `summarize`, `print_summary`. |
| `scripts/part5_aux/_build_part5_notebook.py`                  | One-shot generator that produces the reader notebook. Build helper; not part of the teaching pipeline.              |
| `notebooks/part5_aux/auxiliary_integration.ipynb`             | Primary tutorial notebook. Execute the cells in sequence.                                                           |
| `data/stations_example.csv`                                   | Five Croatian air-quality monitoring stations (shared across all parts).                                            |
| `data/outputs/station_registry.csv`                           | **Optional, from Part 4.** Used if present; otherwise `stations_example.csv` is used as a fallback.                 |
| `data/outputs/master_hourly_index.csv`                        | **Optional, from Part 3.** Used if present; otherwise the notebook constructs a local hourly skeleton for June 2024. |
| `data/outputs/aligned_long.csv`                               | **Optional, from Part 3.** When present, its rows are folded into the master long table.                            |
| `data/outputs/master_long.csv`                                | Produced by Section 10 — every source stacked into canonical long format.                                           |
| `data/outputs/master_wide.csv`                                | Produced by Section 10 — the model-ready wide table, sorted by `(location_id, time)`.                               |
| `data/outputs/master_wide.meta.txt`                           | Produced by Section 10 — provenance sidecar (variables, units, dataset versions).                                   |

---

## Setup procedure

### Step 1. Install dependencies

```bash
pip install -r requirements.txt
```

No additional dependencies are required beyond those used in Parts
1 to 4; pandas and numpy are sufficient.

### Step 2. (Optional) Prepare upstream outputs

The notebook is **fully self-contained**: it synthesises traffic,
station-meteo, and static-context datasets on the fly, allowing the
entire pipeline to run without any external downloads.

If Parts 3 and 4 have already been completed, the notebook will
detect their canonical CSV outputs
(`master_hourly_index.csv`, `aligned_long.csv`,
`station_registry.csv`) and incorporate them into the master table.
Any missing file is skipped silently.

### Step 3. Launch the notebook

```bash
jupyter notebook notebooks/part5_aux/auxiliary_integration.ipynb
```

Execute the cells in sequence.

---

## Extensions

- **Adding a new feed.** Copy one of the three contracts in
  `aux_to_table.py`, list the new columns, units, and version, and
  pass the resulting long-format frame into `stack_sources` together
  with the other sources. No change to the join code is required.
- **Sub-hourly auxiliary feeds.** Resample first with
  `time_align.resample_to_hourly` from Part 3, then submit the
  result to the Part 5 pipeline.
- **Non-collocated auxiliary feeds.** If a traffic counter is not
  collocated with an air-quality station, attach the counter to its
  nearest air-quality station(s) using
  `spatial_match.join_contextual_layer` from Part 4 (or
  `gpd.sjoin_nearest` directly) before calling `to_canonical_long`.
- **Predictor-readiness thresholds.** The defaults
  (`ready_min=0.85`, `borderline_min=0.50`) are suitable for a
  one-month hourly window. Adjust them according to the amount of
  imputation that the modelling stage is willing to accept.

---

## Next

Continue with [Part 6 — Dataset Export](../part6_packaging/README.md)
to package the master dataset for partner reuse in CSV, Parquet, and
Excel formats.
