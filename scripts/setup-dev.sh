#!/bin/bash
set -euo pipefail

echo "=== NAS Cloud Development Setup ==="

# EC2 setup
echo ""
echo "--- EC2 (Django/DRF) ---"
cd "$(dirname "$0")/../ec2"

if [ ! -f .env ]; then
    cp .env.example .env
    echo "[EC2] .env created from .env.example"
else
    echo "[EC2] .env already exists, skipping"
fi

echo "[EC2] Building and starting containers..."
docker compose up -d --build

echo "[EC2] Waiting for DB..."
sleep 5

echo "[EC2] Running migrations..."
docker compose exec web python manage.py migrate

echo "[EC2] Creating superuser (skip if exists)..."
docker compose exec web python manage.py createsuperuser --noinput 2>/dev/null || echo "[EC2] Superuser already exists or DJANGO_SUPERUSER_* env vars not set"

echo "[EC2] Django ready at http://localhost:80"
echo "[EC2] Admin at http://localhost:80/admin/"

# NAS setup
echo ""
echo "--- NAS (FastAPI) ---"
cd "$(dirname "$0")/../nas"

if [ ! -f .env ]; then
    cp .env.example .env
    echo "[NAS] .env created from .env.example"
else
    echo "[NAS] .env already exists, skipping"
fi

echo "[NAS] Building and starting containers..."
docker compose up -d --build

echo "[NAS] Waiting for DB..."
sleep 5

echo "[NAS] Running Alembic migrations..."
docker compose exec api alembic upgrade head 2>/dev/null || echo "[NAS] Alembic migrations skipped (no migrations yet)"

echo "[NAS] FastAPI ready at http://localhost:8001"
echo "[NAS] Health check: http://localhost:8001/health"
echo "[NAS] API docs: http://localhost:8001/docs"

echo ""
echo "=== Setup Complete ==="
echo "EC2 Django: http://localhost:80"
echo "NAS FastAPI: http://localhost:8001"
