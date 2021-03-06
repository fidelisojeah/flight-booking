# flight-booking

[![CircleCI](https://circleci.com/gh/fidelisojeah/flight-booking.svg?style=svg)](https://circleci.com/gh/fidelisojeah/flight-booking)

Flight Booking Application

API at: [https://flight-booking-lms.herokuapp.com](<https://flight-booking-lms.herokuapp.com>)

## Installation and configuration

### In a Development Environment

Before you install:

Ensure you have RabbitMQ up and running on your computer (You could use Redis or both together with Redis as your backend)

Ensure you have MySQL or PostgreSQL up and running on your computer and create a new database schema and new user with a password and login

> The Name of the database, user and password must be consitient with what is used in your [environment variables]  (in-a-development-environment)

You also need a Cloudinary account (for data uploads): You can sign up using [THIS LINK](<https://cloudinary.com/invites/lpov9zyyucivvxsnalc5/e0e7v3bfqbzsn0jhxkjy>)

For Installation in a development environment, check the docs at [Flight-booking Installation in a development environment](flight-booking)

### In a Production Environment

- You need docker installed on your machine

- Set up Environment Variables

> Below are environment variables needed for the application

```env
APP_SECRET_KEY
DATABASE_URL
CLOUDINARY_URL
CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT
CELERY_TASK_SERIALIZER
CELERY_RESULT_SERIALIZER
CELERY_TIMEZONE
EMAIL_SERVER
EMAIL_PORT defaults to 587
EMAIL_USERNAME
EMAIL_PASSWORD

EMAIL_DOMAIN_URL
BUGSNAG_API_KEY
```

Include the `BUGSNAG_API_KEY` if tracking application errors

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
APP_URL
DEBUG=on
SECRET
DATABASE_URL
CLOUDINARY_URL
CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT
CELERY_TASK_SERIALIZER
CELERY_RESULT_SERIALIZER
CELERY_TIMEZONE
EMAIL_SERVER
EMAIL_PORT defaults to 587
EMAIL_USERNAME
EMAIL_PASSWORD

EMAIL_DOMAIN_URL
BUGSNAG_API_KEY
```

You likely want to use a mail trap for your development environment

`DATABASE_URL` can be: `postgres://<username>:<password@>host>:<port>/schema`

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
