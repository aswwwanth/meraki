#!/usr/bin/env bash

# running the server
if [ "$ENV" = "prod" ]; then
    
    # database migrations
    flask db init --directory /migrations
    flask db migrate --directory /migrations
    flask db upgrade --directory /migrations

    service nginx start
    gunicorn --worker-class eventlet -w 1 --bind unix:meraki.sock -u www-data -m 007 wsgi:app
else
    # database migrations
    flask db init
    flask db migrate
    flask db upgrade

    python3 meraki.py
fi