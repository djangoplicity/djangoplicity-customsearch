FROM python:2.7-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    gcc \
    git \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    python-dev

RUN mkdir /app
WORKDIR /app

ENV DJANGO_SETTINGS_MODULE tests.testapp.settings

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY scripts/ scripts/
RUN chmod +x scripts/command-dev.sh
COPY djangoplicity/ djangoplicity/
COPY tests/ tests/
COPY setup.cfg .