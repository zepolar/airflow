from __future__ import annotations


def create_iris_table_sql(table: str) -> str:
    # Repurposed for Diabetes dataset. Keeping function name for backward compatibility with db.ensure_tables.
    # scikit-learn Diabetes features: age, sex, bmi, bp, s1, s2, s3, s4, s5, s6
    return f"""
    CREATE TABLE IF NOT EXISTS {table} (
        age double precision,
        sex double precision,
        bmi double precision,
        bp double precision,
        s1 double precision,
        s2 double precision,
        s3 double precision,
        s4 double precision,
        s5 double precision,
        s6 double precision,
        target double precision,
        ingestion_date date
    )
    """


def create_eval_table_sql(table: str) -> str:
    # Regression metrics for Diabetes dataset
    return f"""
    CREATE TABLE IF NOT EXISTS {table} (
        run_id text,
        rmse double precision,
        mae double precision,
        r2 double precision,
        execution_date date
    )
    """
