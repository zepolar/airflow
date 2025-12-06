from __future__ import annotations

from typing import Dict, Any

import pandas as pd
from sklearn import datasets

from .config import Settings
from .db import get_engine
from .schemas import create_iris_table_sql


# For Diabetes dataset we keep original feature names from scikit-learn
DIABETES_FEATURES = ["age", "sex", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6"]


def load_iris_df(ds: str | None = None) -> pd.DataFrame:
    # Backward-compatible function name; now loads Diabetes dataset
    diabetes = datasets.load_diabetes()
    df = pd.DataFrame(diabetes.data, columns=DIABETES_FEATURES)
    df["target"] = diabetes.target
    if ds:
        df["ingestion_date"] = pd.to_datetime(ds).normalize()
    return df


def ensure_iris_table(settings: Settings) -> None:
    engine = get_engine(settings)
    with engine.begin() as conn:
        conn.execute(create_iris_table_sql(settings.iris_table))


def write_iris(settings: Settings, df: pd.DataFrame) -> int:
    engine = get_engine(settings)
    df.to_sql(settings.iris_table, engine, if_exists="append", index=False)
    return len(df)
