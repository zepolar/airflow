from __future__ import annotations

import os
import tempfile
from typing import Dict, Any, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from .config import Settings
from .db import get_engine


FEATURE_COLS: List[str] = [
    "sepal_length",
    "sepal_width",
    "petal_length",
    "petal_width",
]


def load_dataset(settings: Settings) -> Tuple[np.ndarray, np.ndarray]:
    engine = get_engine(settings)
    df = pd.read_sql(f"SELECT * FROM {settings.iris_table}", con=engine)
    X = df[FEATURE_COLS].values
    y = df["target"].values
    return X, y


def fit_model(settings: Settings, X: np.ndarray, y: np.ndarray):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=settings.test_size, random_state=settings.random_state, stratify=y
    )

    if settings.model_type == "rf":
        model = RandomForestClassifier(random_state=settings.random_state)
        params: Dict[str, Any] = {"model": "RandomForestClassifier", "random_state": settings.random_state}
    else:
        model = LogisticRegression(max_iter=400, multi_class="auto")
        params = {"model": "LogisticRegression", "max_iter": 400}

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Persist model to a temp path to avoid XCom heavy objects
    tmp_dir = tempfile.mkdtemp(prefix="iris_model_")
    model_path = os.path.join(tmp_dir, "model.joblib")
    joblib.dump(model, model_path)

    # Important: make XCom-safe payload (avoid numpy arrays in XCom)
    return {
        "model_path": model_path,
        "params": params,
        "X_test": X_test.tolist(),
        "y_test": y_test.tolist(),
        "y_pred": y_pred.tolist(),
        "features": FEATURE_COLS,
    }
