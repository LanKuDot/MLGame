FROM python:3.6.8-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN adduser --system --group --no-create-home --uid 1000 appuser

# Set working directory
WORKDIR /app
RUN chown appuser:appuser /app/

# Copy project
COPY --chown=appuser:appuser . /app/

RUN apt-get update \
    && apt-get install -y gcc build-essential \
    && pip install -r requirements.txt \
    && pip install -r requirements-ml.txt \
    && pip install channels_redis==2.3.3 \
    && rm -r /root/.cache/pip \
    && apt-get remove -y --purge gcc build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

USER appuser
