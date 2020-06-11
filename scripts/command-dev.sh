#!/bin/sh

python tests/testapp/manage.py migrate
python tests/testapp/manage.py runserver 0.0.0.0:8000