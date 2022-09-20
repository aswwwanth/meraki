#!/usr/bin/env bash

# database migrations
flask db init
flask db migrate
flask db upgrade

# running the server
if [ "$ENV" = "prod" ]; then
    service nginx start
    gunicorn --worker-class eventlet -w 1 --bind unix:meraki.sock -u www-data -m 007 wsgi:app
else 
    python3 meraki.py
fi