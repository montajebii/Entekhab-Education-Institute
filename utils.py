import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64
from typing import List, Dict, Any, Optional
import jdatetime
from config import *

def create_task_chart(tasks_data: List[Dict[str, Any]]) -> str:
    """ایجاد نمودار تعاملی برای نمایش وضعیت وظایف"""
    df = pd.DataFrame(tasks_data)
    
    fig = make_subplots(rows=2, cols=2,
                        subplot_titles=('وضعیت وظایف', 'توزیع اولویت‌ها',
                                      'روند تکمیل وظایف', 'میانگین زمان انجام'))
    
    # نمودار وضعیت وظایف
    status_counts = df['status'].value_counts()
    fig.add_trace(
        go.Pie(labels=status_counts.index, values=status_counts.values),
        row=1, col=1
    )
    
    # نمودار اولویت‌ها
    priority_counts = df['priority'].value_counts()
    fig.add_trace(
        go.Bar(x=priority_counts.index, y=priority_counts.values),
        row=1, col=2
    )
    
    # نمودار روند تکمیل
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['completed_at'] = pd.to_datetime(df['completed_at'])
    daily_completion = df.groupby(df['completed_at'].dt.date).size()
    fig.add_trace(
        go.Scatter(x=daily_completion.index, y=daily_completion.values),
        row=2, col=1
    )
    
    # نمودار زمان انجام
    df['duration'] = (df['completed_at'] - df['created_at']).dt.total_seconds() / 3600
    fig.add_trace(
        go.Box(y=df['duration']),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False)
    
    # تبدیل نمودار به تصویر
    img_bytes = fig.to_image(format="png")
    img_str = base64.b64encode(img_bytes).decode()
    return f"data:image/png;base64,{img_str}"

def generate_analytics_report(tasks_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """تولید گزارش تحلیلی از داده‌های وظایف"""
    df = pd.DataFrame(tasks_data)
    
    # محاسبه شاخص‌های کلیدی
    total_tasks = len(df)
    completed_tasks = len(df[df['status'] == 'completed'])
    completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
    
    # محاسبه میانگین زمان انجام
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['completed_at'] = pd.to_datetime(df['completed_at'])
    df['duration'] = (df['completed_at'] - df['created_at']).dt.total_seconds() / 3600
    avg_duration = df['duration'].mean()
    
    # تحلیل اولویت‌ها
    priority_stats = df['priority'].value_counts().to_dict()
    
    # تحلیل وضعیت‌ها
    status_stats = df['status'].value_counts().to_dict()
    
    return {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'completion_rate': completion_rate,
        'avg_duration': avg_duration,
        'priority_stats': priority_stats,
        'status_stats': status_stats,
        'chart': create_task_chart(tasks_data)
    }

def predict_task_duration(task_features: Dict[str, Any], model) -> float:
    """پیش‌بینی زمان انجام وظیفه با استفاده از مدل"""
    features = pd.DataFrame([task_features])
    prediction = model.predict(features)[0]
    return max(0, prediction)  # اطمینان از عدم پیش‌بینی زمان منفی

def convert_to_jalali(date: datetime) -> str:
    """تبدیل تاریخ میلادی به شمسی"""
    return jdatetime.date.fromgregorian(date=date).strftime('%Y/%m/%d')

def format_duration(seconds: float) -> str:
    """تبدیل ثانیه به فرمت خوانا"""
    duration = timedelta(seconds=seconds)
    hours = duration.total_seconds() / 3600
    if hours < 24:
        return f"{hours:.1f} ساعت"
    else:
        days = hours / 24
        return f"{days:.1f} روز"

def validate_file_size(file_size: int) -> bool:
    """بررسی اعتبار اندازه فایل"""
    return file_size <= MAX_FILE_SIZE

def generate_task_summary(task: Dict[str, Any]) -> str:
    """تولید خلاصه وظیفه برای نمایش"""
    return f"""
📋 عنوان: {task['title']}
👤 مسئول: {task['assignee']}
⚡ اولویت: {task['priority']}
📅 تاریخ ایجاد: {convert_to_jalali(task['created_at'])}
⏰ زمان تخمینی: {format_duration(task['estimated_duration'])}
📝 توضیحات: {task['description'][:100]}...
""" 