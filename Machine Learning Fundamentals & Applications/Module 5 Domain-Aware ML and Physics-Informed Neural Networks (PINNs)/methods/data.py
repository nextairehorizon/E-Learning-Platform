import torch
import pandas as pd
from sklearn.model_selection import train_test_split

def load_measurements(test_size=0.2, random_state=42, shuffle=True):
    
    data_path = "data/measurements.csv"  

    df = pd.read_csv(data_path)

    # Features and target
    X = df[["x", "t"]]
    y = df[["C"]]

    # Train-test split
    X_train_df, X_test_df, y_train_df, y_test_df = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        shuffle=shuffle
    )

    # Convert to PyTorch tensors
    X_train = torch.tensor(X_train_df.values, dtype=torch.float32)
    X_test  = torch.tensor(X_test_df.values, dtype=torch.float32)

    y_train = torch.tensor(y_train_df.values, dtype=torch.float32)
    y_test  = torch.tensor(y_test_df.values, dtype=torch.float32)

    # Check shapes
    print("Training features:", X_train.shape)
    print("Training targets :", y_train.shape)
    print("Test features    :", X_test.shape)
    print("Test targets     :", y_test.shape)
    
    return X_train, y_train, X_test, y_test