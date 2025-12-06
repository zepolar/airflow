import numpy as np
from sklearn import datasets


def _get_settings(model_type: str):
    from dags.iris_pipeline.config import Settings

    return Settings(
        postgres_conn_id="postgres_default",
        breast_cancer_table="breast_cancer_data",
        eval_table="breast_cancer_evaluation",
        experiment_name="BreastCancerClassifier",
        model_type=model_type,
        test_size=0.2,
        random_state=42,
        mlflow_tracking_uri=None,
    )


def test_fit_model_logreg_returns_expected_keys():
    from dags.iris_pipeline.train import fit_model

    bc = datasets.load_breast_cancer()
    X = bc.data
    y = bc.target
    settings = _get_settings("logreg")
    result = fit_model(settings, X, y)

    for key in ("model_path", "params", "X_test", "y_test", "y_pred", "features"):
        assert key in result
    assert len(result["y_test"]) == len(result["y_pred"])  # type: ignore[index]


def test_fit_model_rf_returns_expected_keys():
    from dags.iris_pipeline.train import fit_model

    bc = datasets.load_breast_cancer()
    X = bc.data
    y = bc.target
    settings = _get_settings("rf")
    result = fit_model(settings, X, y)

    assert result["params"]["model"] == "RandomForestClassifier"
    assert len(result["y_test"]) == len(result["y_pred"])  # type: ignore[index]
