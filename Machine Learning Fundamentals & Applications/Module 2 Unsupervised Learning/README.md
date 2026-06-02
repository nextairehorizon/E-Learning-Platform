# Unsupervised Learning Module

Welcome to the Unsupervised Learning module. This course is designed for learners who already have basic familiarity with Python and tabular data analysis, and want to understand how machine learning can reveal structure in data without predefined labels. The focus is on practical unsupervised learning methods using air-quality and meteorological measurements from the Beijing Multi-Site Air-Quality dataset.

The module is divided into 4 interactive Jupyter notebooks that can be run locally or in Google Colab.

* * *

## Notebook Overview

### 1. [Introduction to Unsupervised Learning](./01_Introduction_to_Unsupervised_Learning.ipynb)

- Topics: supervised vs unsupervised learning, unlabeled data, clustering intuition, density-based thinking, synthetic data examples, and practical limitations of unsupervised methods.
- Core Theme: Understanding what it means to discover structure in data without target labels.

### 2. [Dimensionality Reduction with PCA](./02_Dimensionality_Reduction_with_PCA.ipynb)

- Topics: feature standardisation, correlated pollution and meteorological variables, principal components, explained variance, PCA loadings, and two-dimensional projections.
- Core Theme: Reducing complex environmental datasets into interpretable directions of variation.

### 3. [Clustering with K-Means](./03_Clustering_KMeans.ipynb)

- Topics: K-Means clustering, choosing the number of clusters, elbow method, silhouette score, cluster centroids, and interpretation of air-quality regimes.
- Core Theme: Grouping similar air-quality observations into meaningful pollution and weather patterns.

### 4. [Anomaly Detection with DBSCAN](./04_Anomaly_Detection_DBSCAN.ipynb)

- Topics: density-based clustering, DBSCAN parameters, epsilon selection, noise points, anomaly detection, comparison with K-Means, and source-hypothesis interpretation.
- Core Theme: Identifying unusual observations and dense data regions in environmental monitoring data.

* * *

## Suggested Teaching Plan

This module is intended for **2 sessions of approximately 2 hours each**.

### Session 1
- Notebook 1: Introduction to Unsupervised Learning
- Notebook 2: Dimensionality Reduction with PCA

### Session 2
- Notebook 3: Clustering with K-Means
- Notebook 4: Anomaly Detection with DBSCAN

This structure gives enough material for approximately four hours of teaching with explanation, live coding, interpretation of visual outputs, and guided learner practice.

## Dataset

The `dataset/` folder contains 12 station CSV files from the Beijing Multi-Site Air-Quality dataset, covering hourly observations from March 2013 to February 2017. The notebooks use these files to demonstrate unsupervised learning on real pollution and meteorological measurements.

## Additional Files

- `requirements.txt` contains the Python dependencies needed to run the notebooks locally.

## How to use these notebooks

1. Upload the files to the appropriate GitHub folder of the E-Learning Platform repository.
2. Open the notebooks in GitHub or Google Colab.
3. Run the notebooks in order, from Notebook 1 to Notebook 4.
4. Encourage learners to inspect the plots, change parameters, and compare how the methods respond.
5. Use the recap and check-your-understanding sections for discussion and hands-on work.
6. Treat the examples as templates that can be adapted to other air-quality or sensor datasets.

## Responsible Partner Details

- **Institution:** FERIT Osijek, Croatia
