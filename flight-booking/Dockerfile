FROM python:3.6.6

RUN apt-get update && apt-get install -y mysql-client && rm -rf /var/lib/apt

ENV PYTHONUNBUFFERED 1

ENV PROJECT_ROOT /app

COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

RUN mkdir /app

WORKDIR /app

EXPOSE 8000

COPY . /app

CMD ["gunicorn", "app.wsgi", "--bind 0.0.0.0:$PORT"]
