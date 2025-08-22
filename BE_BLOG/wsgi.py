"""
WSGI config for BE_BLOG project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BE_BLOG.settings')

application = get_wsgi_application()

# Ensure MEDIA_ROOT exists at runtime (useful on Render persistent disk)
try:
    from django.conf import settings
    media_root = Path(settings.MEDIA_ROOT)
    media_root.mkdir(parents=True, exist_ok=True)
except Exception:
    pass
