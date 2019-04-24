FROM python:3.6.8-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Copy project
COPY . /app/

RUN apt-get update \
    && apt-get install -y gcc build-essential \
    && pip install -r requirements.txt \
    && pip install -r requirements-ml.txt \
    && pip install channels_redis==2.3.3 \
    && rm -r /root/.cache/pip \
    && apt-get remove -y --purge gcc build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
