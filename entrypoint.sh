#!/usr/bin/env sh
# Dừng script ngay khi có lệnh lỗi
set -e

# Thiết lập giá trị mặc định cho biến môi trường nếu chưa được truyền vào
: "${DJANGO_SETTINGS_MODULE:=BE_BLOG.settings}"
: "${WEB_CONCURRENCY:=3}"
: "${PORT:=8000}"

# Chạy migrate để áp dụng các thay đổi database trước khi start server
python manage.py migrate --noinput
# Gom toàn bộ static files về STATIC_ROOT để Nginx có thể phục vụ trực tiếp
python manage.py collectstatic --noinput

# Khởi động Gunicorn phục vụ ứng dụng Django
exec gunicorn BE_BLOG.wsgi:application \
  --bind 0.0.0.0:${PORT} \
  --workers ${WEB_CONCURRENCY} \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
