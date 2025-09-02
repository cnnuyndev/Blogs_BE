# BE_BLOG - Django Blog Backend

A Django REST API backend for a blog application with Celery, Redis, and Nginx.

## Features

- Django REST Framework API
- JWT Authentication
- Celery for background tasks
- Redis for caching and message broker
- Nginx reverse proxy
- Docker containerization
- Email verification system

## Prerequisites

- Docker
- Docker Compose

## Quick Start

### 1. Clone the repository
```bash
git clone <repository-url>
cd BE_BLOG
```

### 2. Set up environment variables
```bash
cp env.example .env
# Edit .env file with your configuration
```

### 3. Build and run with Docker Compose

#### For Production:
```bash
docker-compose up --build
```

#### For Development:
```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build
```

### 4. Access the application
- API: http://localhost
- Admin: http://localhost/admin/

## Services

### Web (Django)
- **Port**: 8000 (internal), 80 (external via Nginx)
- **Description**: Django application with Gunicorn WSGI server

### Celery Worker
- **Description**: Processes background tasks
- **Dependencies**: Redis, Web

### Celery Beat
- **Description**: Scheduler for periodic tasks
- **Dependencies**: Redis, Web

### Redis
- **Port**: 6379 (internal)
- **Description**: Message broker and cache backend

### Nginx
- **Port**: 80 (external)
- **Description**: Reverse proxy and static file server

## Environment Variables

### Required
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to False for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

### Optional
- `REDIS_URL`: Redis connection URL (default: redis://redis:6379/1)
- `CELERY_BROKER_URL`: Celery broker URL (default: redis://redis:6379/1)
- `CELERY_RESULT_BACKEND`: Celery result backend (default: redis://redis:6379/1)
- `EMAIL_HOST_USER`: SMTP email username
- `EMAIL_HOST_PASSWORD`: SMTP email password

## Development

### Running locally without Docker
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp env.example .env
# Edit .env file

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run Celery worker (in another terminal)
celery -A BE_BLOG worker --loglevel=info

# Run Celery beat (in another terminal)
celery -A BE_BLOG beat --loglevel=info
```

### Running tests

#### Using Django test runner:
```bash
python manage.py test
```

#### Using pytest (recommended):
```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py --unit          # Unit tests only
python run_tests.py --integration   # Integration tests only
python run_tests.py --api           # API tests only
python run_tests.py --celery        # Celery tests only

# Run with coverage
python run_tests.py --coverage

# Run specific test file
python run_tests.py --path tests/api/test_registration.py

# Run tests with specific markers
python run_tests.py --markers "slow"
```

#### Test Structure:
```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures
├── unit/                    # Unit tests
│   ├── test_models.py
│   ├── test_serializers.py
│   └── test_celery_tasks.py
├── integration/             # Integration tests
│   └── test_blog_workflow.py
└── api/                     # API tests
    └── test_registration.py
```

## Production Deployment

### 1. Set production environment variables
```bash
DEBUG=False
SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

### 2. Build and run
```bash
docker-compose -f docker-compose.yml up --build -d
```

### 3. Create superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

### 4. Monitor logs
```bash
docker-compose logs -f
```

## API Endpoints

- `/api/` - API root
- `/admin/` - Django admin interface
- `/health/` - Health check endpoint

## Celery Tasks

Celery is configured to handle background tasks such as:
- Email sending
- File processing
- Scheduled tasks

### Running Celery commands
```bash
# Check Celery status
docker-compose exec web celery -A BE_BLOG inspect active

# Monitor Celery tasks
docker-compose exec web celery -A BE_BLOG monitor

# Purge all tasks
docker-compose exec web celery -A BE_BLOG purge
```

## Troubleshooting

### Common Issues

1. **Database migrations not applied**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

2. **Static files not collected**
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

3. **Celery worker not starting**
   - Check Redis connection
   - Verify Celery configuration in settings.py

4. **Permission denied on entrypoint.sh**
   ```bash
   chmod +x entrypoint.sh
   ```

5. **Line endings error (Windows)**
   ```powershell
   # Run PowerShell script to fix line endings
   .\fix-line-endings.ps1
   
   # Or manually convert using Git
   git config core.autocrlf false
   git add --renormalize .
   ```

### Logs
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs web
docker-compose logs celery
docker-compose logs redis
docker-compose logs nginx
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.