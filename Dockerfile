# syntax=docker/dockerfile:1

# Base image: Apache Airflow official image
# Choose a recent stable version compatible with your environment
FROM apache/airflow:2.9.3-python3.11

USER root

# Install OS packages you might need (kept minimal). Uncomment if needed.
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#  && rm -rf /var/lib/apt/lists/*

USER airflow

WORKDIR /opt/airflow

# Copy only requirements first to leverage Docker layer caching
COPY --chown=airflow:airflow requirements.txt /opt/airflow/requirements.txt

# Install Python dependencies into the Airflow image
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt

# Copy DAGs last (they change more often)
COPY --chown=airflow:airflow dags/ /opt/airflow/dags/

# Recommended envs
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False \
    AIRFLOW__CORE__EXECUTOR=SequentialExecutor

# Pipeline runtime settings (override at `docker run -e ...`)
# These are read by our SOLID-configured modules via environment variables.
ENV POSTGRES_CONN_ID=postgres_default \
    IRIS_TABLE=iris_data \
    EVAL_TABLE=iris_evaluation \
    EXPERIMENT_NAME=IrisClassifier \
    MODEL_TYPE=logreg \
    TEST_SIZE=0.2 \
    RANDOM_STATE=42

# Expose Airflow Webserver port
EXPOSE 8080

# Default command: run a single-container demo with webserver + scheduler
# For production, use docker-compose or Kubernetes with dedicated scheduler/webserver.
CMD ["bash", "-lc", "airflow db migrate && airflow users create --role Admin --username admin --password admin --firstname Air --lastname Flow --email admin@example.com || true; exec airflow standalone"]
