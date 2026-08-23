#!/bin/sh
set -eu

python backend/manage.py check --deploy
python backend/manage.py migrate --noinput
python backend/manage.py collectstatic --noinput
exec gunicorn config.wsgi:application \
  --chdir backend \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout "${GUNICORN_TIMEOUT:-60}" \
  --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(m)s %(U)s %(H)s" %(s)s %(b)s "%(f)s" "%(a)s"' \
  --access-logfile - \
  --error-logfile -
