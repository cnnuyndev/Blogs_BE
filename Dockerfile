FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    build-essential \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# App code
COPY . /app

# Collect static
RUN mkdir -p /app/static /app/media && \
    chmod -R 755 /app/static /app/media && \
    python manage.py collectstatic --no-input

# Nginx config
# Remove default Nginx site and use our config
RUN rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf || true
COPY nginx.conf /etc/nginx/conf.d/app.conf

# Supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80

CMD ["/usr/bin/supervisord", "-n"]

