Airflow DAG: Iris Ingestion, Training and MLflow Logging

This project contains an Airflow DAG that runs every 10 minutes to:

1. Ingest the Iris dataset from scikit-learn into PostgreSQL (`iris_data`).
2. Train a classifier (LogisticRegression by default) and log params, metrics and artifacts to MLflow.
3. Persist evaluation metrics into PostgreSQL (`iris_evaluation`) and MLflow.

Project layout

- `dags/iris_mlflow_dag.py` — main DAG orchestrator using TaskFlow API and TaskGroups (SOLID refactor).
- `dags/iris_pipeline/` — modular components (apply SOLID principles):
  - `config.py` — settings read from environment variables at runtime.
  - `schemas.py` — DDL helpers for required tables.
  - `db.py` — DB engine and ensure‑tables helpers.
  - `ingest.py` — load/transform the Iris dataset and write to DB.
  - `train.py` — dataset loading from DB and model training (LogReg/RandomForest).
  - `metrics.py` — evaluation metrics and confusion matrix.
  - `mlflow_utils.py` — pluggable metrics logger (MLflow/NoOp).
  - `types.py` — small DTOs for XCom‑safe payloads.
- `tests/` — unit tests for metrics, ingest, train, and logger utilities (pytest).
- `requirements.txt` — dependencies (install into Airflow environment).

Prerequisites

- Airflow environment (2.6+ recommended).
- PostgreSQL instance reachable from Airflow.
- MLflow Tracking server (optional but recommended). If not configured, the DAG will still run and only skip MLflow logging.

Installation

Install Python dependencies in the Airflow environment (for example, your Scheduler/Workers image or venv):

```
pip install -r requirements.txt
```

Ensure the Airflow Postgres provider is installed (included in `requirements.txt`).

Docker usage

You can run this DAG quickly using the included Dockerfile based on the official Apache Airflow image.

1) Build the image (from the project root):

```
docker build -t iris-airflow:latest .
```

2) Run the container. Provide the Postgres connection and (optionally) MLflow tracking URI via environment variables. Airflow will start in standalone mode on port 8080.

Minimal example (SQLite metadata, external Postgres for the DAG tasks via Airflow connection env var):

```
docker run --rm -it -p 8080:8080 \
  -e AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=False \
  -e AIRFLOW_CONN_POSTGRES_DEFAULT=postgresql+psycopg2://USER:PASSWORD@HOST:5432/DBNAME \
  -e MLFLOW_TRACKING_URI=http://mlflow:5000 \
  -e MODEL_TYPE=logreg \
  -e TEST_SIZE=0.2 \
  -e RANDOM_STATE=42 \
  -e EXPERIMENT_NAME=IrisClassifier \
  -e IRIS_TABLE=iris_data \
  -e EVAL_TABLE=iris_evaluation \
  --name iris-airflow iris-airflow:latest
```

Notes:
- Access the UI at http://localhost:8080. The image creates an admin user `admin`/`admin` on first start.
- The DAG will appear as `iris_mlflow_training_dag`. Enable it and trigger a run.
- `AIRFLOW_CONN_POSTGRES_DEFAULT` sets the `postgres_default` connection used by the DAG.
- If you prefer a persistent Airflow metadata DB (instead of SQLite), configure `AIRFLOW__DATABASE__SQL_ALCHEMY_CONN` accordingly and consider using Docker Compose with a Postgres service for Airflow metadata.

Airflow Connections and Variables

- Create an Airflow connection named `postgres_default` (or adjust `DEFAULT_CONN_ID` in the DAG):
  - Conn Type: `Postgres`
  - Host, Schema (database), Login, Password, Port

- (Optional) Set the MLflow Tracking URI via environment variable (preferred in this refactor):
  - `MLFLOW_TRACKING_URI` (e.g., `http://mlflow:5000`).
  - The SOLID `config.py` reads all settings from environment variables. Defaults are provided in the Dockerfile and can be overridden via `-e` flags.

