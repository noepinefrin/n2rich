#!/bin/ash

echo "Applying database migrations"

python manage.py makemigrations enrichment
python manage.py migrate

exec "$@"