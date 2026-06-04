#!/bin/sh
set -e

# Ensure Django runtime directories exist and are writable.
mkdir -p /app/static /app/media
chown -R appuser:appuser /app/static /app/media
chmod -R 755 /app/static /app/media

echo "Waiting for database to be ready..."
until python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings'); from django.db import connections; connections['default'].cursor();" > /dev/null 2>&1; do
  sleep 2
  echo "Still waiting for database..."
done

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gosu appuser "$@"
