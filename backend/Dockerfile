# Backend Dockerfile - Django ASGI + Gunicorn + Uvicorn
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install poetry (optional) and pip tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements placeholder and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt || true

# Copy project
COPY . /app

EXPOSE 8000

CMD ["gunicorn", "--workers=3", "--timeout", "120", "--bind", "0.0.0.0:8000", "config.asgi:application", "-k", "uvicorn.workers.UvicornWorker"]