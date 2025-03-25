from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import List, Optional
from config import *

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    username = Column(String, unique=True)
    role = Column(String)  # 'employee' or 'manager'
    created_at = Column(DateTime, default=datetime.now)
    last_active = Column(DateTime)
    settings = Column(JSON, default={})
    
    tasks = relationship("Task", back_populates="assignee")
    comments = relationship("Comment", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(String, primary_key=True)
    title = Column(String)
    description = Column(String)
    status = Column(String)  # 'pending', 'in_progress', 'completed'
    priority = Column(String)  # 'low', 'medium', 'high'
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    completed_at = Column(DateTime)
    estimated_duration = Column(Float)  # in hours
    actual_duration = Column(Float)  # in hours
    tags = Column(String)  # comma-separated tags
    assignee_id = Column(String, ForeignKey('users.id'))
    
    assignee = relationship("User", back_populates="tasks")
    comments = relationship("Comment", back_populates="task")
    analytics = relationship("Analytics", back_populates="task")

class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(String, primary_key=True)
    content = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    user_id = Column(String, ForeignKey('users.id'))
    task_id = Column(String, ForeignKey('tasks.id'))
    
    user = relationship("User", back_populates="comments")
    task = relationship("Task", back_populates="comments")

class Analytics(Base):
    __tablename__ = 'analytics'
    
    id = Column(String, primary_key=True)
    task_id = Column(String, ForeignKey('tasks.id'))
    created_at = Column(DateTime, default=datetime.now)
    data = Column(JSON)  # Store analytics data as JSON
    
    task = relationship("Task", back_populates="analytics")

class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    title = Column(String)
    message = Column(String)
    type = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    read = Column(Boolean, default=False)
    action_data = Column(JSON)
    
    user = relationship("User", back_populates="notifications")

class ChatGroup(Base):
    __tablename__ = 'chat_groups'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    task_id = Column(String, ForeignKey('tasks.id'))
    created_at = Column(DateTime, default=datetime.now)
    members = Column(JSON)  # List of user IDs
    settings = Column(JSON, default={})

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(String, primary_key=True)
    group_id = Column(String, ForeignKey('chat_groups.id'))
    user_id = Column(String, ForeignKey('users.id'))
    content = Column(String)
    type = Column(String)  # 'text', 'file', etc.
    created_at = Column(DateTime, default=datetime.now)
    metadata = Column(JSON)  # Additional message data

class Database:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        """دریافت یک جلسه دیتابیس جدید"""
        return self.Session()
    
    def add_user(self, user_id: str, username: str, role: str) -> User:
        """افزودن کاربر جدید"""
        session = self.get_session()
        try:
            user = User(id=user_id, username=username, role=role)
            session.add(user)
            session.commit()
            return user
        finally:
            session.close()
    
    def get_user(self, user_id: str) -> Optional[User]:
        """دریافت کاربر با شناسه"""
        session = self.get_session()
        try:
            return session.query(User).filter(User.id == user_id).first()
        finally:
            session.close()
    
    def add_task(self, task_id: str, title: str, description: str, assignee_id: str,
                 priority: str = 'medium', estimated_duration: float = None) -> Task:
        """افزودن وظیفه جدید"""
        session = self.get_session()
        try:
            task = Task(
                id=task_id,
                title=title,
                description=description,
                assignee_id=assignee_id,
                priority=priority,
                estimated_duration=estimated_duration,
                status='pending'
            )
            session.add(task)
            session.commit()
            return task
        finally:
            session.close()
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """دریافت وظیفه با شناسه"""
        session = self.get_session()
        try:
            return session.query(Task).filter(Task.id == task_id).first()
        finally:
            session.close()
    
    def update_task_status(self, task_id: str, status: str) -> bool:
        """به‌روزرسانی وضعیت وظیفه"""
        session = self.get_session()
        try:
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = status
                if status == 'completed':
                    task.completed_at = datetime.now()
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def add_comment(self, comment_id: str, task_id: str, user_id: str, content: str) -> Comment:
        """افزودن نظر جدید"""
        session = self.get_session()
        try:
            comment = Comment(
                id=comment_id,
                task_id=task_id,
                user_id=user_id,
                content=content
            )
            session.add(comment)
            session.commit()
            return comment
        finally:
            session.close()
    
    def get_task_comments(self, task_id: str) -> List[Comment]:
        """دریافت نظرات یک وظیفه"""
        session = self.get_session()
        try:
            return session.query(Comment).filter(Comment.task_id == task_id).all()
        finally:
            session.close()
    
    def add_analytics(self, analytics_id: str, task_id: str, data: dict) -> Analytics:
        """افزودن داده‌های تحلیلی"""
        session = self.get_session()
        try:
            analytics = Analytics(
                id=analytics_id,
                task_id=task_id,
                data=data
            )
            session.add(analytics)
            session.commit()
            return analytics
        finally:
            session.close()
    
    def get_task_analytics(self, task_id: str) -> List[Analytics]:
        """دریافت داده‌های تحلیلی یک وظیفه"""
        session = self.get_session()
        try:
            return session.query(Analytics).filter(Analytics.task_id == task_id).all()
        finally:
            session.close()
    
    def add_notification(self, notification_id: str, user_id: str, title: str,
                        message: str, notification_type: str, action_data: dict = None) -> Notification:
        """افزودن اعلان جدید"""
        session = self.get_session()
        try:
            notification = Notification(
                id=notification_id,
                user_id=user_id,
                title=title,
                message=message,
                type=notification_type,
                action_data=action_data
            )
            session.add(notification)
            session.commit()
            return notification
        finally:
            session.close()
    
    def get_user_notifications(self, user_id: str, unread_only: bool = False) -> List[Notification]:
        """دریافت اعلان‌های کاربر"""
        session = self.get_session()
        try:
            query = session.query(Notification).filter(Notification.user_id == user_id)
            if unread_only:
                query = query.filter(Notification.read == False)
            return query.all()
        finally:
            session.close()
    
    def create_chat_group(self, group_id: str, name: str, task_id: str = None,
                         members: List[str] = None) -> ChatGroup:
        """ایجاد گروه چت جدید"""
        session = self.get_session()
        try:
            group = ChatGroup(
                id=group_id,
                name=name,
                task_id=task_id,
                members=members or []
            )
            session.add(group)
            session.commit()
            return group
        finally:
            session.close()
    
    def add_chat_message(self, message_id: str, group_id: str, user_id: str,
                        content: str, message_type: str = 'text', metadata: dict = None) -> ChatMessage:
        """افزودن پیام به گروه چت"""
        session = self.get_session()
        try:
            message = ChatMessage(
                id=message_id,
                group_id=group_id,
                user_id=user_id,
                content=content,
                type=message_type,
                metadata=metadata
            )
            session.add(message)
            session.commit()
            return message
        finally:
            session.close()
    
    def get_group_messages(self, group_id: str, limit: int = 50) -> List[ChatMessage]:
        """دریافت پیام‌های گروه"""
        session = self.get_session()
        try:
            return session.query(ChatMessage)\
                .filter(ChatMessage.group_id == group_id)\
                .order_by(ChatMessage.created_at.desc())\
                .limit(limit)\
                .all()
        finally:
            session.close() 