from __future__ import annotations

from typing import Any

from sqlalchemy.engine import Engine

from airflow.providers.postgres.hooks.postgres import PostgresHook

from . import schemas
from .config import Settings


def get_engine(settings: Settings) -> Engine:
    """Return a SQLAlchemy engine from the Airflow Postgres connection."""
    hook = PostgresHook(postgres_conn_id=settings.postgres_conn_id)
    return hook.get_sqlalchemy_engine()  # type: ignore[return-value]


def ensure_tables(engine: Engine, settings: Settings) -> None:
    """Create required tables if they do not exist (idempotent)."""
    with engine.begin() as conn:
        conn.execute(schemas.create_iris_table_sql(settings.iris_table))
        conn.execute(schemas.create_eval_table_sql(settings.eval_table))
