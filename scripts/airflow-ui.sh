#!/usr/bin/env bash
set -euo pipefail

# Change to repo root (parent of this scripts directory)
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "${SCRIPT_DIR}/.."

echo "Starting Airflow (and dependencies) with Docker Compose..."
docker compose up -d airflow

echo
echo "Waiting for Airflow webserver to become ready (health endpoint)..."
READY_URL="http://localhost:8080/health"
MAX_WAIT=180
SLEEP=3
ELAPSED=0
until curl -fsS "$READY_URL" >/dev/null 2>&1; do
  if (( ELAPSED >= MAX_WAIT )); then
    echo "Airflow webserver not ready after ${MAX_WAIT}s. Check logs: docker compose logs -f airflow" >&2
    exit 1
  fi
  sleep $SLEEP
  ELAPSED=$((ELAPSED + SLEEP))
done

echo "Airflow is ready. Open:"
echo "  http://localhost:8080"
echo
echo "Default credentials (first run): admin / admin"
