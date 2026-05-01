#!/bin/sh
set -eu

python scripts/wait_for_db.py
python manage.py migrate --noinput
python scripts/bootstrap.py

exec python manage.py runserver 0.0.0.0:8000

