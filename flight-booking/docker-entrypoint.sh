#!/bin/sh

while ! mysqladmin ping -h $MYSQL_DB_HOST --silent; do
>&2 echo "Waiting for Mysql server - sleeping"
    sleep 1
done
mysqladmin ping -h $MYSQL_DB_HOST

>&2 echo "MySQL Up and running"

if [ "x$DJANGO_MANAGEPY_MIGRATE" = 'xon' ]; then
    python manage.py migrate --noinput
fi

exec "$@"
