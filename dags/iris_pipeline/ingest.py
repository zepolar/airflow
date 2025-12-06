from __future__ import annotations

from typing import Dict, Any

import pandas as pd
from sklearn import datasets

from .config import Settings
from .db import get_engine
from .schemas import create_iris_table_sql


RENAME_MAP = {
    "sepal length (cm)": "sepal_length",
    "sepal width (cm)": "sepal_width",
    "petal length (cm)": "petal_length",
    "petal width (cm)": "petal_width",
}


def load_iris_df(ds: str | None = None) -> pd.DataFrame:
    iris = datasets.load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df = df.rename(columns=RENAME_MAP)
    df["target"] = iris.target
    df["target_name"] = df["target"].apply(lambda i: iris.target_names[i])
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
