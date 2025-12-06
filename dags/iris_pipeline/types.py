from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass(frozen=True)
class TrainSplit:
    X_train_path: str
    y_train_path: str
    X_test_path: str
    y_test_path: str


@dataclass(frozen=True)
class TrainingResult:
    model_path: str
    params: Dict[str, Any]


@dataclass(frozen=True)
class EvalMetrics:
    accuracy: float
    precision_weighted: float
    recall_weighted: float
    confusion_matrix_path: Optional[str] = None


@dataclass(frozen=True)
class MlflowResult:
    run_id: Optional[str]
    error: Optional[str] = None
