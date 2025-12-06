import numpy as np


def test_compute_metrics_basic():
    from dags.iris_pipeline.metrics import compute_metrics

    y_true = np.array([0, 1, 1, 0])
    y_pred = np.array([0, 1, 0, 0])
    eval_metrics, cm = compute_metrics(y_true, y_pred)

    # accuracy: 3/4 = 0.75
    assert abs(eval_metrics.accuracy - 0.75) < 1e-9
    # confusion matrix shape (2x2) for classes {0,1}
    assert cm.shape == (2, 2)
