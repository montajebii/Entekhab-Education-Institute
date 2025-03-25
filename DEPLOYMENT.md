# راهنمای استقرار

## پیش‌نیازها

### سخت‌افزار
- CPU: حداقل 2 هسته
- RAM: حداقل 4GB
- فضای ذخیره‌سازی: حداقل 20GB SSD

### نرم‌افزار
- Python 3.8 یا بالاتر
- PostgreSQL 12 یا بالاتر
- Redis 6 یا بالاتر
- Nginx
- Docker (اختیاری)

## روش‌های استقرار

### 1. استقرار مستقیم

#### نصب وابستگی‌ها
```bash
# ایجاد محیط مجازی
python -m venv venv

# فعال‌سازی محیط مجازی
# در ویندوز:
venv\Scripts\activate
# در لینوکس:
source venv/bin/activate

# نصب وابستگی‌ها
pip install -r requirements.txt
```

#### تنظیمات محیطی
1. فایل `.env.example` را به `.env` کپی کنید
2. مقادیر را تنظیم کنید:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
```

#### تنظیم پایگاه داده
```bash
# ایجاد پایگاه داده
createdb dbname

# اجرای مهاجرت‌ها
python manage.py migrate
```

#### اجرای برنامه
```bash
# اجرای مستقیم
python main.py

# یا با استفاده از Gunicorn
gunicorn main:app --workers 4 --bind 0.0.0.0:8000
```

### 2. استقرار با Docker

#### ساخت تصویر
```bash
docker build -t entekhab-task-manager .
```

#### اجرای کانتینر
```bash
docker run -d \
  --name entekhab-task-manager \
  -p 8000:8000 \
  -e TELEGRAM_BOT_TOKEN=your_bot_token \
  -e DATABASE_URL=postgresql://user:password@db:5432/dbname \
  -e REDIS_URL=redis://redis:6379/0 \
  entekhab-task-manager
```

#### استفاده از Docker Compose
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - TELEGRAM_BOT_TOKEN=your_bot_token
      - DATABASE_URL=postgresql://user:password@db:5432/dbname
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:12
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=dbname
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 3. استقرار با Nginx

#### تنظیم Nginx
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## نظارت و نگهداری

### 1. لاگ‌ها
- بررسی لاگ‌های برنامه: `tail -f logs/app.log`
- بررسی لاگ‌های Nginx: `tail -f /var/log/nginx/access.log`
- بررسی لاگ‌های سیستم: `journalctl -u entekhab-task-manager`

### 2. پشتیبان‌گیری
```bash
# پشتیبان‌گیری از پایگاه داده
pg_dump dbname > backup.sql

# پشتیبان‌گیری از فایل‌های برنامه
tar -czf app_backup.tar.gz /path/to/app
```

### 3. به‌روزرسانی
```bash
# دریافت آخرین تغییرات
git pull origin main

# نصب وابستگی‌های جدید
pip install -r requirements.txt

# اجرای مهاجرت‌ها
python manage.py migrate

# راه‌اندازی مجدد سرویس
systemctl restart entekhab-task-manager
```

## امنیت

### 1. فایروال
```bash
# باز کردن پورت‌های مورد نیاز
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5432/tcp
sudo ufw allow 6379/tcp
```

### 2. SSL/TLS
```bash
# نصب Certbot
sudo apt install certbot python3-certbot-nginx

# دریافت گواهینامه
sudo certbot --nginx -d your_domain.com
```

### 3. محدودیت دسترسی
```bash
# محدود کردن دسترسی به SSH
sudo nano /etc/ssh/sshd_config
# تغییر Port
# غیرفعال کردن root login
# فعال کردن کلید SSH
```

## مقیاس‌پذیری

### 1. افزایش منابع
- افزایش RAM و CPU
- استفاده از SSD
- بهینه‌سازی تنظیمات

### 2. Load Balancing
- استفاده از HAProxy
- تنظیم Nginx برای Load Balancing
- استفاده از CDN

### 3. کش‌گذاری
- تنظیم Redis
- استفاده از Memcached
- بهینه‌سازی کوئری‌ها 