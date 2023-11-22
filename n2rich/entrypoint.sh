#!/bin/sh

echo "Applying database migrations"

python manage.py makemigrations
python manage.py makemigrations enrichment
python manage.py migrate

exec "$@"