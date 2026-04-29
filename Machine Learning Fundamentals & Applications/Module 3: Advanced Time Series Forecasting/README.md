# Module 3 — Advanced Time Series Forecasting

Sequence models for hourly air-quality forecasting on the **Beijing Multi-Site Air-Quality dataset** (12 stations, 2013-03 – 2017-02). The module walks from naive baselines to recurrent models (LSTM, GRU) and ends by measuring the empirical performance ceiling under idealized future-information assumptions.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Launch Jupyter and open the notebooks in order, or run them headless:

```bash
jupyter nbconvert --to notebook --execute --inplace 01_*.ipynb
```

## Notebooks

| # | Notebook | Topic |
|---|----------|-------|
| 1 | `01_Introduction_and_Data_Preprocessing.ipynb` | Dataset overview, cleaning, feature engineering, train/val/test split |
| 2 | `02_Naive_Forecasting_Models.ipynb` | Persistence and seasonal-naive baselines for *h* &isin; {1, 6, 12} |
| 3 | `03_Recurrent_Models_LSTM.ipynb` | LSTM(32) on PM2.5 / O&#8323;, sliding-window pipeline |
| 4 | `04_GRU_and_Advanced_Techniques.ipynb` | GRU vs LSTM, Huber loss, Dropout, EarlyStopping |
| 5 | `05_Future_Informed_Inputs_and_Data_Ceiling.ipynb` | Look-ahead inputs, target leakage as a measurement tool, empirical ceiling |

Each notebook ends with a **Recap + Check your understanding** section.

## Dataset

`dataset/` contains the 12 station CSVs (`PRSA_Data_<station>_20130301-20170228.csv`) from the UCI Beijing Multi-Site Air-Quality dataset. Notebooks load them via `forecasting_utils.load_clean_station(name)`.

## Files

- `forecasting_utils.py` &mdash; shared helpers: cleaning, wind components, cyclic features, sliding-window builder, default feature sets
- `requirements.txt` &mdash; Python dependencies (TensorFlow CPU, scikit-learn, pandas, matplotlib, jupyter)

