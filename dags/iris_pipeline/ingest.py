from __future__ import annotations

from typing import Dict, Any

import pandas as pd
from sklearn import datasets

from .config import Settings
from .db import get_engine
from .schemas import create_breast_cancer_table_sql


def load_breast_cancer_df(ds: str | None = None) -> pd.DataFrame:
    bc = datasets.load_breast_cancer()
    # Feature names are already in snake_case format (e.g., "mean radius" -> "mean_radius")
    feature_names = [name.replace(' ', '_') for name in bc.feature_names]
    df = pd.DataFrame(bc.data, columns=feature_names)
    df["target"] = bc.target
    if ds:
        df["ingestion_date"] = pd.to_datetime(ds).normalize()
    return df


def ensure_breast_cancer_table(settings: Settings) -> None:
    engine = get_engine(settings)
    with engine.begin() as conn:
        conn.execute(create_breast_cancer_table_sql(settings.breast_cancer_table))


def write_breast_cancer(settings: Settings, df: pd.DataFrame) -> int:
    engine = get_engine(settings)
    df.to_sql(settings.breast_cancer_table, engine, if_exists="append", index=False)
    return len(df)
