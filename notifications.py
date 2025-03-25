from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from config import *
import asyncio
from utils import format_duration

class Notification:
    def __init__(self, user_id: str, title: str, message: str, notification_type: str):
        self.id = str(datetime.now().timestamp())
        self.user_id = user_id
        self.title = title
        self.message = message
        self.type = notification_type
        self.created_at = datetime.now()
        self.read = False
        self.action_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل اعلان به دیکشنری"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'created_at': self.created_at,
            'read': self.read,
            'action_data': self.action_data
        }

class NotificationManager:
    def __init__(self):
        self.notifications: Dict[str, List[Notification]] = {}
        self.reminder_tasks: Dict[str, asyncio.Task] = {}
    
    def add_notification(self, user_id: str, title: str, message: str, notification_type: str,
                        action_data: Optional[Dict[str, Any]] = None) -> Notification:
        """افزودن اعلان جدید"""
        notification = Notification(user_id, title, message, notification_type)
        notification.action_data = action_data
        
        if user_id not in self.notifications:
            self.notifications[user_id] = []
        self.notifications[user_id].append(notification)
        
        return notification
    
    def get_user_notifications(self, user_id: str, unread_only: bool = False) -> List[Dict[str, Any]]:
        """دریافت اعلان‌های کاربر"""
        if user_id not in self.notifications:
            return []
        
        notifications = self.notifications[user_id]
        if unread_only:
            notifications = [n for n in notifications if not n.read]
        
        return [n.to_dict() for n in notifications]
    
    def mark_as_read(self, user_id: str, notification_id: str) -> bool:
        """علامت‌گذاری اعلان به عنوان خوانده شده"""
        if user_id not in self.notifications:
            return False
        
        for notification in self.notifications[user_id]:
            if notification.id == notification_id:
                notification.read = True
                return True
        return False
    
    def mark_all_as_read(self, user_id: str) -> bool:
        """علامت‌گذاری تمام اعلان‌ها به عنوان خوانده شده"""
        if user_id not in self.notifications:
            return False
        
        for notification in self.notifications[user_id]:
            notification.read = True
        return True
    
    def delete_notification(self, user_id: str, notification_id: str) -> bool:
        """حذف اعلان"""
        if user_id not in self.notifications:
            return False
        
        for i, notification in enumerate(self.notifications[user_id]):
            if notification.id == notification_id:
                del self.notifications[user_id][i]
                return True
        return False
    
    def clear_user_notifications(self, user_id: str) -> bool:
        """پاک کردن تمام اعلان‌های کاربر"""
        if user_id in self.notifications:
            del self.notifications[user_id]
            return True
        return False
    
    async def schedule_reminder(self, user_id: str, task_id: str, title: str,
                              message: str, delay: int) -> None:
        """برنامه‌ریزی یادآوری"""
        reminder_id = f"{user_id}_{task_id}"
        
        # لغو یادآوری قبلی اگر وجود داشته باشد
        if reminder_id in self.reminder_tasks:
            self.reminder_tasks[reminder_id].cancel()
            del self.reminder_tasks[reminder_id]
        
        # ایجاد یادآوری جدید
        async def reminder_task():
            await asyncio.sleep(delay)
            self.add_notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type='reminder',
                action_data={'task_id': task_id}
            )
        
        self.reminder_tasks[reminder_id] = asyncio.create_task(reminder_task())
    
    def cancel_reminder(self, user_id: str, task_id: str) -> bool:
        """لغو یادآوری"""
        reminder_id = f"{user_id}_{task_id}"
        if reminder_id in self.reminder_tasks:
            self.reminder_tasks[reminder_id].cancel()
            del self.reminder_tasks[reminder_id]
            return True
        return False
    
    def create_task_notification(self, user_id: str, task_id: str, title: str,
                               message: str, notification_type: str) -> Notification:
        """ایجاد اعلان مرتبط با وظیفه"""
        return self.add_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            action_data={'task_id': task_id}
        )
    
    def create_group_notification(self, user_id: str, group_id: str, title: str,
                                message: str, notification_type: str) -> Notification:
        """ایجاد اعلان مرتبط با گروه"""
        return self.add_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            action_data={'group_id': group_id}
        )
    
    def get_notification_stats(self, user_id: str) -> Dict[str, Any]:
        """دریافت آمار اعلان‌ها"""
        if user_id not in self.notifications:
            return {
                'total': 0,
                'unread': 0,
                'by_type': {}
            }
        
        notifications = self.notifications[user_id]
        unread_count = len([n for n in notifications if not n.read])
        
        # شمارش اعلان‌ها به تفکیک نوع
        type_counts = {}
        for notification in notifications:
            if notification.type not in type_counts:
                type_counts[notification.type] = 0
            type_counts[notification.type] += 1
        
        return {
            'total': len(notifications),
            'unread': unread_count,
            'by_type': type_counts
        } 