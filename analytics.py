import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from config import *
from utils import convert_to_jalali, format_duration

class TaskAnalytics:
    def __init__(self, tasks_data: List[Dict[str, Any]]):
        self.df = pd.DataFrame(tasks_data)
        self._prepare_data()
    
    def _prepare_data(self) -> None:
        """آماده‌سازی داده‌ها برای تحلیل"""
        # تبدیل تاریخ‌ها
        self.df['created_at'] = pd.to_datetime(self.df['created_at'])
        self.df['completed_at'] = pd.to_datetime(self.df['completed_at'])
        
        # محاسبه مدت زمان انجام
        self.df['duration'] = (self.df['completed_at'] - self.df['created_at']).dt.total_seconds() / 3600
        
        # محاسبه تاخیر
        self.df['delay'] = (self.df['completed_at'] - self.df['created_at']).dt.total_seconds() / 3600 - self.df['estimated_duration']
    
    def get_basic_stats(self) -> Dict[str, Any]:
        """محاسبه آمار پایه"""
        return {
            'total_tasks': len(self.df),
            'completed_tasks': len(self.df[self.df['status'] == 'completed']),
            'pending_tasks': len(self.df[self.df['status'] == 'pending']),
            'completion_rate': len(self.df[self.df['status'] == 'completed']) / len(self.df) if len(self.df) > 0 else 0,
            'avg_duration': self.df['duration'].mean(),
            'avg_delay': self.df['delay'].mean()
        }
    
    def get_priority_stats(self) -> Dict[str, Any]:
        """آمار مربوط به اولویت‌ها"""
        priority_counts = self.df['priority'].value_counts()
        priority_completion = self.df[self.df['status'] == 'completed']['priority'].value_counts()
        
        return {
            'distribution': priority_counts.to_dict(),
            'completion_by_priority': priority_completion.to_dict(),
            'completion_rate_by_priority': (priority_completion / priority_counts).to_dict()
        }
    
    def get_user_stats(self) -> Dict[str, Any]:
        """آمار مربوط به کاربران"""
        user_stats = self.df.groupby('assignee').agg({
            'id': 'count',
            'duration': 'mean',
            'delay': 'mean'
        }).rename(columns={
            'id': 'total_tasks',
            'duration': 'avg_duration',
            'delay': 'avg_delay'
        })
        
        return user_stats.to_dict('index')
    
    def get_trend_analysis(self, days: int = 30) -> Dict[str, Any]:
        """تحلیل روند در بازه زمانی مشخص"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        mask = (self.df['created_at'] >= start_date) & (self.df['created_at'] <= end_date)
        period_df = self.df[mask]
        
        daily_stats = period_df.groupby(period_df['created_at'].dt.date).agg({
            'id': 'count',
            'duration': 'mean',
            'delay': 'mean'
        }).rename(columns={
            'id': 'tasks_count',
            'duration': 'avg_duration',
            'delay': 'avg_delay'
        })
        
        return daily_stats.to_dict('index')
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """محاسبه شاخص‌های عملکرد"""
        # محاسبه نرخ تکمیل به موقع
        on_time_completion = len(self.df[self.df['delay'] <= 0])
        on_time_rate = on_time_completion / len(self.df) if len(self.df) > 0 else 0
        
        # محاسبه میانگین زمان تاخیر
        avg_delay = self.df['delay'].mean()
        
        # محاسبه نرخ تکمیل وظایف با اولویت بالا
        high_priority_tasks = self.df[self.df['priority'] == 'high']
        high_priority_completion = len(high_priority_tasks[high_priority_tasks['status'] == 'completed'])
        high_priority_rate = high_priority_completion / len(high_priority_tasks) if len(high_priority_tasks) > 0 else 0
        
        return {
            'on_time_completion_rate': on_time_rate,
            'average_delay': avg_delay,
            'high_priority_completion_rate': high_priority_rate
        }
    
    def get_efficiency_analysis(self) -> Dict[str, Any]:
        """تحلیل کارایی"""
        # محاسبه نسبت زمان واقعی به زمان تخمینی
        self.df['efficiency_ratio'] = self.df['estimated_duration'] / self.df['duration']
        
        # محاسبه میانگین کارایی
        avg_efficiency = self.df['efficiency_ratio'].mean()
        
        # محاسبه کارایی به تفکیک اولویت
        efficiency_by_priority = self.df.groupby('priority')['efficiency_ratio'].mean()
        
        return {
            'average_efficiency': avg_efficiency,
            'efficiency_by_priority': efficiency_by_priority.to_dict()
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """تولید گزارش جامع"""
        return {
            'basic_stats': self.get_basic_stats(),
            'priority_stats': self.get_priority_stats(),
            'user_stats': self.get_user_stats(),
            'trend_analysis': self.get_trend_analysis(),
            'performance_metrics': self.get_performance_metrics(),
            'efficiency_analysis': self.get_efficiency_analysis()
        }
    
    def format_report(self, report: Dict[str, Any]) -> str:
        """فرمت‌بندی گزارش برای نمایش"""
        basic_stats = report['basic_stats']
        priority_stats = report['priority_stats']
        performance_metrics = report['performance_metrics']
        
        return f"""
📊 گزارش عملکرد سیستم مدیریت وظایف

📈 آمار کلی:
• تعداد کل وظایف: {basic_stats['total_tasks']}
• وظایف تکمیل شده: {basic_stats['completed_tasks']}
• نرخ تکمیل: {basic_stats['completion_rate']:.1%}
• میانگین زمان انجام: {format_duration(basic_stats['avg_duration'] * 3600)}
• میانگین تاخیر: {format_duration(basic_stats['avg_delay'] * 3600)}

⚡ آمار اولویت‌ها:
• توزیع اولویت‌ها: {', '.join(f'{k}: {v}' for k, v in priority_stats['distribution'].items())}
• نرخ تکمیل به تفکیک اولویت: {', '.join(f'{k}: {v:.1%}' for k, v in priority_stats['completion_rate_by_priority'].items())}

🎯 شاخص‌های عملکرد:
• نرخ تکمیل به موقع: {performance_metrics['on_time_completion_rate']:.1%}
• نرخ تکمیل وظایف با اولویت بالا: {performance_metrics['high_priority_completion_rate']:.1%}
• میانگین تاخیر: {format_duration(performance_metrics['average_delay'] * 3600)}

📅 تاریخ گزارش: {convert_to_jalali(datetime.now())}
""" 