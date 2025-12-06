from __future__ import annotations

import os
import logging
import tempfile
from datetime import datetime
from typing import Dict, Any

import numpy as np
import pandas as pd
from airflow.decorators import dag, task, task_group
from airflow.operators.python import get_current_context

from iris_pipeline.config import load_settings_from_env
from iris_pipeline import ingest as ingest_mod
from iris_pipeline import train as train_mod
from iris_pipeline import metrics as metrics_mod
from iris_pipeline import db as db_mod
from iris_pipeline.mlflow_utils import build_metrics_logger


@dag(
    schedule="@daily",  # every day
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["example", "ml", "iris", "mlflow"],
    default_args={"owner": "airflow", "retries": 1},
)
def iris_mlflow_training_dag():

    settings = load_settings_from_env()

    @task_group(group_id="ingestion")
    def ingestion_group():
        @task()
        def create_iris_table() -> str:
            engine = db_mod.get_engine(settings)
            db_mod.ensure_tables(engine, settings)
            return settings.iris_table

        @task()
        def ingest_iris() -> Dict[str, Any]:
            ctx = get_current_context()
            ds = ctx.get("ds")
            df = ingest_mod.load_iris_df(ds)
            rows = ingest_mod.write_iris(settings, df)
            return {"rows_ingested": rows, "table": settings.iris_table}

        _ = create_iris_table()
        return ingest_iris()

    @task_group(group_id="training")
    def training_group():
        @task()
        def load_data() -> Dict[str, Any]:
            X, y = train_mod.load_dataset(settings)
            # write arrays to temp npy files to avoid heavy XCom
            tmp_dir = tempfile.mkdtemp(prefix="iris_data_")
            X_path = os.path.join(tmp_dir, "X.npy")
            y_path = os.path.join(tmp_dir, "y.npy")
            np.save(X_path, X)
            np.save(y_path, y)
            return {"X_path": X_path, "y_path": y_path}

        @task()
        def fit(payload: Dict[str, Any]) -> Dict[str, Any]:
            X = np.load(payload["X_path"])  # type: ignore[arg-type]
            y = np.load(payload["y_path"])  # type: ignore[arg-type]
            result = train_mod.fit_model(settings, X, y)
            return result

        loaded = load_data()
        return fit(loaded)

    @task_group(group_id="evaluation")
    def evaluation_group(train_result: Dict[str, Any]):
        @task()
        def compute(train_result: Dict[str, Any]) -> Dict[str, Any]:
            y_test = train_result["y_test"]
            y_pred = train_result["y_pred"]
            eval_metrics, cm = metrics_mod.compute_metrics(y_test, y_pred)

            # Persist confusion matrix to file for artifact logging
            tmp_dir = tempfile.mkdtemp(prefix="iris_eval_")
            cm_path = os.path.join(tmp_dir, "confusion_matrix.csv")
            pd.DataFrame(cm).to_csv(cm_path, index=False)
            return {
                "metrics": {
                    "accuracy": eval_metrics.accuracy,
                    "precision_weighted": eval_metrics.precision_weighted,
                    "recall_weighted": eval_metrics.recall_weighted,
                },
                "confusion_matrix_path": cm_path,
            }

        @task()
        def log_mlflow(train_result: Dict[str, Any], eval_result: Dict[str, Any]) -> Dict[str, Any]:
            # Emit a preflight log so users know where to look (Airflow task logs, not MLflow container)
            effective_tracking_uri = settings.mlflow_tracking_uri or os.getenv("MLFLOW_TRACKING_URI")
            # Use print to guarantee visibility even if logging handlers are missing in the container
            print(
                f"[MLFLOW] BEGIN logging from Airflow task: tracking_uri={effective_tracking_uri}, "
                f"experiment={settings.experiment_name}",
                flush=True,
            )
            logger = build_metrics_logger(settings)
            ml = logger.log_all(
                params=train_result["params"],
                metrics=eval_result["metrics"],
                model_path=train_result["model_path"],
                features=train_result["features"],
                confusion_matrix_path=eval_result.get("confusion_matrix_path"),
            )
            # Post-flight visibility to confirm MLflow outcome in Airflow task logs
            print(f"[MLFLOW] END logging: run_id={ml.run_id}, error={ml.error}", flush=True)
            return {"run_id": ml.run_id, "mlflow_error": ml.error}

        @task()
        def persist(eval_result: Dict[str, Any], mlflow_result: Dict[str, Any]) -> Dict[str, Any]:
            engine = db_mod.get_engine(settings)
            db_mod.ensure_tables(engine, settings)
            ctx = get_current_context()
            ds = ctx.get("ds")
            # Echo the incoming MLflow result to ensure at least one task surfaces it in logs
            print(
                f"[MLFLOW] Persisting evaluation with run_id={mlflow_result.get('run_id')} "
                f"error={mlflow_result.get('mlflow_error')}",
                flush=True,
            )
            payload = {
                "run_id": mlflow_result.get("run_id"),
                "accuracy": eval_result["metrics"]["accuracy"],
                "precision_weighted": eval_result["metrics"]["precision_weighted"],
                "recall_weighted": eval_result["metrics"]["recall_weighted"],
                "execution_date": pd.to_datetime(ds).date(),
            }
            pd.DataFrame([payload]).to_sql(settings.eval_table, engine, if_exists="append", index=False)
            return payload

        eval_result = compute(train_result)
        mlflow_result = log_mlflow(train_result, eval_result)
        return persist(eval_result, mlflow_result)

    ing = ingestion_group()
    tr = training_group()
    # Ensure ingestion (table creation + data load) completes before training reads from the table
    ing >> tr
    _ = evaluation_group(tr)


dag = iris_mlflow_training_dag()
