#!/bin/bash

set -e

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating admin superuser if needed..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model

User = get_user_model()

username = "admin"
password = "admin"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        password=password,
    )
    print("Superuser created.")
else:
    print("Superuser already exists. Skipping.")
EOF

echo "Deployment setup complete."