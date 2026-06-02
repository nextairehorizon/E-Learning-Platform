import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch

def plot_concentration_2d(df):
    """
    Plot concentration field with time on x-axis and space on y-axis.

    Parameters
    ----------
    df : pandas.DataFrame
        Must contain columns: 'x', 't', 'C'
    """

    # Extract sorted unique coordinates
    x = np.sort(df["x"].unique())
    t = np.sort(df["t"].unique())

    # Pivot to grid: rows -> space (x), columns -> time (t)
    C_grid = df.pivot(index="x", columns="t", values="C").values

    plt.figure(figsize=(8, 5))

    plt.imshow(
        C_grid,
        aspect='auto',
        origin='lower',
        extent=[t.min(), t.max(), x.min(), x.max()]
    )

    plt.xlim(0, 1)

    plt.colorbar(label="Concentration C(x,t)")
    plt.xlabel("Time t")
    plt.ylabel("Space x")
    plt.title("Concentration Field")

    plt.show()


def plot_reference(model):
    # --------------------------------------------------
    # Load reference ("true") dataset
    # --------------------------------------------------
    df_true = pd.read_csv("data/reference.csv")

    # Rename concentration column for clarity
    df_true = df_true.rename(columns={"C": "C_true"})

    # --------------------------------------------------
    # Use coordinates from true dataset for prediction
    # --------------------------------------------------
    X_true = df_true[["x", "t"]].values
    X_true_torch = torch.tensor(X_true, dtype=torch.float32)

    # Predict with trained model
    model.eval()

    with torch.no_grad():
        C_pred = model(X_true_torch).cpu().numpy().flatten()

    # Add predictions to dataframe
    df_compare = df_true.copy()
    df_compare["C_pred"] = C_pred

    # Compute absolute residuals
    df_compare["residual"] = abs(df_compare["C_true"] - df_compare["C_pred"])

    # --------------------------------------------------
    # Prepare grids for plotting
    # --------------------------------------------------
    x_vals = np.sort(df_compare["x"].unique())
    t_vals = np.sort(df_compare["t"].unique())

    C_true_grid = df_compare.pivot(index="x", columns="t", values="C_true").values
    C_pred_grid = df_compare.pivot(index="x", columns="t", values="C_pred").values
    R_grid      = df_compare.pivot(index="x", columns="t", values="residual").values

    # Common scales
    vmin = min(C_true_grid.min(), C_pred_grid.min())
    vmax = max(C_true_grid.max(), C_pred_grid.max())

    rmax = np.abs(R_grid).max()

    # --------------------------------------------------
    # Plot side-by-side comparison
    # --------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharex=True, sharey=True, constrained_layout=True)

    # --- True field
    im0 = axes[0].imshow(
        C_true_grid,
        aspect="auto",
        origin="lower",
        extent=[t_vals.min(), t_vals.max(), x_vals.min(), x_vals.max()],
        vmin=vmin,
        vmax=vmax
    )
    axes[0].set_title("Reference Data")
    axes[0].set_xlabel("Time t")
    axes[0].set_ylabel("Space x")

    # --- Prediction
    im1 = axes[1].imshow(
        C_pred_grid,
        aspect="auto",
        origin="lower",
        extent=[t_vals.min(), t_vals.max(), x_vals.min(), x_vals.max()],
        vmin=vmin,
        vmax=vmax
    )
    axes[1].set_title("Neural Network Prediction")
    axes[1].set_xlabel("Time t")

    # --- Residuals
    im2 = axes[2].imshow(
        R_grid,
        aspect="auto",
        origin="lower",
        extent=[t_vals.min(), t_vals.max(), x_vals.min(), x_vals.max()],
        vmin=0,
        vmax=rmax
    )
    axes[2].set_title("Absolute Residuals (True - Predicted)")
    axes[2].set_xlabel("Time t")

    # Colorbars
    fig.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04, label="Concentration")
    fig.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04, label="Concentration")
    fig.colorbar(im2, ax=axes[2], fraction=0.046, pad=0.04, label="Residual")

    plt.show()

    # --------------------------------------------------
    # rel. L2 error computation
    # --------------------------------------------------
    # Flatten arrays / columns
    C_true = df_compare["C_true"].values
    C_pred = df_compare["C_pred"].values

    relative_l2_error = np.linalg.norm(C_true - C_pred) / np.linalg.norm(C_true)

    print(f"Relative L2 Error: {100 * relative_l2_error:.1f}%")