#!/usr/bin/env bash

python manage.py migrate
python manage.py upload-default-image
