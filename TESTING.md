# راهنمای تست‌نویسی

## مقدمه

این راهنما روش‌های تست‌نویسی و اجرای تست‌ها در پروژه را توضیح می‌دهد.

## انواع تست‌ها

### 1. تست واحد (Unit Tests)

تست‌های واحد برای تست کردن توابع و کلاس‌های منفرد استفاده می‌شوند.

#### مثال تست واحد
```python
import unittest
from models import Task

class TestTask(unittest.TestCase):
    def setUp(self):
        self.task = Task(
            title="تست",
            description="توضیحات تست",
            priority="high"
        )

    def test_task_creation(self):
        self.assertEqual(self.task.title, "تست")
        self.assertEqual(self.task.priority, "high")

    def test_task_status(self):
        self.assertEqual(self.task.status, "pending")
        self.task.complete()
        self.assertEqual(self.task.status, "completed")
```

### 2. تست یکپارچگی (Integration Tests)

تست‌های یکپارچگی برای تست کردن تعامل بین اجزای مختلف سیستم استفاده می‌شوند.

#### مثال تست یکپارچگی
```python
import unittest
from database import Database
from models import Task, User

class TestTaskIntegration(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.user = User(username="test_user")
        self.task = Task(title="تست یکپارچگی")

    def test_task_assignment(self):
        self.task.assign_to(self.user)
        self.assertEqual(self.task.assignee, self.user)
        self.assertIn(self.task, self.user.tasks)
```

### 3. تست عملکرد (Performance Tests)

تست‌های عملکرد برای اندازه‌گیری سرعت و کارایی سیستم استفاده می‌شوند.

#### مثال تست عملکرد
```python
import time
import unittest
from database import Database

class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.tasks = [Task(title=f"تست {i}") for i in range(1000)]

    def test_bulk_insert(self):
        start_time = time.time()
        self.db.bulk_insert(self.tasks)
        end_time = time.time()
        self.assertLess(end_time - start_time, 5.0)  # کمتر از 5 ثانیه
```

### 4. تست امنیتی (Security Tests)

تست‌های امنیتی برای بررسی آسیب‌پذیری‌های سیستم استفاده می‌شوند.

#### مثال تست امنیتی
```python
import unittest
from security import SecurityManager

class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.security = SecurityManager()

    def test_password_strength(self):
        weak_password = "123456"
        strong_password = "P@ssw0rd123"
        
        self.assertFalse(self.security.is_password_strong(weak_password))
        self.assertTrue(self.security.is_password_strong(strong_password))

    def test_rate_limiting(self):
        for _ in range(100):
            self.security.check_rate_limit("test_ip")
        with self.assertRaises(RateLimitExceeded):
            self.security.check_rate_limit("test_ip")
```

## اجرای تست‌ها

### 1. با استفاده از unittest
```bash
# اجرای تمام تست‌ها
python -m unittest discover

# اجرای یک فایل تست خاص
python -m unittest tests/test_task.py

# اجرای یک کلاس تست خاص
python -m unittest tests.test_task.TestTask
```

### 2. با استفاده از pytest
```bash
# نصب pytest
pip install pytest

# اجرای تمام تست‌ها
pytest

# اجرای با گزارش پوشش کد
pytest --cov=app tests/
```

### 3. با استفاده از tox
```bash
# نصب tox
pip install tox

# اجرای تست‌ها در محیط‌های مختلف
tox
```

## بهترین شیوه‌ها

### 1. ساختار تست‌ها
- تست‌ها را در پوشه `tests` قرار دهید
- نام فایل‌های تست را با `test_` شروع کنید
- نام کلاس‌های تست را با `Test` شروع کنید
- نام متدهای تست را با `test_` شروع کنید

### 2. تنظیمات تست
- از `setUp` و `tearDown` استفاده کنید
- از محیط‌های مجازی جداگانه استفاده کنید
- از پایگاه داده تست جداگانه استفاده کنید
- از فیکسچرها استفاده کنید

### 3. نوشتن تست‌های خوب
- تست‌ها باید مستقل باشند
- هر تست یک چیز را تست کند
- از نام‌های توصیفی استفاده کنید
- از کامنت‌های مناسب استفاده کنید
- تست‌ها باید قابل تکرار باشند

### 4. پوشش کد
- هدف: حداقل 80% پوشش کد
- تست‌های مثبت و منفی بنویسید
- موارد خاص را تست کنید
- خطاها را تست کنید

## ابزارها

### 1. پوشش کد
```bash
# نصب coverage
pip install coverage

# اجرای تست‌ها با پوشش کد
coverage run -m unittest discover

# گزارش پوشش کد
coverage report
```

### 2. تحلیل کد
```bash
# نصب pylint
pip install pylint

# بررسی کد
pylint app/
```

### 3. فرمت‌بندی کد
```bash
# نصب black
pip install black

# فرمت‌بندی کد
black .
```

## CI/CD

### 1. GitHub Actions
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python -m pytest
```

### 2. GitLab CI
```yaml
test:
  stage: test
  script:
    - pip install -r requirements.txt
    - pytest
  coverage: '/TOTAL.+ ([0-9]{1,3}%)/'
``` 