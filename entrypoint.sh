#!/bin/sh

if [ "$DB_ENGINE" = "django.db.backends.mysql" ]; then
    echo "Waiting for mysql..."
    # Simple wait since we don't have netcat installed by default, 
    # optionally we could install netcat, or let it crash and restart.
    sleep 10
fi

echo "Applying database migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

exec "$@"