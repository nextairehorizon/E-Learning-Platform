# NextAIRE - Air Quality Data Integration

This repository presents a structured teaching curriculum on the
data-integration pipeline used to assemble a machine-learning-ready
air-quality dataset for five Croatian cities: Zagreb, Split, Rijeka,
Osijek, and Zadar. Each part consists of a self-contained Jupyter
notebook supported by reusable Python helper modules.

The curriculum is divided into six parts. Although the parts build on
one another sequentially, every notebook is designed to execute
independently: if an upstream output is unavailable, the notebook
either synthesises a stand-in dataset or skips the affected section
without error.

| Part | Topic                                                                  |
| ---- | ---------------------------------------------------------------------- |
| 1    | [Satellite Data (CAMS PM₂.₅)](notebooks/part1_satellite_aq/README.md)  |
| 2    | [Reanalysis (ERA5 + CAMS)](notebooks/part2_reanalysis/README.md)       |
| 3    | [Temporal Harmonization](notebooks/part3_temporal/README.md)           |
| 4    | [Spatial Harmonization](notebooks/part4_spatial/README.md)             |
| 5    | [Auxiliary Datasets → Master](notebooks/part5_aux/README.md)           |
| 6    | [Dataset Export (CSV / Parquet / Excel)](notebooks/part6_packaging/README.md) |

---

## Repository layout

```
notebooks/
├── part1_satellite_aq/      satellite_reader.ipynb + README
├── part2_reanalysis/        reanalysis_reader.ipynb + README
├── part3_temporal/          time_harmonization.ipynb + README
├── part4_spatial/           spatial_harmonization.ipynb + README
├── part5_aux/               auxiliary_integration.ipynb + README
└── part6_packaging/         dataset_packaging.ipynb + README

scripts/
├── utils.py                 small shared helper (NetCDF / ZIP loader)
├── part1_satellite_aq/      CAMS + ERA5 downloads, Urban Atlas preparation, extractors
├── part2_reanalysis/        ERA5 / CAMS extractors and canonical writer
├── part3_temporal/          time_align, temporal_diagnostics
├── part4_spatial/           spatial_match, station_registry_builder
├── part5_aux/               aux_data_ingest (synth_*), aux_to_table, join_master_table, coverage_report
└── part6_packaging/         build helper only (the notebook inlines its export code)

data/
├── stations_example.csv     five Croatian air-quality monitoring stations
└── outputs/                 written by the notebooks as you run them
```

---

## Getting started

Install the project dependencies and launch the first notebook:

```bash
pip install -r requirements.txt
jupyter notebook notebooks/part1_satellite_aq/satellite_reader.ipynb
```

Each per-part README specifies the external datasets required, the
credentials needed to download them (ADS for Part 1, CDS for Part 2),
and the artefacts produced by the notebook.