Environment variables (read at runtime by `dags/iris_pipeline/config.py`):
- `POSTGRES_CONN_ID` (default: `postgres_default`) — Airflow connection ID used by `PostgresHook`.
- `IRIS_TABLE` (default: `iris_data`)
- `EVAL_TABLE` (default: `iris_evaluation`)
- `EXPERIMENT_NAME` (default: `IrisClassifier`)
- `MODEL_TYPE` (default: `logreg`, options: `logreg`, `rf`)
- `TEST_SIZE` (default: `0.2`)
- `RANDOM_STATE` (default: `42`)
- `MLFLOW_TRACKING_URI` (optional)

Tables

The DAG creates tables if they don't exist:
- `iris_data`
- `iris_evaluation`

DAG Details

- DAG ID: inferred from file as `iris_mlflow_training_dag`
- Schedule: `*/10 * * * *` (every 10 minutes)
- TaskGroups and tasks:
  - `ingestion`:
    - `create_iris_table` — ensure required tables exist (idempotent).
    - `ingest_iris` — load Iris, transform, write to `iris_data`.
  - `training`:
    - `load_data` — read `iris_data` from Postgres.
    - `fit` — train selected model and serialize it to disk (path passed via XCom).
  - `evaluation`:
    - `compute` — compute accuracy, precision (weighted), recall (weighted) and save confusion matrix to CSV.
    - `log_mlflow` — optional MLflow logging (NoOp if no tracking URI).
    - `persist` — write metrics into `iris_evaluation` with `execution_date`.

Model selection (parameter `model_type`):
- `logreg` (default): `LogisticRegression(max_iter=400)`
- `rf`: `RandomForestClassifier(random_state=42)`

Running the DAG

1. Place this repository (or at least the `dags/` directory) where your Airflow instance loads DAGs.
2. Ensure the `postgres_default` connection is configured.
3. (Optional) Set `MLFLOW_TRACKING_URI`.
4. Start Airflow webserver and scheduler.
5. In the Airflow UI, enable and trigger the DAG `iris_mlflow_training_dag`.

Outputs

- PostgreSQL tables populated:
  - `iris_data` — raw features + labels + `ingestion_date`.
  - `iris_evaluation` — `run_id` (if MLflow run succeeded), `accuracy`, `precision_weighted`, `recall_weighted`, `execution_date`.
- MLflow experiment `IrisClassifier` with:
  - Parameters: model type, hyperparameters.
  - Metrics: accuracy, precision (weighted), recall (weighted).
  - Artifacts: serialized model, confusion matrix CSV, `features.txt`.

Configuration Notes

- To switch to RandomForest, set `MODEL_TYPE=rf` in the container env.
- The DAG uses SQLAlchemy engine from `PostgresHook` for convenient DataFrame I/O via `pandas.to_sql`.
- MLflow errors do not fail the DAG; they are captured and the pipeline continues.

Troubleshooting

- Missing modules (e.g., pandas, sklearn, mlflow) — install `requirements.txt` into the same environment running Airflow workers.
- Permission/DDL issues — ensure the Postgres user has privileges to create tables and insert data.
- MLflow not reachable — verify `MLFLOW_TRACKING_URI` is correct and network is open. The DAG will continue without MLflow if unreachable.

- Where do MLflow log messages appear? The message
  "MLflow logging: tracking_uri=..., experiment=..." is emitted by the Airflow
  task `evaluation.log_mlflow`, so you will see it in the Airflow container task logs
  (Airflow UI → DAG run → Task `evaluation.log_mlflow` → Log). It will not appear
  in the MLflow container logs. Additionally, just before logging, the task prints a
  preflight line: "About to log to MLflow from Airflow task: tracking_uri=..., experiment=..."
  to make the integration point explicit.

MLflow experiment visibility

