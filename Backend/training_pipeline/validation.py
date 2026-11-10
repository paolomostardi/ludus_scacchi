"""Validate arrays and metrics before accepting pipeline results."""
import math
import numpy as np


def validate_arrays(x, y):
    if x.ndim != 4 or tuple(x.shape[1:]) != (15, 8, 8):
        raise ValueError(f"Expected input shape (N, 15, 8, 8), got {x.shape}.")
    if y.shape != (len(x), 64) or len(x) == 0:
        raise ValueError(f"Expected nonempty aligned targets (N, 64), got {y.shape}.")
    for start in range(0, len(x), 8192):
        inputs, targets = x[start:start + 8192], y[start:start + 8192]
        if not np.isfinite(inputs).all() or not np.isfinite(targets).all():
            raise ValueError("Inputs and labels must be finite.")
        if not np.isin(targets, [0, 1]).all() or not (targets.sum(axis=1) == 1).all():
            raise ValueError("Targets must be one-hot source-square labels.")


def validate_metrics(metrics):
    for name, value in metrics.items():
        if not math.isfinite(float(value)):
            raise ValueError(f"Non-finite metric: {name}")
        if "accuracy" in name and not 0 <= value <= 1:
            raise ValueError(f"Accuracy outside [0, 1]: {name}")
        if "loss" in name and value < 0:
            raise ValueError(f"Negative loss: {name}")
