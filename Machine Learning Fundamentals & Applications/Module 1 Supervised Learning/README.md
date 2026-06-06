# Supervised Learning Module

Welcome to the Supervised Learning module. This course is designed for learners who already have basic familiarity with Python and tabular data analysis. It is a self-contained eight-notebook tutorial that takes a student from first principles of supervised learning to model interpretability, using the **Beijing Multi-Site Air-Quality Dataset**.

Everything you need to run the tutorial — definitions, derivations, worked examples, plots, exercises, and the data files themselves — is contained in this folder. No external scripts, manuscripts or project repositories are required.

The module is divided into 8 interactive Jupyter notebooks that can be run locally or in Google Colab.

# Layout

```
├── data/                                          (CSV data — 5 files, ~40 MB)
│   ├── air_quality_basic_aotizhongxin.csv
│   ├── air_quality_basic_nongzhanguan.csv
│   ├── air_quality_nongzhanguan_forecast.csv
│   ├── air_quality_nongzhanguan_o3_forecast.csv
│   └── PRSA_Data_Aotizhongxin_20130301-20170228.csv
├── 01_what_is_ml.ipynb
├── 02_regression.ipynb
├── 03_classification.ipynb
├── 04_feature_engineering.ipynb
├── 05_time_series_forecasting.ipynb
├── 06_trees_random_forest.ipynb
├── 07_boosting_stacking.ipynb
├── 08_interpretability.ipynb
├── README.md                                      (this file)
```

## Notebook Overview

Each notebook has the same format:

1. **Learning objectives** — what you will be able to do after running the notebook.
2. **Definitions and equations** — the theory needed for the topic.
3. **Worked examples** — runnable code cells that produce real numbers and plots.
4. **Common misconceptions** — the mistakes that bite students most often.
5. **Exercises** — 2–3 TODO cells per notebook with hints.
6. **Summary** — five bullet points.

### 1. [What Is Machine Learning?](./01_what_is_ml.ipynb)

- Topics: Datasets, features, labels; supervised vs unsupervised; the ML pipeline; scaling and encoding.
- Core Theme: Establishes the vocabulary (dataset, feature, label, loss) and walks the seven-stage ML pipeline on the Beijing dataset.

### 2. [Regression](./02_regression.ipynb)

- Topics: Linear regression, MSE, the normal equations; MAE / RMSE / MAPE / R² ; ridge.
- Core Theme: RBuilds linear regression from first principles — model, MSE loss, the normal-equations closed form, ridge regularisation.

### 3. [Classification](./03_classification.ipynb)

- Topics:Logistic and softmax regression; cross-entropy; confusion matrix; macro-F1.
- Core Theme: Generalises linear regression to logistic / softmax regression with cross-entropy loss, trains 3-class and 6-class PM2.5 category models, and uses confusion matrices and macro-F1 to expose the granularity-induced error that finer categories incur.

### 4. [Feature Engineering](./04_feature_engineering.ipynb)

- Topics: Standardisation, one-hot, **cyclic (sin/cos)**, lag features, time-based split.
- Core Theme: Walks the five transformations that turn raw atmospheric measurements into model-ready inputs — standardisation, one-hot encoding, cyclic (sin/cos) encoding, lag features, and chronological splits.

### 5. [Time-Series Forecasting](./05_time_series_forecasting.ipynb)

- Topics: Direct vs recursive forecasting; persistence baseline; multi-horizon and multi-pollutant sweep .
- Core Theme: Reframes the target as a future-shifted value, trains direct one-step / multi-step PM2.5 and AQI forecasters at h ∈ {1, 6, 12}, and benchmarks every model against the persistence baseline to quantify pollutant-specific horizon degradation.

### 6. [Decision Trees and Random Forests](./06_trees_random_forest.ipynb)

- Topics: Decision trees, the overfit profile; random forests; `TimeSeriesSplit` cross-validation
- Core Theme: Introduces the non-linear family — recursive impurity-minimising splits, the single-tree overfit profile, bagging plus random feature subsampling.

### 7. [Bagging, Boosting, Gradient Boosting and Stacking](./07_boosting_stacking.ipynb)

- Topics: Gradient boosting derivation, grid search, `StackingRegressor`.
- Core Theme: Derives gradient boosting as steepest descent in function space, tunes a GBM with grid search, and builds a time-aware manual stack (chronological inner-holdout split) combining linear, RF and GBM through a Ridge meta-learner.

### 8. [Model Interpretability](./08_interpretability.ipynb)

- Topics: Coefficients, permutation importance, partial dependence, ICE, SHAP.
- Core Theme: Opens the black box with four complementary tools — standardised linear coefficients, permutation importance, partial-dependence and ICE plots, and SHAP — and uses them to attribute single predictions and expose the PDP pitfalls of correlated lag features..


## Dataset

The five CSVs in `data/` are derived from the Beijing Multi-Site Air-Quality
Dataset (12 stations, hourly observations, 2013-03-01 → 2017-02-28). Their
shapes and uses are described in §1.0 of Notebook 1. In summary:

- The two `air_quality_basic_*.csv` files are wide tables (one row per hour
  for one *target* station) with PM2.5 and PM10 from eleven neighbour
  stations as feature columns, plus three target columns (continuous PM2.5
  and two pre-binned categorical targets).
- The two `*_forecast.csv` files are single-station forecasting tables with
  current-hour pollutants and meteorology, cyclic time encodings, lag
  features (1–24 h), and pre-shifted target columns for horizons of 1, 6,
  and 12 hours.
- `PRSA_Data_Aotizhongxin_20130301-20170228.csv` is the *raw* archive for one
  station — used in Notebook 1 to inspect the literal `NA` markers and the
  natural pattern of missing observations before any cleaning.

## Exercises

Look for cells that begin with `# EXERCISE`. Each exercise has a hint in the
markdown cell immediately above; uncomment and complete the TODO markers.


* * *


## Additional Files

- `requirements.txt` contains the Python dependencies needed to run the notebooks locally.

## How to use these notebooks

1. Upload the files to the appropriate GitHub folder of the E-Learning Platform repository.
2. Open the notebooks in GitHub or Google Colab.
3. Run the notebooks in order, from Notebook 1 to Notebook 4.
4. Encourage learners to inspect the plots, change parameters, and compare how the methods respond.
5. Use the recap and check-your-understanding sections for discussion and hands-on work.
6. Treat the examples as templates that can be adapted to other air-quality or sensor datasets.

(Open the notebooks in numeric order on the first pass. On a typical laptop the whole tutorial runs in roughly 10–15 minutes of cell execution time.

## Responsible Partner Details

- **Institution:** FERIT Osijek, Croatia
