from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    # Airflow connection id for PostgresHook
    postgres_conn_id: str = "postgres_default"

    # Tables
    breast_cancer_table: str = "breast_cancer_data"
    eval_table: str = "breast_cancer_evaluation"

    # ML/experiment
    experiment_name: str = "BreastCancerClassifier"
    model_type: str = "logreg"  # or "rf"
    test_size: float = 0.2
    random_state: int = 42

    # Optional MLflow tracking URI
    mlflow_tracking_uri: str | None = None


def _get_env(name: str, default: str | None = None) -> str | None:
    val = os.getenv(name)
    return val if val not in (None, "") else default


def load_settings_from_env() -> Settings:
    return Settings(
        postgres_conn_id=_get_env("POSTGRES_CONN_ID", "postgres_default"),
        breast_cancer_table=_get_env("BREAST_CANCER_TABLE", "breast_cancer_data"),
        eval_table=_get_env("EVAL_TABLE", "breast_cancer_evaluation"),
        experiment_name=_get_env("EXPERIMENT_NAME", "BreastCancerClassifier"),
        model_type=_get_env("MODEL_TYPE", "logreg"),
        test_size=float(_get_env("TEST_SIZE", "0.2")),
        random_state=int(_get_env("RANDOM_STATE", "42")),
        mlflow_tracking_uri=_get_env("MLFLOW_TRACKING_URI"),
    )
