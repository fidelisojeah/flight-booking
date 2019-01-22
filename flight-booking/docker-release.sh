#!/usr/bin/env bash

python manage.py migrate
python manage.py upload-default-image
if [ "x$DJANGO_MANAGEPY_FIX_PERMISSIONS" = 'xon' ]; then
    python manage.py fix-permissions
fi
