#!/bin/sh
# Stop script on error
set -e

# Set default environment variables
: "${DJANGO_SETTINGS_MODULE:=BE_BLOG.settings}"
: "${WEB_CONCURRENCY:=3}"
: "${PORT:=8000}"

echo "Starting Django application..."

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Check if running Celery worker
if [ "$1" = "celery" ]; then
    echo "Starting Celery worker..."
    exec celery -A BE_BLOG worker --loglevel=info
elif [ "$1" = "celery-beat" ]; then
    echo "Starting Celery beat..."
    exec celery -A BE_BLOG beat --loglevel=info
else
    # Start Gunicorn server
    echo "Starting Gunicorn server..."
    exec gunicorn BE_BLOG.wsgi:application \
        --bind 0.0.0.0:${PORT} \
        --workers ${WEB_CONCURRENCY} \
        --timeout 120 \
        --access-logfile - \
        --error-logfile - \
        --preload
fi
