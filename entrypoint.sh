#!/usr/bin/env bash
flask db init
flask db migrate
flask db upgrade
python meraki.py