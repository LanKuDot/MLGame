# ===== Step 1: Build the base image =====
FROM python:3.6.8-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /tmp/
COPY requirements-ml.txt /tmp/

RUN apt-get update \
    && apt-get install -y gcc build-essential \
    && pip install -r /tmp/requirements.txt \
    && pip install -r /tmp/requirements-ml.txt \
    && pip install channels_redis==2.3.3 \
    && rm -r /root/.cache/pip \
    && apt-get remove -y --purge gcc build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# ===== Step 2: Build the application =====
FROM base

RUN adduser --system --group --no-create-home --uid 1000 appuser

# Set working directory
WORKDIR /app
RUN chown appuser:appuser /app/

# Copy project
COPY --chown=appuser:appuser . /app/

USER appuser
