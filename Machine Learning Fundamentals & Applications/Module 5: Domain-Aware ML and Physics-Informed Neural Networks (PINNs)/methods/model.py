import numpy as np

import torch
import torch.nn as nn

class NeuralNet(nn.Module):
    def __init__(self):
        super().__init__()

        self.model = nn.Sequential(
            nn.Linear(2, 32),
            nn.Tanh(),

            nn.Linear(32, 32),
            nn.Tanh(),

            nn.Linear(32, 32),
            nn.Tanh(),

            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.model(x)
    

def sample_collocation_points(N_col=128):
    """
    Samples collocation points within the computational domain.

    Parameters
    ----------
    N_col : int
        Number of collocation points to be sampled

    Returns
    -------
    X_col : torch.tensor
        Sampled collocation points
    """


    # Sample uniformly in the full domain
    x_col = np.random.uniform(0.0, 1.0, N_col)
    t_col = np.random.uniform(0.0, 1.0, N_col)

    X_col = torch.tensor(
        np.column_stack([x_col, t_col]),
        dtype=torch.float32,
        requires_grad=True
    )
    return X_col