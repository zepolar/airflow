from __future__ import annotations


def create_iris_table_sql(table: str) -> str:
    return f"""
    CREATE TABLE IF NOT EXISTS {table} (
        sepal_length double precision,
        sepal_width double precision,
        petal_length double precision,
        petal_width double precision,
        target integer,
        target_name text,
        ingestion_date date
    )
    """


def create_eval_table_sql(table: str) -> str:
    return f"""
    CREATE TABLE IF NOT EXISTS {table} (
        run_id text,
        accuracy double precision,
        precision_weighted double precision,
        recall_weighted double precision,
        execution_date date
    )
    """
