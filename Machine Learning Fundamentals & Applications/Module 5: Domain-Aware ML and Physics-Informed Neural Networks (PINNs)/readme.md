# Physics-Informed Neural Networks for Air Pollution Dynamics

This repository contains a hands-on tutorial series introducing **Physics-Informed Neural Networks (PINNs)** through a simple and intuitive application from **air pollution modeling**.

The tutorials are designed for students and beginners who want to understand:

- how standard neural networks learn from data,
- how physics can be incorporated into machine learning models,
- and how PINNs can be used as neural solvers for differential equations.

The example problem is based on the **1D diffusion equation**, which models how a pollutant concentration spreads over time along a road or spatial domain.

---

## 📚 Tutorial Overview

The repository contains three Jupyter notebooks that gradually introduce the main concepts.

### 1️⃣ [Data-Driven Neural Network Baseline](01_diffusion_data_driven_learning.ipynb)

A standard neural network is trained purely on limited and noisy sensor data.

Topics covered:

- supervised learning for regression
- train/test split
- neural network training with PyTorch
- extrapolation challenges
- limitations of purely data-driven models

### 2️⃣ [Physics-Informed Neural Network (Hybrid Learning)](02_diffusion_pinn_hybrid_learning.ipynb)

A PINN is trained using both measurement data and the governing diffusion equation.

Topics covered:

- automatic differentiation
- PDE residual loss
- combining data loss and physics loss
- improved generalization
- physically meaningful predictions

### 3️⃣ [Physics-Informed Neural Network as a Neural Solver](03_diffusion_pinn_forward_simulation.ipynb)

A PINN is trained without measurement data, using only:

- the diffusion equation,
- the initial condition,
- and boundary conditions.

Topics covered:

- solving PDEs with PINNs
- initial/boundary condition constraints
- optimizing PINN performance
- PINN limitations and modifications

---

### 🛠 Requirements

Required packages:
- numpy
- pandas
- matplotlib
- torch
- scikit-learn
- jupyter

Install via:

```` pip install numpy pandas matplotlib torch scikit-learn jupyter ````

or via 

```` pip install -r requirements.txt ````

---

### 🎯 Learning Objectives

After completing the tutorials, you should understand:

- how neural networks solve regression tasks,
- why extrapolation from sparse data is difficult,
- how differential equations can be embedded into training,
- how PINNs improve predictions,
- and how PINNs can solve forward PDE problems.
