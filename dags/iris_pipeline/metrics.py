from __future__ import annotations

from typing import Tuple

import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from .types import EvalMetrics


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> EvalMetrics:
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    return EvalMetrics(rmse=rmse, mae=mae, r2=r2)
