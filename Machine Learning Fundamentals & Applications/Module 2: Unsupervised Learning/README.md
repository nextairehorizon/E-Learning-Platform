# Module 2 — Unsupervised Learning

Dimensionality reduction, clustering, and anomaly detection on the **Beijing Multi-Site Air-Quality dataset** (12 stations, 2013-03 – 2017-02). The module walks from a synthetic warm-up to PCA, KMeans, and DBSCAN applied to real pollution + meteorology data.

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
| 1 | `01_Introduction_to_Unsupervised_Learning.ipynb` | What unsupervised learning is, synthetic blobs, intuition for clustering and density |
| 2 | `02_Dimensionality_Reduction_with_PCA.ipynb` | Standardisation, PCA on pollution + meteorology features, variance explained, 2D projections |
| 3 | `03_Clustering_KMeans.ipynb` | KMeans on PRSA features, choosing *k* (elbow, silhouette), interpreting cluster centroids |
| 4 | `04_Anomaly_Detection_DBSCAN.ipynb` | DBSCAN, *eps* selection, noise points as anomalies, comparison with KMeans |

Each notebook ends with a **Recap + Check your understanding** section.

## Dataset

`dataset/` contains the 12 station CSVs (`PRSA_Data_<station>_20130301-20170228.csv`) from the UCI Beijing Multi-Site Air-Quality dataset. Notebooks load them directly with `pd.read_csv("dataset/PRSA_Data_<station>_...csv")`.

## Files

- `requirements.txt` &mdash; Python dependencies (scikit-learn, pandas, matplotlib, seaborn, scipy, jupyter)
