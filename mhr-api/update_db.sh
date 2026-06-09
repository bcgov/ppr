#! /bin/sh
set -e

echo 'starting upgrade'
poetry run python manage.py db upgrade
echo 'upgrade completed'