# Beijing Multi-Site Air-Quality Dataset

Hourly air-quality and meteorological observations from **12 monitoring stations** across Beijing, **1 March 2013 – 28 February 2017**. The `PRSA_` prefix comes from the journal where the dataset was introduced.

## Source

- **UCI Machine Learning Repository, ID 501** — https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data
- **Citation**: Zhang, S., Guo, B., Dong, A., He, J., Xu, Z., & Chen, S. X. (2017). *Cautionary tales on air-quality improvement in Beijing.* Proceedings of the Royal Society A, **473**(2205), 20170457. https://doi.org/10.1098/rspa.2017.0457

## File format

One CSV per station, one row per hour:

| Column | Description |
|---|---|
| `year`, `month`, `day`, `hour` | timestamp (Beijing local, UTC+8) |
| `PM2.5`, `PM10`, `SO2`, `NO2`, `CO`, `O3` | pollutant concentrations (µg/m³) |
| `TEMP`, `PRES`, `DEWP`, `RAIN` | temperature (°C), pressure (hPa), dew point (°C), rainfall (mm) |
| `wd`, `WSPM` | wind direction (16-point compass) and speed (m/s) |
| `station` | station name |

Missing values are encoded as `NA`.
