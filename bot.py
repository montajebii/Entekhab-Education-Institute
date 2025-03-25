import os
import logging
from datetime import datetime
from typing import Optional, List, Dict
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum
from jdatetime import datetime as jdatetime
from jdatetime import date as jdate
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import plotly.graph_objects as go
import io
import json

# تنظیمات لاگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# لود کردن متغیرهای محیطی
load_dotenv()

# تنظیمات دیتابیس
Base = declarative_base()

class UserRole(enum.Enum):
    CEO = "مدیرعامل"
    DEPUTY = "معاون"
    DORMITORY_MANAGER = "مدیر خوابگاه"
    DORMITORY_CARETAKER = "سرپرست خوابگاه"
    DORMITORY_ACCOUNTANT = "حسابدار خوابگاه"
    DORMITORY_PROCUREMENT = "تدارکات خوابگاه"
    CONSULTANT_LEADER = "سرپرست مشاوران"
    CONSULTANT = "مشاور"
    CONSULTANT_ACCOUNTANT = "حسابدار مشاوران"
    TEST_DESIGNER = "طراح آزمون"
    EDUCATION_MANAGER = "مدیر آموزش"
    TEACHER_LEADER = "سرپرست معلمان"
    TEACHER = "معلم"
    EDUCATION_ACCOUNTANT = "حسابدار آموزش"
    EDUCATION_SECRETARY = "منشی آموزش"
    EDUCATION_IT = "پشتیبان آموزش"
    VIRTUAL_MANAGER = "مدیر مجازی"
    TELEGRAM_MANAGER = "مدیر تلگرام"
    TELEGRAM_ADMIN = "ادمین تلگرام"
    INSTAGRAM_MANAGER = "مدیر اینستاگرام"
    INSTAGRAM_ADMIN = "ادمین اینستاگرام"
    WEBSITE_MANAGER = "مدیر وبسایت"
    WEBSITE_TECH_SUPPORT = "پشتیبان فنی وبسایت"
    WEBSITE_CONTENT_MANAGER = "مدیر محتوای وبسایت"
    WEBSITE_IT = "پشتیبان وبسایت"
    INNOVATION_TEAM = "تیم نوآوری"

class Department(enum.Enum):
    DORMITORY = "خوابگاه"
    CONSULTING = "مشاوره"
    EDUCATION = "آموزش"
    VIRTUAL = "مجازی"
    INNOVATION = "نوآوری"

class TaskStatus(enum.Enum):
    PENDING = "در انتظار"
    IN_PROGRESS = "در حال انجام"
    COMPLETED = "تکمیل شده"
    CANCELLED = "لغو شده"
    DELAYED = "تاخیر داشته"
    PENDING_APPROVAL = "در انتظار تایید مدیر"

class TaskPriority(enum.Enum):
    LOW = "کم"
    MEDIUM = "متوسط"
    HIGH = "زیاد"
    URGENT = "فوری"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    role = Column(Enum(UserRole))
    department = Column(Enum(Department))
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    
    tasks = relationship("Task", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    work_hours = relationship("WorkHour", back_populates="user")
    transferred_tasks = relationship("Task", back_populates="transferred_to")

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'))
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    created_at = Column(DateTime, default=datetime.now)
    deadline = Column(DateTime)
    scheduled_for = Column(DateTime)
    estimated_hours = Column(Float)
    actual_hours = Column(Float)
    completed_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    transferred_to_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    progress = Column(Integer, default=0)
    tags = Column(JSON, default=list)
    attachments = Column(JSON, default=list)
    
    user = relationship("User", back_populates="tasks", foreign_keys=[user_id])
    transferred_to = relationship("User", back_populates="transferred_tasks", foreign_keys=[transferred_to_id])
    comments = relationship("Comment", back_populates="task")
    progress_logs = relationship("ProgressLog", back_populates="task")
    shares = relationship("TaskShare", back_populates="task")
    analytics = Column(JSON, default=dict)

class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    task = relationship("Task", back_populates="comments")
    user = relationship("User", back_populates="comments")

class Attachment(Base):
    __tablename__ = 'attachments'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    file_name = Column(String)
    file_path = Column(String)
    file_type = Column(String)
    file_size = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.now)
    
    task = relationship("Task", back_populates="attachments")

