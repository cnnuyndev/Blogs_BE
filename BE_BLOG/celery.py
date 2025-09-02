"""
Celery configuration cho Django project BE_BLOG.
Celery là message broker để xử lý các tác vụ nền (background tasks) như gửi email.
"""

import os
from celery import Celery

# Thiết lập Django settings module cho Celery
# Celery cần biết Django settings để có thể import models, settings, etc.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BE_BLOG.settings")

# Tạo Celery app instance
# Tên "BE_BLOG" sẽ được dùng làm prefix cho task names
app = Celery("BE_BLOG")

# Cấu hình Celery từ Django settings
# namespace="CELERY" nghĩa là Celery sẽ tìm các setting bắt đầu bằng CELERY_
# Ví dụ: CELERY_BROKER_URL, CELERY_RESULT_BACKEND, etc.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Tự động tìm và đăng ký tasks từ tất cả Django apps
# Celery sẽ scan tất cả apps trong INSTALLED_APPS và tìm file tasks.py
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """
    Task mẫu để test Celery hoạt động.
    Có thể gọi: debug_task.delay() từ Django shell hoặc view.
    """
    print(f"Request: {self.request!r}")
    return "Celery is working!"