- This pipeline logs to the experiment name defined by `EXPERIMENT_NAME` (default: `IrisClassifier`).
- Ensure the Airflow container has `MLFLOW_TRACKING_URI` set to the MLflow server URL (in docker-compose it is `http://mlflow:5000`).
- If you only see the `Default` experiment in the MLflow UI:
  - Confirm the Airflow logs of the `evaluation.log_mlflow` task show a line like: `MLflow logging: tracking_uri=http://mlflow:5000, experiment=IrisClassifier`.
  - Make sure you are looking at the same MLflow server configured in `MLFLOW_TRACKING_URI`.
  - Trigger a DAG run and refresh the MLflow UI; the experiment will be created automatically if it doesn't exist.

MLflow Host header warning

- If you see a warning like `Rejected request with invalid Host header: mlflow:5000` in the MLflow container logs, or HTTP 403 from the MLflow API when Airflow calls it, the server is enforcing allowed hosts.
- This repo's docker-compose sets `MLFLOW_TRACKING_SERVER_ALLOWED_HOSTS` to include both bare hostnames and host:port variants:
  - `mlflow,localhost,127.0.0.1,mlflow:5000,localhost:5000,127.0.0.1:5000`
  This covers calls originating within the Docker network (host `mlflow`) and from your browser on localhost, including the explicit port 5000 which some MLflow versions validate strictly.
- If you access the MLflow UI via a different hostname or port, add it (and its host:port form) to the list under the MLflow service's environment in `docker-compose.yml` and restart the service.

Security and rate‑limit warnings

- Airflow cryptography key: If you see "empty cryptography key - values will not be stored encrypted", set a Fernet key. This repo's docker-compose sets a dev key via `AIRFLOW__CORE__FERNET_KEY`. For production, override it with your own secure key: `openssl rand -base64 32` and place it in an environment variable or secret.
- Flask-Limiter storage: Airflow’s webserver uses Flask-Limiter. By default it warns when using in-memory storage. This compose sets `RATELIMIT_STORAGE_URI=memory://` to silence the warning for local dev. For production, configure a shared backend, e.g. Redis: `RATELIMIT_STORAGE_URI=redis://redis:6379/0`.

Testing (unit tests)

- Install dev dependency `pytest` (already in `requirements.txt`).
- From the project root, run:

```
pytest -q
```

The tests cover:
- `metrics.py` — correctness of basic metric computations.
- `ingest.py` — column renaming and `ingestion_date` normalization.
- `train.py` — model selection/logreg vs rf and expected outputs.
- `mlflow_utils.py` — NoOp logger behavior without a tracking server.

Docker tips

- If your code changes frequently, rebuild with `--no-cache` or keep `requirements.txt` stable to leverage layer caching.
- Add or adjust environment variables using `-e` flags in `docker run` as needed.

Run Airflow UI manually (like "mlflow ui")

You can bring up the Airflow web UI with a single command, similar to running `mlflow ui`.

Option A — using Docker Compose directly:
- Start: `docker compose up -d airflow`
- Open: http://localhost:8080 (default credentials: admin / admin)
- Stop: `docker compose down` (stops all services)

Option B — one‑liner scripts in scripts/:
- Windows (PowerShell): `./scripts/airflow-ui.ps1`
- macOS/Linux (bash): `bash ./scripts/airflow-ui.sh`

Notes:
- The Airflow container depends on Postgres and MLflow defined in docker-compose.yml; they will be started automatically if not running.
- The image initializes an admin user on first run. Credentials: admin / admin.

Readiness and health checks

- The docker-compose defines a healthcheck for the Airflow webserver using the HTTP endpoint `http://localhost:8080/health`. The service is marked healthy only when the UI is actually reachable.
- The helper scripts (`scripts/airflow-ui.sh` and `scripts/airflow-ui.ps1`) wait until the health endpoint returns HTTP 200 (up to 3 minutes) before printing the UI URL. If it times out, use `docker compose logs -f airflow` to investigate.
