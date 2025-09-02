# syntax=docker/dockerfile:1

# Chọn base image Python tối giản cho runtime nhỏ gọn
FROM python:3.12-slim

# Tắt tạo .pyc và bật log không buffer (đẩy log ra stdout ngay lập tức)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Cài các gói hệ thống cần thiết cho build dependencies
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    gcc \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Đặt thư mục làm việc trong container
WORKDIR /app

# Cài dependency Python trước để tận dụng cache khi code thay đổi
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn vào container
COPY . .

# Đảm bảo script entrypoint có quyền thực thi và có line endings đúng
RUN chmod +x /app/entrypoint.sh && \
    dos2unix /app/entrypoint.sh 2>/dev/null || true

# Tạo thư mục cho static và media files
RUN mkdir -p /static /media

# Thiết lập các biến môi trường cho Django
ENV DJANGO_SETTINGS_MODULE=BE_BLOG.settings

# Mở cổng 8000 (Gunicorn sẽ lắng nghe ở cổng này)
EXPOSE 8000

# Điểm vào container: chạy script entrypoint để migrate, collectstatic và start Gunicorn
ENTRYPOINT ["/app/entrypoint.sh"]