class ProgressLog(Base):
    __tablename__ = 'progress_logs'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    progress_percentage = Column(Integer)
    description = Column(Text)
    logged_at = Column(DateTime, default=datetime.now)
    
    task = relationship("Task", back_populates="progress_logs")

class TaskShare(Base):
    __tablename__ = 'task_shares'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    shared_with_id = Column(Integer, ForeignKey('users.id'))
    shared_at = Column(DateTime, default=datetime.now)
    
    task = relationship("Task", back_populates="shares")

class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String)
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="notifications")

class WorkHour(Base):
    __tablename__ = 'work_hours'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    date = Column(DateTime)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    total_hours = Column(Float)
    description = Column(Text)
    
    user = relationship("User", back_populates="work_hours")

class Analytics(Base):
    __tablename__ = 'analytics'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    completion_time = Column(Float)
    quality_score = Column(Float)
    efficiency_score = Column(Float)
    created_at = Column(DateTime, default=datetime.now)

class ChatGroup(Base):
    __tablename__ = 'chat_groups'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    created_at = Column(DateTime, default=datetime.now)
    members = Column(JSON, default=list)
    messages = relationship("ChatMessage", back_populates="group")

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('chat_groups.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    group = relationship("ChatGroup", back_populates="messages")
    user = relationship("User")

# ایجاد اتصال به دیتابیس
engine = create_engine('sqlite:///tasks.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class TaskBot:
    def __init__(self):
        self.session = Session()
        self.admin_id = int(os.getenv('ADMIN_TELEGRAM_ID'))
        self.model = RandomForestRegressor()
        self.is_model_trained = False
        
        # تعریف نقش‌های دارای دسترسی تایید
        self.approval_roles = {
            UserRole.CEO,
            UserRole.DEPUTY,
            UserRole.DORMITORY_MANAGER,
            UserRole.CONSULTANT_LEADER,
            UserRole.EDUCATION_MANAGER,
            UserRole.TEACHER_LEADER,
            UserRole.VIRTUAL_MANAGER,
            UserRole.WEBSITE_MANAGER
        }
        
        # تعریف سلسله مراتب نظارت
        self.supervision_hierarchy = {
            UserRole.CEO: [UserRole.DEPUTY, UserRole.INNOVATION_TEAM],
            UserRole.DEPUTY: [
                UserRole.DORMITORY_MANAGER,
                UserRole.CONSULTANT_LEADER,
                UserRole.EDUCATION_MANAGER,
                UserRole.VIRTUAL_MANAGER
            ],
            UserRole.DORMITORY_MANAGER: [
                UserRole.DORMITORY_CARETAKER,
                UserRole.DORMITORY_ACCOUNTANT,
                UserRole.DORMITORY_PROCUREMENT
            ],
            UserRole.CONSULTANT_LEADER: [
                UserRole.CONSULTANT,
                UserRole.CONSULTANT_ACCOUNTANT,
                UserRole.TEST_DESIGNER
            ],
            UserRole.EDUCATION_MANAGER: [
                UserRole.TEACHER_LEADER,
                UserRole.EDUCATION_ACCOUNTANT,
                UserRole.EDUCATION_SECRETARY,
                UserRole.EDUCATION_IT
            ],
            UserRole.TEACHER_LEADER: [UserRole.TEACHER],
            UserRole.VIRTUAL_MANAGER: [
                UserRole.TELEGRAM_MANAGER,
                UserRole.INSTAGRAM_MANAGER,
                UserRole.WEBSITE_MANAGER
            ],
            UserRole.TELEGRAM_MANAGER: [UserRole.TELEGRAM_ADMIN],
            UserRole.INSTAGRAM_MANAGER: [UserRole.INSTAGRAM_ADMIN],
            UserRole.WEBSITE_MANAGER: [
                UserRole.WEBSITE_TECH_SUPPORT,
                UserRole.WEBSITE_CONTENT_MANAGER,
                UserRole.WEBSITE_IT
            ]
        }
    
    def get_jalali_date(self, date):
        return jdatetime.fromgregorian(datetime=date).strftime('%Y/%m/%d %H:%M')
    
    def create_role_keyboard(self, department: Department = None) -> InlineKeyboardMarkup:
        keyboard = []
        for role in UserRole:
            if department and role.name.startswith(department.name):
                keyboard.append([InlineKeyboardButton(role.value, callback_data=f'role_{role.name}')])
            elif not department:
                keyboard.append([InlineKeyboardButton(role.value, callback_data=f'role_{role.name}')])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')])
        return InlineKeyboardMarkup(keyboard)
    
    def create_department_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = []
        for dept in Department:
            keyboard.append([InlineKeyboardButton(dept.value, callback_data=f'dept_{dept.name}')])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')])
        return InlineKeyboardMarkup(keyboard)
    
    def create_task_status_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = []
        for status in TaskStatus:
            keyboard.append([InlineKeyboardButton(status.value, callback_data=f'status_{status.name}')])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')])
        return InlineKeyboardMarkup(keyboard)
    
    def create_task_priority_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = []
        for priority in TaskPriority:
            keyboard.append([InlineKeyboardButton(priority.value, callback_data=f'priority_{priority.name}')])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')])
        return InlineKeyboardMarkup(keyboard)
    
    def create_main_menu_keyboard(self, user: User) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton("➕ افزودن وظیفه جدید", callback_data='add_task')],
            [InlineKeyboardButton("📋 مشاهده وظایف من", callback_data='my_tasks')],
            [InlineKeyboardButton("📊 گزارش‌گیری", callback_data='reports')],
            [InlineKeyboardButton("📅 تقویم وظایف", callback_data='task_calendar')],
            [InlineKeyboardButton("👥 همکاری", callback_data='collaboration')],
            [InlineKeyboardButton("⚙️ تنظیمات", callback_data='settings')]
        ]
        
        if self.can_approve_tasks(user.role):
            keyboard.append([InlineKeyboardButton("👥 وظایف زیرمجموعه", callback_data='subordinate_tasks')])
            
        return InlineKeyboardMarkup(keyboard)
    
    def create_reports_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton("📈 عملکرد کارمندان", callback_data='report_performance')],
            [InlineKeyboardButton("📊 آمار وظایف", callback_data='report_tasks')],
            [InlineKeyboardButton("⏰ گزارش تاخیرات", callback_data='report_delays')],
            [InlineKeyboardButton("📅 گزارش دوره‌ای", callback_data='report_periodic')],
            [InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def create_collaboration_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton("💬 پیام‌های خصوصی", callback_data='private_messages')],
            [InlineKeyboardButton("👥 اشتراک وظایف", callback_data='share_tasks')],
            [InlineKeyboardButton("📝 کامنت‌ها", callback_data='comments')],
            [InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def create_settings_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton("🔔 تنظیمات اعلان‌ها", callback_data='notification_settings')],
            [InlineKeyboardButton("📅 تنظیمات تقویم", callback_data='calendar_settings')],
            [InlineKeyboardButton("👤 پروفایل", callback_data='profile')],
            [InlineKeyboardButton("❓ راهنما", callback_data='help')],
            [InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def can_approve_tasks(self, role: UserRole) -> bool:
        return role in self.approval_roles
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        db_user = self.session.query(User).filter_by(telegram_id=user.id).first()
        
        if not db_user:
            await update.message.reply_text(
                'به ربات مدیریت وظایف خوش آمدید! لطفاً بخش سازمانی خود را انتخاب کنید:',
                reply_markup=self.create_department_keyboard()
            )
        elif not db_user.is_approved:
            await update.message.reply_text(
                'ثبت‌نام شما در انتظار تایید مدیر است. لطفاً صبر کنید.'
            )
        else:
            await self.show_main_menu(update, context)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if 'state' not in context.user_data:
            return
            
        if context.user_data['state'] == 'waiting_for_first_name':
            context.user_data['registration']['first_name'] = update.message.text
            await update.message.reply_text('لطفاً نام خانوادگی خود را وارد کنید:')
            context.user_data['state'] = 'waiting_for_last_name'
            
        elif context.user_data['state'] == 'waiting_for_last_name':
            reg_data = context.user_data['registration']
            reg_data['last_name'] = update.message.text
            
            db_user = User(
                telegram_id=reg_data['telegram_id'],
                username=reg_data['username'],
                first_name=reg_data['first_name'],
                last_name=reg_data['last_name'],
                role=reg_data['role'],
                department=reg_data['department']
            )
            self.session.add(db_user)
            self.session.commit()
            
            # ارسال درخواست به مدیر برای تایید
            admin_message = (
                f'درخواست ثبت‌نام جدید:\n'
                f'نام: {reg_data["first_name"]}\n'
                f'نام خانوادگی: {reg_data["last_name"]}\n'
                f'نام کاربری: {reg_data["username"]}\n'
                f'نقش: {reg_data["role"].value}\n'
                f'بخش: {reg_data["department"].value}'
            )
            
            keyboard = [
                [InlineKeyboardButton("✅ تایید", callback_data=f'approve_user_{db_user.id}')],
                [InlineKeyboardButton("❌ رد", callback_data=f'reject_user_{db_user.id}')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=self.admin_id,
                text=admin_message,
                reply_markup=reply_markup
            )
            
            await update.message.reply_text(
                'اطلاعات شما ثبت شد و در انتظار تایید مدیر است.'
            )
            context.user_data.clear()
            
        elif context.user_data['state'] == 'waiting_for_task_title':
            context.user_data['task'] = {'title': update.message.text}
            await update.message.reply_text('لطفاً توضیحات وظیفه را وارد کنید:')
            context.user_data['state'] = 'waiting_for_task_description'
            
        elif context.user_data['state'] == 'waiting_for_task_description':
            context.user_data['task']['description'] = update.message.text
            await update.message.reply_text(
                'لطفاً اولویت وظیفه را انتخاب کنید:',
                reply_markup=self.create_task_priority_keyboard()
            )
            context.user_data['state'] = 'waiting_for_task_priority'
            
        elif context.user_data['state'] == 'waiting_for_schedule_date':
            try:
                date_str = update.message.text
                scheduled_date = jdatetime.strptime(date_str, '%Y/%m/%d %H:%M').togregorian()
                context.user_data['task']['scheduled_for'] = scheduled_date
                
                user = update.effective_user
                db_user = self.session.query(User).filter_by(telegram_id=user.id).first()
                
                task = Task(
                    title=context.user_data['task']['title'],
                    description=context.user_data['task']['description'],
                    user_id=db_user.id,
                    scheduled_for=scheduled_date,
                    priority=context.user_data['task']['priority']
                )
                self.session.add(task)
                self.session.commit()
                
                # ایجاد اعلان برای یادآوری
                notification = Notification(
                    title="وظیفه جدید",
                    content=f"وظیفه جدید '{task.title}' برای شما ثبت شد.",
                    user_id=db_user.id
                )
                self.session.add(notification)
                self.session.commit()
                
                await update.message.reply_text(
                    'وظیفه با موفقیت ثبت شد!',
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]])
                )
                context.user_data.clear()
                await self.show_main_menu(update, context)
                
            except ValueError:
                await update.message.reply_text(
                    'فرمت تاریخ نامعتبر است. لطفاً به فرمت YYYY/MM/DD HH:MM وارد کنید:'
                )
            
        elif context.user_data['state'] == 'waiting_for_chat_group_name':
            group_name = update.message.text
            user = update.effective_user
            db_user = self.session.query(User).filter_by(telegram_id=user.id).first()
            
            chat_group = ChatGroup(
                name=group_name,
                members=[db_user.id]
            )
            self.session.add(chat_group)
            self.session.commit()
            
            await update.message.reply_text(
                f'گروه چت "{group_name}" با موفقیت ایجاد شد.',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]])
            )
            context.user_data.clear()
            
        elif context.user_data['state'] == 'waiting_for_file':
            file = update.message.document
            if file:
                file_path = await context.bot.get_file(file.file_id)
                file_name = file.file_name
                
                # ذخیره اطلاعات فایل در دیتابیس
                task_id = context.user_data.get('current_task_id')
                if task_id:
                    task = self.session.query(Task).get(task_id)
                    if task:
                        task.attachments.append({
                            'name': file_name,
                            'file_id': file.file_id
                        })
                        self.session.commit()
                
                await update.message.reply_text(
                    'فایل با موفقیت آپلود شد.',
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]])
                )
                context.user_data.clear()
                
        elif context.user_data['state'] == 'waiting_for_user_tag':
            username = update.message.text
            user = self.session.query(User).filter_by(username=username).first()
            
            if user:
                task_id = context.user_data.get('current_task_id')
                if task_id:
                    task = self.session.query(Task).get(task_id)
                    if task:
                        task.tags.append(user.id)
                        self.session.commit()
                        
                        await update.message.reply_text(
                            f'کاربر {user.first_name} {user.last_name} با موفقیت تگ شد.',
                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]])
                        )
            else:
                await update.message.reply_text(
                    'کاربر مورد نظر یافت نشد.',
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]])
                )
            context.user_data.clear()
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith('approve_user_'):
            user_id = int(query.data.split('_')[2])
            db_user = self.session.query(User).get(user_id)
            if db_user:
                db_user.is_approved = True
                self.session.commit()
                await query.message.reply_text('کاربر مورد نظر تایید شد.')
                await context.bot.send_message(
                    chat_id=db_user.telegram_id,
                    text='ثبت‌نام شما تایید شد. می‌توانید از ربات استفاده کنید.'
                )
                
        elif query.data.startswith('reject_user_'):
            user_id = int(query.data.split('_')[2])
            db_user = self.session.query(User).get(user_id)
            if db_user:
                self.session.delete(db_user)
                self.session.commit()
                await query.message.reply_text('کاربر مورد نظر رد شد.')
                await context.bot.send_message(
                    chat_id=db_user.telegram_id,
                    text='متاسفانه ثبت‌نام شما رد شد. لطفاً دوباره تلاش کنید.'
                )
                
        elif query.data.startswith('dept_'):
            department = Department[query.data.split('_')[1]]
            context.user_data['registration'] = {
                'department': department,
                'telegram_id': query.from_user.id,
                'username': query.from_user.username
            }
            await query.message.edit_text(
                'لطفاً نقش خود را انتخاب کنید:',
                reply_markup=self.create_role_keyboard(department)
            )
            
        elif query.data.startswith('role_'):
            role = UserRole[query.data.split('_')[1]]
            context.user_data['registration']['role'] = role
            await query.message.edit_text(
                'لطفاً نام خود را وارد کنید:',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]])
            )
            context.user_data['state'] = 'waiting_for_first_name'
            
        elif query.data == 'add_task':
            await query.message.edit_text(
                'لطفاً عنوان وظیفه را وارد کنید:',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]])
            )
            context.user_data['state'] = 'waiting_for_task_title'
            
        elif query.data.startswith('priority_'):
            priority = TaskPriority[query.data.split('_')[1]]
            context.user_data['task']['priority'] = priority
            keyboard = [
                [InlineKeyboardButton("⏰ همین الان", callback_data='schedule_now')],
                [InlineKeyboardButton("📅 برای آینده", callback_data='schedule_future')]
            ]
            await query.message.edit_text(
                'زمان اجرای وظیفه را انتخاب کنید:',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            context.user_data['state'] = 'waiting_for_schedule_choice'
            
        elif query.data == 'schedule_now':
            user = query.from_user
            db_user = self.session.query(User).filter_by(telegram_id=user.id).first()
            
            task = Task(
                title=context.user_data['task']['title'],
                description=context.user_data['task']['description'],
                user_id=db_user.id,
                scheduled_for=datetime.now(),
                priority=context.user_data['task']['priority']
            )
            self.session.add(task)
            self.session.commit()
            
            # ایجاد اعلان برای یادآوری
            notification = Notification(
                title="وظیفه جدید",
                content=f"وظیفه جدید '{task.title}' برای شما ثبت شد.",
                user_id=db_user.id
            )
            self.session.add(notification)
            self.session.commit()
            
            await query.message.edit_text(
                'وظیفه با موفقیت ثبت شد!',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]])
            )
            context.user_data.clear()
            await self.show_main_menu(query, context)
            
        elif query.data == 'schedule_future':
            await query.message.edit_text(
                'لطفاً تاریخ اجرای وظیفه را به فرمت YYYY/MM/DD HH:MM وارد کنید:',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]])
            )
            context.user_data['state'] = 'waiting_for_schedule_date'
            
        elif query.data == 'my_tasks':
            await self.show_user_tasks(query)
            
        elif query.data == 'reports':
            await query.message.edit_text(
                'گزارش‌گیری:',
                reply_markup=self.create_reports_keyboard()
            )
            
        elif query.data == 'task_calendar':
            await self.show_task_calendar(query)
            
        elif query.data == 'collaboration':
            await query.message.edit_text(
                'همکاری:',
                reply_markup=self.create_collaboration_keyboard()
            )
            
        elif query.data == 'settings':
            await query.message.edit_text(
                'تنظیمات:',
                reply_markup=self.create_settings_keyboard()
            )
            
        elif query.data == 'back_to_main':
            await self.show_main_menu(query, context)
            
        elif query.data == 'analytics':
            user = query.from_user
            db_user = self.session.query(User).filter_by(telegram_id=user.id).first()
            report, img_bytes = self.generate_analytics_report(db_user.id)
            
            await query.message.reply_photo(
                photo=img_bytes,
                caption=report,
                parse_mode=ParseMode.MARKDOWN
            )
            
        elif query.data == 'chat_group':
            await query.message.edit_text(
                'لطفاً نام گروه چت را وارد کنید:',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]])
            )
            context.user_data['state'] = 'waiting_for_chat_group_name'
            
        elif query.data == 'share_file':
            await query.message.edit_text(
                'لطفاً فایل مورد نظر را ارسال کنید:',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]])
            )
            context.user_data['state'] = 'waiting_for_file'
            
        elif query.data == 'tag_user':
            await query.message.edit_text(
                'لطفاً نام کاربری را که می‌خواهید تگ کنید وارد کنید:',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]])
            )
            context.user_data['state'] = 'waiting_for_user_tag'
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        db_user = self.session.query(User).filter_by(telegram_id=user.id).first()
        
        if isinstance(update.callback_query, CallbackQuery):
            await update.callback_query.message.edit_text(
                'منوی اصلی:',
                reply_markup=self.create_main_menu_keyboard(db_user)
            )
        else:
            await update.message.reply_text(
                'منوی اصلی:',
                reply_markup=self.create_main_menu_keyboard(db_user)
            )
    
    async def show_user_tasks(self, query: CallbackQuery):
        user = query.from_user
        db_user = self.session.query(User).filter_by(telegram_id=user.id).first()
        tasks = self.session.query(Task).filter_by(user_id=db_user.id).all()
        
        if not tasks:
            await query.message.edit_text(
                'شما هیچ وظیفه‌ای ندارید.',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]])
            )
            return
            
        message = 'وظایف شما:\n\n'
        for task in tasks:
            message += f'📝 {task.title}\n'
            message += f'📄 {task.description}\n'
            message += f'📅 تاریخ: {self.get_jalali_date(task.created_at)}\n'
            message += f'🔍 وضعیت: {task.status.value}\n'
            message += f'⚡️ اولویت: {task.priority.value}\n'
            if task.deadline:
                message += f'⏰ مهلت: {self.get_jalali_date(task.deadline)}\n'
            message += '\n'
            
            keyboard = [
                [InlineKeyboardButton("📊 ثبت پیشرفت", callback_data=f'log_progress_{task.id}')],
                [InlineKeyboardButton("💬 کامنت", callback_data=f'add_comment_{task.id}')],
                [InlineKeyboardButton("📎 پیوست", callback_data=f'add_attachment_{task.id}')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.edit_text(message, reply_markup=reply_markup)
    
    async def show_task_calendar(self, query: CallbackQuery):
        user = query.from_user
        db_user = self.session.query(User).filter_by(telegram_id=user.id).first()
        tasks = self.session.query(Task).filter_by(user_id=db_user.id).all()
        
        if not tasks:
            await query.message.edit_text(
                'شما هیچ وظیفه‌ای در تقویم ندارید.',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]])
            )
            return
            
        message = 'تقویم وظایف شما:\n\n'
        for task in tasks:
            if task.scheduled_for:
                message += f'📅 {self.get_jalali_date(task.scheduled_for)}\n'
                message += f'📝 {task.title}\n'
                message += f'🔍 وضعیت: {task.status.value}\n'
                message += f'⚡️ اولویت: {task.priority.value}\n\n'
        
        await query.message.edit_text(
            message,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]])
        )
    
    def train_prediction_model(self):
        tasks = self.session.query(Task).filter(Task.completed_at.isnot(None)).all()
        if not tasks:
            return
            
        X = []
        y = []
        for task in tasks:
            features = [
                task.estimated_hours or 0,
                len(task.description.split()),
                len(task.comments),
                task.priority.value,
                task.created_at.hour,
                task.created_at.weekday()
            ]
            X.append(features)
            y.append((task.completed_at - task.created_at).total_seconds() / 3600)
            
        self.model.fit(X, y)
        self.is_model_trained = True
    
    def predict_task_duration(self, task):
        if not self.is_model_trained:
            self.train_prediction_model()
            
        features = [
            task.estimated_hours or 0,
            len(task.description.split()),
            len(task.comments),
            task.priority.value,
            task.created_at.hour,
            task.created_at.weekday()
        ]
        return self.model.predict([features])[0]
    
    def generate_analytics_report(self, user_id: int, period: str = 'month') -> str:
        user = self.session.query(User).get(user_id)
        tasks = self.session.query(Task).filter_by(user_id=user_id).all()
        
        # محاسبه شاخص‌های کلیدی
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
        completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        # محاسبه میانگین زمان انجام وظایف
        completed_tasks_with_time = [t for t in tasks if t.completed_at and t.created_at]
        avg_completion_time = np.mean([
            (t.completed_at - t.created_at).total_seconds() / 3600
            for t in completed_tasks_with_time
        ]) if completed_tasks_with_time else 0
        
        # ایجاد نمودار
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[t.created_at for t in tasks],
            y=[t.progress for t in tasks],
            name='پیشرفت وظایف'
        ))
        
        # ذخیره نمودار
        img_bytes = io.BytesIO()
        fig.write_image(img_bytes, format='png')
        img_bytes.seek(0)
        
        report = f"""
📊 گزارش عملکرد {user.first_name} {user.last_name}

📈 شاخص‌های کلیدی:
• تعداد کل وظایف: {total_tasks}
• وظایف تکمیل شده: {completed_tasks}
• نرخ تکمیل: {completion_rate:.1f}%
• میانگین زمان انجام: {avg_completion_time:.1f} ساعت

📊 تحلیل عملکرد:
• بهره‌وری: {'عالی' if completion_rate > 80 else 'خوب' if completion_rate > 60 else 'متوسط'}
• سرعت انجام: {'عالی' if avg_completion_time < 24 else 'خوب' if avg_completion_time < 48 else 'متوسط'}
"""
        return report, img_bytes

def main():
    bot = TaskBot()
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
    
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CallbackQueryHandler(bot.handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    application.run_polling()

if __name__ == '__main__':
    main()