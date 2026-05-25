# Part 3 - Temporal Harmonization and Alignment

This module places the **satellite** (CAMS PM₂.₅) and
**reanalysis** (ERA5 plus CAMS) outputs on a **single,
consistent time axis** together with **ground-station** observations.
The same five Croatian cities from the preceding parts are used:
Zagreb, Split, Rijeka, Osijek, and Zadar.

[Part 1](../part1_satellite_aq/README.md) introduced CAMS PM₂.₅
extraction. [Part 2](../part2_reanalysis/README.md) added ERA5
meteorology and built a joint reanalysis predictor table. Part 3 is
where every source receives a shared clock: UTC, hourly, period-start
labels, and a master `(time, location_id)` skeleton.

[Part 4](../part4_spatial/README.md) addresses the **spatial** side
— coordinate-reference-system checks and point-to-grid matching —
and consumes the long-format file produced by Part 3.

---

## Learning objectives

Upon completion of this module, you will be able to:

1. Standardise mixed time sources to **UTC**, handling daylight-saving
   transitions (spring-forward and fall-back) without silent
   hour-shifts.
2. Choose and document the **timestamp semantics** (period-start
   versus period-end) so that two datasets with the same label do not
   end up offset by an hour after a naïve join.
3. **Resample** minute-level sensor data to hourly resolution using
   the appropriate aggregation per quantity (mean for concentrations,
   sum for accumulations, maximum for peaks).
4. Construct a **master hourly index** — the Cartesian product
   `time × location_id` — and reindex every source onto it.
5. Produce **integration-stage diagnostics**: coverage, missingness
   by day, duplicates, and the largest time gaps.

---

## Files

| File                                                       | Purpose                                                                                |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `scripts/part3_temporal/time_align.py`                     | Reusable functions: `standardize_timezone`, `resample_to_hourly`, `build_master_index`, `align_to_master_index`, `to_wide`. |
| `scripts/part3_temporal/temporal_diagnostics.py`           | Reusable diagnostics: `coverage_by_source`, `missingness_by_day`, `find_duplicates`, `time_gap_report`, `summarize`. |
| `scripts/part3_temporal/_build_part3_notebook.py`          | One-shot generator that produces the reader notebook. Build helper; not part of the teaching pipeline. |
| `notebooks/part3_temporal/time_harmonization.ipynb`        | Primary tutorial notebook. Execute the cells in sequence.                              |
| `data/stations_example.csv`                                | Five Croatian air-quality monitoring stations (shared across all parts).               |
| `data/outputs/satellite_pm25_nearest.csv`                  | **From Part 1.** Read in Section 10 if present; otherwise skipped.                     |
| `data/outputs/reanalysis_features.csv`                     | **From Part 2.** Read in Section 11 if present; otherwise skipped.                     |
| `data/outputs/master_hourly_index.csv`                     | Produced by Section 13 — the empty `(time, location_id)` skeleton.                     |
| `data/outputs/aligned_long.csv`                            | Produced by Section 13 — every source and variable reindexed onto the master.          |

---

## Setup procedure

### Step 1. Install dependencies

```bash
pip install -r requirements.txt
```

No additional packages are required beyond those used in Parts 1 and
2; pandas and numpy are sufficient for the entire module.

### Step 2. (Optional) Refresh Part 1 and Part 2 outputs

Sections 3 to 9 of Part 3 are **self-contained**: the notebook
synthesises a realistic one-month, minute-level station dataset so
that time-zone handling, daylight saving, resampling, and master-
index construction can all be exercised without any additional
download.

Sections 10 and 11 consume Part 1 and Part 2 canonical CSVs if those
files exist. If you ran Parts 1 and 2 before the download window was
widened to the full month of June 2024, re-run the downloads and the
reader notebooks so that the CSVs reflect the new window:

```bash
python scripts/part1_satellite_aq/download_cams_data.py
python scripts/part1_satellite_aq/download_era5_data.py
```

Then re-execute `notebooks/part1_satellite_aq/satellite_reader.ipynb`
and `notebooks/part2_reanalysis/reanalysis_reader.ipynb`.

If either CSV is absent, the corresponding section is skipped
silently.

### Step 3. Launch the notebook

```bash
jupyter notebook notebooks/part3_temporal/time_harmonization.ipynb
```

Execute the cells in sequence.

---

## Next

Continue with
[Part 4 — Spatial Harmonization](../part4_spatial/README.md) to add
coordinate-reference-system checks, point-to-grid matching (nearest
neighbour, bilinear interpolation, or buffer mean), and the
location-registry build step.
