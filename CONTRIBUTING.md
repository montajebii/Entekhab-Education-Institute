# راهنمای مشارکت در پروژه

## مقدمه

از مشارکت شما در پروژه استقبال می‌کنیم. این راهنما به شما کمک می‌کند تا به راحتی در پروژه مشارکت کنید.

## شروع کار

### 1. فورک کردن پروژه
1. به صفحه پروژه در GitHub بروید
2. روی دکمه "Fork" کلیک کنید
3. یک نسخه از پروژه در حساب شما ایجاد می‌شود

### 2. کلون کردن پروژه
```bash
git clone https://github.com/your-username/entekhab-task-manager.git
cd entekhab-task-manager
```

### 3. تنظیم محیط توسعه
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
pip install -r requirements-dev.txt
```

## فرآیند توسعه

### 1. ایجاد شاخه جدید
```bash
# اطمینان از به‌روز بودن شاخه اصلی
git checkout main
git pull origin main

# ایجاد شاخه جدید
git checkout -b feature/your-feature-name
# یا
git checkout -b fix/your-fix-name
```

### 2. توسعه
- کد را با توجه به استانداردهای پروژه بنویسید
- تست‌های مناسب اضافه کنید
- مستندات را به‌روز کنید
- از کامنت‌های مناسب استفاده کنید

### 3. تست‌ها
```bash
# اجرای تست‌ها
python -m pytest

# بررسی پوشش کد
coverage run -m pytest
coverage report

# بررسی کیفیت کد
pylint app/
```

### 4. کامیت تغییرات
```bash
# اضافه کردن تغییرات
git add .

# ایجاد کامیت
git commit -m "توضیحات تغییرات"

# ارسال تغییرات
git push origin feature/your-feature-name
```

### 5. ایجاد Pull Request
1. به صفحه پروژه اصلی بروید
2. روی "New Pull Request" کلیک کنید
3. شاخه خود را انتخاب کنید
4. توضیحات مناسب اضافه کنید
5. PR را ایجاد کنید

## استانداردهای کدنویسی

### 1. فرمت‌بندی
- از `black` برای فرمت‌بندی کد استفاده کنید
- حداکثر طول خط: 88 کاراکتر
- از فاصله به جای تب استفاده کنید
- از 4 فاصله برای تورفتگی استفاده کنید

### 2. نام‌گذاری
- نام کلاس‌ها: PascalCase
- نام توابع و متغیرها: snake_case
- نام ثابت‌ها: UPPER_SNAKE_CASE
- از نام‌های توصیفی استفاده کنید

### 3. مستندات
- از docstring برای توابع و کلاس‌ها استفاده کنید
- از کامنت‌های مناسب استفاده کنید
- مستندات را به‌روز نگه دارید
- از زبان فارسی استفاده کنید

### 4. تست‌ها
- تست‌های واحد بنویسید
- تست‌های یکپارچگی بنویسید
- پوشش کد را بالا نگه دارید
- تست‌های مثبت و منفی بنویسید

## بهترین شیوه‌ها

### 1. مدیریت کد
- تغییرات کوچک و متمرکز ایجاد کنید
- از شاخه‌های معنادار استفاده کنید
- پیام‌های کامیت واضح بنویسید
- کد تمیز و خوانا بنویسید

### 2. همکاری
- با دیگر توسعه‌دهندگان همکاری کنید
- بازخورد سازنده ارائه دهید
- از کدهای دیگران یاد بگیرید
- احترام متقابل را رعایت کنید

### 3. امنیت
- از توکن‌ها و رمزهای عبور محافظت کنید
- آسیب‌پذیری‌ها را گزارش دهید
- از بهترین شیوه‌های امنیتی پیروی کنید
- داده‌های حساس را محافظت کنید

### 4. عملکرد
- کد بهینه بنویسید
- از کش استفاده کنید
- کوئری‌های پایگاه داده را بهینه کنید
- منابع سیستم را در نظر بگیرید

## منابع مفید

### 1. مستندات
- [README.md](README.md)
- [API.md](API.md)
- [TESTING.md](TESTING.md)
- [DEPLOYMENT.md](DEPLOYMENT.md)

### 2. ابزارها
- [Python](https://www.python.org/)
- [Git](https://git-scm.com/)
- [GitHub](https://github.com/)
- [Docker](https://www.docker.com/)

### 3. انجمن‌ها
- [Stack Overflow](https://stackoverflow.com/)
- [GitHub Discussions](https://github.com/yourusername/entekhab-task-manager/discussions)
- [Python Discord](https://discord.gg/python)
- [Telegram Channel](https://t.me/your_channel)

## تماس با ما

- ایمیل: [ایمیل]
- تلگرام: [کانال تلگرام]
- وب‌سایت: [وب‌سایت]
- GitHub Issues: [Issues](https://github.com/yourusername/entekhab-task-manager/issues) 