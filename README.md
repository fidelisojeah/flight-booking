# flight-booking

[![CircleCI](https://circleci.com/gh/fidelisojeah/flight-booking.svg?style=svg)](https://circleci.com/gh/fidelisojeah/flight-booking)
Flight Booking Application

## Installation and configuration

### In a Development Environment

Before you install:

Ensure you have RabbitMQ up and running on your computer (You could use Redis or both together with Redis as your backend)

Ensure you have MySQL up and running on your computer and create a new database schema and new user with a password and login

> The Name of the database, user and password must be consitient with what is used in your [environment variables]  (in-a-development-environment)

You also need a Cloudinary account (for data uploads): You can sign up using [THIS LINK](<https://cloudinary.com/invites/lpov9zyyucivvxsnalc5/e0e7v3bfqbzsn0jhxkjy>)

For Installation in a development environment, check the docs at [Flight-booking Installation in a development environment](flight-booking)

### In a Production Environment

- You need docker installed on your machine

- Set up Environment Variables

> Below are environment variables needed for the application

```env
APP_SECRET_KEY
MYSQL_DATABASE
MYSQL_ROOT_PASSWORD
MYSQL_USER
MYSQL_PASSWORD
CLOUDINARY_URL
CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT
CELERY_TASK_SERIALIZER
CELERY_RESULT_SERIALIZER
CELERY_TIMEZONE

```

If you have REDIS as your backend, include the `REDIS_URL` in your environment variables

- run with docker

```bash
docker-compose up --build
```

## Runnning

To run the application:

### In a development environment

- create a `.env` file in the [flight-booking](flight-booking) directory
> the root directory of main python application: manage.py can be found here

- add the following environment environment variables:

```env
DEBUG=on
SECRET
MYSQL_USER
MYSQL_DATABASE
MYSQL_PASSWORD
MYSQL_DB_HOST
CLOUDINARY_URL
CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT
CELERY_TASK_SERIALIZER
CELERY_RESULT_SERIALIZER
CELERY_TIMEZONE
```

> Sample of these can be found in the [example](flight-booking/.env.sample)

- Run any pending migrations:

```bash
python manage.py migrate
```

- Start the server

```bash
python manage.py runserver
```


### To test the application

Simply run python tests

```bash
python manage.py test
```
