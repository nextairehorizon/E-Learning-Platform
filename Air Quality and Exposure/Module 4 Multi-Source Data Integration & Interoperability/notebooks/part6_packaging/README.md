# Part 6 - Dataset Export

This module exports the integration-stage master dataset in three
interoperable formats, enabling a partner to consume the data
without re-executing the pipeline:

- **CSV** - human-readable and supported by virtually every tool.
- **Parquet** - typed, compressed, and efficient for column-pruned
  reads.
- **Excel** - a spreadsheet-friendly review copy.

[Parts 1](../part1_satellite_aq/README.md),
[2](../part2_reanalysis/README.md),
[3](../part3_temporal/README.md),
[4](../part4_spatial/README.md), and
[5](../part5_aux/README.md) produced a single merged dataset
(`master_long.csv` and `master_wide.csv`). Part 6 transforms that
dataset into a versioned export directory suitable for hand-off.

---

## Files

| File                                                          | Purpose                                                                                                  |
| ------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `scripts/part6_packaging/_build_part6_notebook.py`            | One-shot generator that produces the reader notebook. Build helper; not part of the teaching pipeline.   |
| `notebooks/part6_packaging/dataset_packaging.ipynb`           | Primary tutorial notebook. Execute the cells in sequence.                                                |
| `data/outputs/master_long.csv`                                | **Optional, from Part 5.** Loaded if present; otherwise a small stand-in is synthesised.                 |
| `data/outputs/master_wide.csv`                                | **Optional, from Part 5.** Same fallback applies.                                                        |
| `data/outputs/integrated_dataset_v0.1.0/`                     | Produced by the notebook — the partner-ready export directory.                                           |

After the notebook is executed, the export directory contains:

```
integrated_dataset_v0.1.0/
├── master_long.csv
├── master_long.parquet
├── master_long.xlsx
├── master_wide.csv
├── master_wide.parquet
└── master_wide.xlsx
```

---

## Setup procedure

### Step 1. Install dependencies

```bash
pip install -r requirements.txt
```

Two packages are optional and govern Parquet and Excel output:

- **`pyarrow`** — required for Parquet output. If it is not
  installed, the Parquet step is skipped with a notification and CSV
  and Excel outputs are still produced.
- **`openpyxl`** — required for Excel output. If it is not installed,
  the Excel step is skipped.

### Step 2. (Optional) Prepare upstream outputs

The notebook is **self-contained**: when Part 5 outputs are not
present, it synthesises a small master table on the fly so that the
export pipeline runs without any external downloads.

If Part 5 has already been completed, the notebook will detect
`data/outputs/master_long.csv` and `master_wide.csv` and package
those files — which is the realistic workflow.

### Step 3. Launch the notebook

```bash
jupyter notebook notebooks/part6_packaging/dataset_packaging.ipynb
```

Execute the cells in sequence.

---

## Extensions

- **Partitioned Parquet** for very large multi-year datasets:
  `df.to_parquet(path, partition_cols=["date"])` produces
  Hive-partitioned output that partners may read one day at a time.
- **NetCDF or Zarr** for native gridded data: when a downstream
  consumer requires the raw CAMS or ERA5 grids, write them to
  CF-compliant NetCDF or Zarr alongside the master.
- **Versioning.** Increment the export directory name
  (`integrated_dataset_v0.1.0` → `v0.1.1`) on every release; never
  overwrite an export that has already been shipped.
