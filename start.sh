#!/usr/bin/env bash
set -o errexit

echo "=== Running migrations ==="
python manage.py migrate --noinput

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

echo "=== Seeding database ==="
python seed.py

echo "=== Starting server ==="
gunicorn hospital_mgmt.wsgi:application --bind 0.0.0.0:${PORT:-8000}
