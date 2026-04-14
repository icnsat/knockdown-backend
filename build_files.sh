#!/usr/bin/env bash

echo "Build packages"
python3.14 -m pip install --break-system-packages -r requirements.txt

cd knockdown/

echo "Making migrations"
python3.14 manage.py makemigrations users
python3.14 manage.py makemigrations lessons
python3.14 manage.py makemigrations stats
python3.14 manage.py makemigrations

echo "Migrating database"
python3.14 manage.py migrate users
python3.14 manage.py migrate lessons
python3.14 manage.py migrate stats
python3.14 manage.py migrate

echo "Collecting static files"
python3.14 manage.py collectstatic --noinput --clear

echo "Populating dictionary"
python3.14 scripts/populate_dictionary.py
