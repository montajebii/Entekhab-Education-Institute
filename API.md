# مستندات API

## مقدمه

این مستندات API ربات مدیریت وظایف تلگرام را توضیح می‌دهد. API از پروتکل HTTP/HTTPS استفاده می‌کند و پاسخ‌ها در قالب JSON هستند.

## احراز هویت

### توکن API
برای استفاده از API، نیاز به توکن API دارید که می‌توانید آن را از پنل مدیریت دریافت کنید.

```http
Authorization: Bearer YOUR_API_TOKEN
```

## نقاط پایانی

### 1. مدیریت وظایف

#### ایجاد وظیفه جدید
```http
POST /api/v1/tasks
```

**درخواست:**
```json
{
    "title": "عنوان وظیفه",
    "description": "توضیحات وظیفه",
    "priority": "high",
    "due_date": "2024-03-20T15:00:00Z",
    "assignee_id": 123
}
```

**پاسخ موفق:**
```json
{
    "id": 1,
    "title": "عنوان وظیفه",
    "description": "توضیحات وظیفه",
    "priority": "high",
    "due_date": "2024-03-20T15:00:00Z",
    "assignee_id": 123,
    "status": "pending",
    "created_at": "2024-03-19T10:00:00Z"
}
```

#### دریافت لیست وظایف
```http
GET /api/v1/tasks
```

**پارامترهای اختیاری:**
- `status`: وضعیت وظیفه
- `priority`: اولویت
- `assignee_id`: شناسه مسئول
- `page`: شماره صفحه
- `per_page`: تعداد در هر صفحه

**پاسخ موفق:**
```json
{
    "tasks": [
        {
            "id": 1,
            "title": "عنوان وظیفه",
            "status": "pending",
            "priority": "high"
        }
    ],
    "total": 100,
    "page": 1,
    "per_page": 10
}
```

### 2. مدیریت کاربران

#### ثبت‌نام کاربر جدید
```http
POST /api/v1/users
```

**درخواست:**
```json
{
    "username": "username",
    "email": "user@example.com",
    "password": "password123",
    "role": "user"
}
```

**پاسخ موفق:**
```json
{
    "id": 1,
    "username": "username",
    "email": "user@example.com",
    "role": "user",
    "created_at": "2024-03-19T10:00:00Z"
}
```

#### دریافت اطلاعات کاربر
```http
GET /api/v1/users/{user_id}
```

**پاسخ موفق:**
```json
{
    "id": 1,
    "username": "username",
    "email": "user@example.com",
    "role": "user",
    "created_at": "2024-03-19T10:00:00Z"
}
```

### 3. گزارش‌گیری

#### دریافت گزارش عملکرد
```http
GET /api/v1/analytics/performance
```

**پارامترهای اختیاری:**
- `start_date`: تاریخ شروع
- `end_date`: تاریخ پایان
- `user_id`: شناسه کاربر

**پاسخ موفق:**
```json
{
    "total_tasks": 100,
    "completed_tasks": 80,
    "pending_tasks": 20,
    "completion_rate": 0.8,
    "average_completion_time": "2.5 days"
}
```

### 4. مدیریت گروه‌ها

#### ایجاد گروه جدید
```http
POST /api/v1/groups
```

**درخواست:**
```json
{
    "name": "نام گروه",
    "description": "توضیحات گروه",
    "member_ids": [1, 2, 3]
}
```

**پاسخ موفق:**
```json
{
    "id": 1,
    "name": "نام گروه",
    "description": "توضیحات گروه",
    "member_ids": [1, 2, 3],
    "created_at": "2024-03-19T10:00:00Z"
}
```

## کدهای خطا

| کد | توضیحات |
|----|----------|
| 400 | درخواست نامعتبر |
| 401 | عدم احراز هویت |
| 403 | عدم دسترسی |
| 404 | یافت نشد |
| 429 | تعداد درخواست زیاد |
| 500 | خطای سرور |

## محدودیت‌ها

- حداکثر 100 درخواست در دقیقه
- حداکثر حجم درخواست: 1MB
- حداکثر تعداد اعضای گروه: 100
- حداکثر تعداد وظایف در هر گروه: 1000

## بهترین شیوه‌ها

1. از کش استفاده کنید
2. درخواست‌ها را به صورت دسته‌ای ارسال کنید
3. از فیلترها استفاده کنید
4. خطاها را مدیریت کنید
5. از نسخه‌بندی استفاده کنید 