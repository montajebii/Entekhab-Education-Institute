from typing import List, Dict, Any, Optional
from datetime import datetime
from config import *
import os

class ChatGroup:
    def __init__(self, group_id: str, name: str, task_id: Optional[str] = None):
        self.group_id = group_id
        self.name = name
        self.task_id = task_id
        self.members: List[str] = []
        self.messages: List[Dict[str, Any]] = []
        self.files: List[Dict[str, Any]] = []
        self.created_at = datetime.now()
    
    def add_member(self, user_id: str) -> bool:
        """افزودن عضو جدید به گروه"""
        if len(self.members) >= MAX_GROUP_MEMBERS:
            return False
        if user_id not in self.members:
            self.members.append(user_id)
            return True
        return False
    
    def remove_member(self, user_id: str) -> bool:
        """حذف عضو از گروه"""
        if user_id in self.members:
            self.members.remove(user_id)
            return True
        return False
    
    def add_message(self, user_id: str, text: str, message_type: str = 'text') -> Dict[str, Any]:
        """افزودن پیام جدید به گروه"""
        message = {
            'id': str(len(self.messages) + 1),
            'user_id': user_id,
            'text': text,
            'type': message_type,
            'timestamp': datetime.now(),
            'reactions': {},
            'mentions': []
        }
        self.messages.append(message)
        return message
    
    def add_file(self, user_id: str, file_id: str, file_name: str, file_size: int) -> Optional[Dict[str, Any]]:
        """افزودن فایل به گروه"""
        if not validate_file_size(file_size):
            return None
        
        file_info = {
            'id': str(len(self.files) + 1),
            'user_id': user_id,
            'file_id': file_id,
            'file_name': file_name,
            'file_size': file_size,
            'uploaded_at': datetime.now(),
            'downloads': 0
        }
        self.files.append(file_info)
        return file_info
    
    def get_messages(self, limit: int = 50, before: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """دریافت پیام‌های گروه"""
        messages = self.messages
        if before:
            messages = [m for m in messages if m['timestamp'] < before]
        return messages[-limit:]
    
    def get_files(self) -> List[Dict[str, Any]]:
        """دریافت لیست فایل‌های گروه"""
        return self.files
    
    def add_reaction(self, message_id: str, user_id: str, reaction: str) -> bool:
        """افزودن واکنش به پیام"""
        for message in self.messages:
            if message['id'] == message_id:
                if user_id not in message['reactions']:
                    message['reactions'][user_id] = reaction
                    return True
                elif message['reactions'][user_id] == reaction:
                    del message['reactions'][user_id]
                    return True
        return False
    
    def add_mention(self, message_id: str, mentioned_user_id: str) -> bool:
        """افزودن تگ کاربر در پیام"""
        for message in self.messages:
            if message['id'] == message_id:
                if mentioned_user_id not in message['mentions']:
                    message['mentions'].append(mentioned_user_id)
                    return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل گروه به دیکشنری"""
        return {
            'group_id': self.group_id,
            'name': self.name,
            'task_id': self.task_id,
            'members': self.members,
            'message_count': len(self.messages),
            'file_count': len(self.files),
            'created_at': self.created_at
        }

class ChatManager:
    def __init__(self):
        self.groups: Dict[str, ChatGroup] = {}
    
    def create_group(self, group_id: str, name: str, task_id: Optional[str] = None) -> ChatGroup:
        """ایجاد گروه چت جدید"""
        group = ChatGroup(group_id, name, task_id)
        self.groups[group_id] = group
        return group
    
    def get_group(self, group_id: str) -> Optional[ChatGroup]:
        """دریافت گروه با شناسه"""
        return self.groups.get(group_id)
    
    def delete_group(self, group_id: str) -> bool:
        """حذف گروه"""
        if group_id in self.groups:
            del self.groups[group_id]
            return True
        return False
    
    def get_user_groups(self, user_id: str) -> List[Dict[str, Any]]:
        """دریافت لیست گروه‌های کاربر"""
        return [
            group.to_dict()
            for group in self.groups.values()
            if user_id in group.members
        ]
    
    def get_task_groups(self, task_id: str) -> List[Dict[str, Any]]:
        """دریافت لیست گروه‌های مرتبط با یک وظیفه"""
        return [
            group.to_dict()
            for group in self.groups.values()
            if group.task_id == task_id
        ]
    
    def search_messages(self, group_id: str, query: str) -> List[Dict[str, Any]]:
        """جستجو در پیام‌های گروه"""
        group = self.get_group(group_id)
        if not group:
            return []
        
        return [
            message
            for message in group.messages
            if query.lower() in message['text'].lower()
        ]
    
    def get_file_info(self, group_id: str, file_id: str) -> Optional[Dict[str, Any]]:
        """دریافت اطلاعات فایل"""
        group = self.get_group(group_id)
        if not group:
            return None
        
        for file in group.files:
            if file['file_id'] == file_id:
                return file
        return None
    
    def increment_file_downloads(self, group_id: str, file_id: str) -> bool:
        """افزایش تعداد دانلودهای فایل"""
        group = self.get_group(group_id)
        if not group:
            return False
        
        for file in group.files:
            if file['file_id'] == file_id:
                file['downloads'] += 1
                return True
        return False 