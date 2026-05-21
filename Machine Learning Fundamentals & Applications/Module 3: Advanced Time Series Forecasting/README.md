# Advanced Time Series Forecasting Module

Welcome to the Advanced Time Series Forecasting module. This course is designed for learners who already have basic familiarity with Python, tabular data analysis, and introductory machine learning. The focus is on practical forecasting of hourly air-quality measurements using baseline methods, recurrent neural networks, and carefully designed time-series validation.

The module is divided into 5 interactive Jupyter notebooks that can be run locally or in Google Colab.

* * *

## Notebook Overview

### 1. [Introduction and Data Preprocessing](./01_Introduction_and_Data_Preprocessing.ipynb)

- Topics: Beijing Multi-Site Air-Quality dataset, station-level time series, missing values, feature engineering, chronological train-validation-test splitting, and forecasting targets.
- Core Theme: Preparing environmental time-series data for reliable forecasting experiments.

### 2. [Naive Forecasting Models](./02_Naive_Forecasting_Models.ipynb)

- Topics: persistence baseline, seasonal-naive baseline, forecast horizons, evaluation metrics, and comparison of simple reference models.
- Core Theme: Building honest baseline models before using more complex machine learning methods.

### 3. [Recurrent Models with LSTM](./03_Recurrent_Models_LSTM.ipynb)

- Topics: sliding-window datasets, sequence-to-value forecasting, LSTM architecture, training and validation curves, early stopping, and PM2.5 / O3 prediction.
- Core Theme: Using recurrent neural networks to learn temporal patterns in air-quality data.

### 4. [GRU and Advanced Techniques](./04_GRU_and_Advanced_Techniques.ipynb)

- Topics: GRU models, comparison with LSTM, Huber loss, dropout, learning-rate scheduling, and practical neural-network training choices.
- Core Theme: Improving recurrent forecasting models with robust training techniques.

### 5. [Future-Informed Inputs and Data Ceiling](./05_Future_Informed_Inputs_and_Data_Ceiling.ipynb)

- Topics: look-ahead inputs, target leakage as a diagnostic tool, future meteorology, empirical performance ceiling, and interpretation of upper-bound experiments.
- Core Theme: Understanding what model performance is possible when future information is partially available.

* * *

## Suggested Teaching Plan

This module is intended for **3 sessions of approximately 2 hours each**.

### Session 1
- Notebook 1: Introduction and Data Preprocessing
- Notebook 2: Naive Forecasting Models

### Session 2
- Notebook 3: Recurrent Models with LSTM
- Notebook 4: GRU and Advanced Techniques

### Session 3
- Notebook 5: Future-Informed Inputs and Data Ceiling
- Review and comparison of all forecasting approaches

This structure gives enough material for approximately six hours of teaching with explanation, live coding, model training, evaluation, and guided learner discussion.

## Dataset

The `dataset/` folder contains 12 station CSV files from the Beijing Multi-Site Air-Quality dataset, covering hourly observations from March 2013 to February 2017. The notebooks use these files to build forecasting tasks for pollutants such as PM2.5 and O3, together with meteorological predictors.

## Additional Files

- `requirements.txt` contains the Python dependencies needed to run the notebooks locally.

## How to use these notebooks

1. Upload the files to the appropriate GitHub folder of the E-Learning Platform repository.
2. Open the notebooks in GitHub or Google Colab.
3. Run the notebooks in order, from Notebook 1 to Notebook 5.
4. Encourage learners to compare each model against the naive baselines.
5. Use the plots, metrics, and recap sections for discussion and hands-on interpretation.
6. Treat the examples as templates that can be adapted to other environmental time-series forecasting problems.

## Responsible Partner Details

- **Institution:** FERIT Osijek, Croatia
