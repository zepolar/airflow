"""Iris pipeline modular components applying SOLID principles.

Modules:
- config: runtime configuration via environment variables
- db: database helpers (Postgres engine + ensure tables)
- schemas: DDL definitions
- ingest: dataset loading/transformation and persistence
- train: model training and data loading utilities
- metrics: evaluation metrics computations
- mlflow_utils: pluggable metrics/artifacts logger (MLflow / NoOp)
- types: typed DTOs for XCom-safe payloads
"""
