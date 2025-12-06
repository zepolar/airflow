import os
import pandas as pd


def test_ingest_rename_and_date():
    from dags.iris_pipeline.ingest import load_breast_cancer_df

    ds = "2024-01-02"
    df = load_breast_cancer_df(ds)

    # Check that all 30 breast cancer features are present
    expected_features = [
        "mean_radius", "mean_texture", "mean_perimeter", "mean_area", "mean_smoothness",
        "mean_compactness", "mean_concavity", "mean_concave_points", "mean_symmetry",
        "mean_fractal_dimension", "radius_error", "texture_error", "perimeter_error",
        "area_error", "smoothness_error", "compactness_error", "concavity_error",
        "concave_points_error", "symmetry_error", "fractal_dimension_error",
        "worst_radius", "worst_texture", "worst_perimeter", "worst_area",
        "worst_smoothness", "worst_compactness", "worst_concavity",
        "worst_concave_points", "worst_symmetry", "worst_fractal_dimension"
    ]
    
    for feature in expected_features:
        assert feature in df.columns

    # ingestion_date set and normalized to date
    assert "ingestion_date" in df.columns
    assert pd.to_datetime(df["ingestion_date"]).dt.time.eq(pd.to_datetime(ds).normalize().time()).all()
