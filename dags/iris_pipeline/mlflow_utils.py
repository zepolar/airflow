from __future__ import annotations

import logging
import os
from typing import Dict, Any, Optional

from .config import Settings
from .types import MlflowResult


# Ensure that, even if no logging handler is configured inside the Airflow
# container, our messages are still visible in task logs. Airflow usually
# configures logging, but in some setups custom images might miss that.
def _emit_log(level: str, msg: str, *args: Any) -> None:
    try:
        root = logging.getLogger()
        logger = logging.getLogger(__name__)
        # If there are no handlers configured at all, set up a basic one
        if not root.handlers and not logger.handlers:
            logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
        # Forward to logging module
        log_fn = getattr(logging.getLogger(__name__), level, None)
        if callable(log_fn):
            log_fn(msg, *args)
    except Exception:
        # Never fail because of logging
        pass
    # Always also print, so stdout captures it in Docker logs even if logging is misconfigured
    try:
        print(msg % args if args else msg, flush=True)
    except Exception:
        # Fallback plain print
        print(msg, flush=True)


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
            from mlflow.tracking import MlflowClient

            if self.tracking_uri:
                mlflow.set_tracking_uri(self.tracking_uri)
            # Emit a small debug line to Airflow logs to make troubleshooting easier
            _emit_log(
                "info",
                "MLflow logging: tracking_uri=%s, experiment=%s",
                mlflow.get_tracking_uri(),
                self.experiment_name,
            )
            _emit_log("info", "Ensuring MLflow experiment exists: %s", self.experiment_name)

            # Robustly ensure the experiment exists and obtain its ID
            client = MlflowClient()
            exp = client.get_experiment_by_name(self.experiment_name)
            if exp is None:
                try:
                    exp_id = client.create_experiment(self.experiment_name)
                    _emit_log(
                        "info",
                        "Created MLflow experiment '%s' with id=%s",
                        self.experiment_name,
                        exp_id,
                    )
                except Exception as ce:
                    # There can be a race if multiple tasks try to create simultaneously; re-fetch
                    _emit_log("warning", "Creating MLflow experiment failed (%s). Will retry fetching it.", ce)
                    exp = client.get_experiment_by_name(self.experiment_name)
                    if exp is None:
                        raise
                    exp_id = exp.experiment_id
            else:
                exp_id = exp.experiment_id

            _emit_log("info", "Using MLflow experiment '%s' (id=%s)", self.experiment_name, exp_id)

            # Start the run explicitly under the resolved experiment id
            with mlflow.start_run(experiment_id=exp_id) as run:
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
            _emit_log("warning", "MLflow logging failed: %s", e)
            return MlflowResult(run_id=None, error=str(e))


def build_metrics_logger(settings: Settings) -> MetricsLogger:
    # Prefer explicit setting; if missing, fall back to environment.
    tracking_uri = settings.mlflow_tracking_uri or os.getenv("MLFLOW_TRACKING_URI")
    # Always return an MLflow logger so we surface errors instead of silently NoOp'ing.
    # If tracking_uri is None, MLflow uses its default local store; this still helps with debugging.
    return MLflowMetricsLogger(tracking_uri, settings.experiment_name)
