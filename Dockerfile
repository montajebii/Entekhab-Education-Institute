FROM python:3.13-slim

WORKDIR /app

# نصب وابستگی‌های سیستم
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# کپی فایل‌های پروژه
COPY . .

# نصب وابستگی‌های Python
RUN pip install --no-cache-dir -e .

# تنظیم متغیرهای محیطی
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# اجرای ربات
CMD ["python", "main.py"] 