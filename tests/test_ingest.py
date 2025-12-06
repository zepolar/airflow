import os
import pandas as pd


def test_ingest_rename_and_date():
    from dags.iris_pipeline.ingest import load_iris_df, RENAME_MAP

    ds = "2024-01-02"
    df = load_iris_df(ds)

    # Columns renamed
    for src, dst in RENAME_MAP.items():
        assert dst in df.columns

    # ingestion_date set and normalized to date
    assert "ingestion_date" in df.columns
    assert pd.to_datetime(df["ingestion_date"]).dt.time.eq(pd.to_datetime(ds).normalize().time()).all()
