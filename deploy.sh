#!/bin/bash

set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating admin superuser if needed..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model

User = get_user_model()

email = "admin@gmail.com"
password = "admin"
username = "admin"

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        username=username,
        password=password,
    )
    print("Superuser created.")
else:
    print("Superuser already exists. Skipping.")
EOF

echo "Deployment setup complete."