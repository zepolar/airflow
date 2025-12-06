def test_noop_logger_returns_none_run_id():
    from dags.iris_pipeline.mlflow_utils import NoOpMetricsLogger

    logger = NoOpMetricsLogger()
    res = logger.log_all(
        params={"a": 1},
        metrics={"m": 0.5},
        model_path="/tmp/nonexistent.model",
        features=["f1", "f2"],
        confusion_matrix_path=None,
    )
    assert res.run_id is None
    assert res.error is None
