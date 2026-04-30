#!/bin/sh
set -eu

python manage.py migrate --noinput
python scripts/bootstrap.py

exec python manage.py runserver 0.0.0.0:8000

