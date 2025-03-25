import os
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

# تنظیمات اصلی
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DATABASE_URL = 'sqlite:///tasks.db'

# تنظیمات تحلیل
ANALYTICS_UPDATE_INTERVAL = 3600  # به ثانیه
MAX_TASK_HISTORY = 1000  # تعداد حداکثر وظایف ذخیره شده برای تحلیل

# تنظیمات یادآوری
REMINDER_INTERVAL = 1800  # به ثانیه (30 دقیقه)
MAX_REMINDERS = 3  # تعداد حداکثر یادآوری برای هر وظیفه

# تنظیمات گروه‌های چت
MAX_GROUP_MEMBERS = 50
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 مگابایت

# تنظیمات پیش‌بینی
MIN_TASKS_FOR_PREDICTION = 10
PREDICTION_CONFIDENCE_THRESHOLD = 0.7

# تنظیمات گزارش‌گیری
REPORT_FORMATS = ['pdf', 'excel']
DEFAULT_REPORT_FORMAT = 'pdf'
REPORT_UPDATE_INTERVAL = 86400  # به ثانیه (24 ساعت)

# تنظیمات امنیتی
MAX_LOGIN_ATTEMPTS = 3
SESSION_TIMEOUT = 3600  # به ثانیه (1 ساعت)

# تنظیمات عملکرد
CACHE_TIMEOUT = 300  # به ثانیه (5 دقیقه)
MAX_CONCURRENT_REQUESTS = 10 