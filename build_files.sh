#!/usr/bin/env bash

echo "Build packages"
python3 -m pip install --break-system-packages -r requirements.txt

cd knockdown/

echo "Migrating database"
python3 manage.py makemigrations
python3 manage.py migrate

echo "Collecting static files"
python3 manage.py collectstatic --noinput

echo "Populating dictionary"
python3 scripts/populate_dictionary.py