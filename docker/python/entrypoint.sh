#!/usr/bin/env bash
python manage.py wait_for_db
python manage.py makemigrations
python manage.py migrate

CONTAINER_ALREADY_STARTED=".CONTAINER_ALREADY_STARTED_PLACEHOLDER"
if [ ! -e $CONTAINER_ALREADY_STARTED ]; then
  touch $CONTAINER_ALREADY_STARTED
  echo "-- First container startup --"
  python manage.py create_custom_admin --email $DJANGO_ADMIN_EMAIL --password $DJANGO_ADMIN_PASS
  python manage.py load_clients --filename=clients.csv
else
  echo "-- Not first container startup --"
fi

python manage.py collectstatic --noinput

exec "$@"
