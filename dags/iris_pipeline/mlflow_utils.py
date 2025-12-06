from __future__ import annotations

import os
from typing import Dict, Any, Optional

import pandas as pd

from .config import Settings
from .types import MlflowResult


class MetricsLogger:
    def log_all(
        self,
        params: Dict[str, Any],
        metrics: Dict[str, float],
        model_path: str,
        features: list[str],
        confusion_matrix_path: Optional[str] = None,
    ) -> MlflowResult:
        raise NotImplementedError


class NoOpMetricsLogger(MetricsLogger):
    def log_all(
        self,
        params: Dict[str, Any],
        metrics: Dict[str, float],
        model_path: str,
        features: list[str],
        confusion_matrix_path: Optional[str] = None,
    ) -> MlflowResult:
        return MlflowResult(run_id=None, error=None)


class MLflowMetricsLogger(MetricsLogger):
    def __init__(self, tracking_uri: Optional[str], experiment_name: str) -> None:
        self.tracking_uri = tracking_uri
        self.experiment_name = experiment_name

    def log_all(
        self,
        params: Dict[str, Any],
        metrics: Dict[str, float],
        model_path: str,
        features: list[str],
        confusion_matrix_path: Optional[str] = None,
    ) -> MlflowResult:
        try:
            import mlflow
            import mlflow.sklearn  # ensure flavor registered

            if self.tracking_uri:
                mlflow.set_tracking_uri(self.tracking_uri)
            mlflow.set_experiment(self.experiment_name)

            with mlflow.start_run() as run:
                run_id = run.info.run_id
                mlflow.log_params(params)
                mlflow.log_metrics(metrics)
                # mlflow.sklearn.log_model expects a model object, so load it from disk
                try:
                    import joblib

                    model_obj = joblib.load(model_path)
                    mlflow.sklearn.log_model(model_obj, artifact_path="model")
                except Exception:
                    # If loading fails, skip model logging but keep run
                    pass

                # Artifacts
                # Save features list
                feats_path = os.path.join(os.path.dirname(model_path), "features.txt")
                with open(feats_path, "w", encoding="utf-8") as fh:
                    fh.write("\n".join(features))
                mlflow.log_artifact(feats_path, artifact_path="artifacts")

                if confusion_matrix_path and os.path.exists(confusion_matrix_path):
                    mlflow.log_artifact(confusion_matrix_path, artifact_path="artifacts")

                return MlflowResult(run_id=run_id, error=None)
        except Exception as e:
            return MlflowResult(run_id=None, error=str(e))


def build_metrics_logger(settings: Settings) -> MetricsLogger:
    if settings.mlflow_tracking_uri:
        return MLflowMetricsLogger(settings.mlflow_tracking_uri, settings.experiment_name)
    return NoOpMetricsLogger()
