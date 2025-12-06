from __future__ import annotations

from typing import Tuple

import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix

from .types import EvalMetrics


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Tuple[EvalMetrics, np.ndarray]:
    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, average="weighted", zero_division=0))
    rec = float(recall_score(y_true, y_pred, average="weighted", zero_division=0))
    cm = confusion_matrix(y_true, y_pred)
    return EvalMetrics(accuracy=acc, precision_weighted=prec, recall_weighted=rec), cm
