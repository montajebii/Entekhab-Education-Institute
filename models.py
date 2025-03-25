import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any, Optional
import joblib
import os
from config import *

class TaskDurationPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.model_path = 'task_duration_model.joblib'
        self.scaler_path = 'task_duration_scaler.joblib'
        
    def prepare_features(self, tasks_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """آماده‌سازی ویژگی‌ها برای آموزش مدل"""
        df = pd.DataFrame(tasks_data)
        
        # تبدیل اولویت‌ها به اعداد
        priority_map = {'low': 1, 'medium': 2, 'high': 3}
        df['priority_numeric'] = df['priority'].map(priority_map)
        
        # محاسبه طول توضیحات
        df['description_length'] = df['description'].str.len()
        
        # محاسبه تعداد کلمات
        df['word_count'] = df['description'].str.split().str.len()
        
        # محاسبه تعداد تگ‌ها
        df['tag_count'] = df['tags'].str.split(',').str.len()
        
        # انتخاب ویژگی‌های نهایی
        features = [
            'priority_numeric',
            'description_length',
            'word_count',
            'tag_count'
        ]
        
        return df[features]
    
    def prepare_target(self, tasks_data: List[Dict[str, Any]]) -> np.ndarray:
        """آماده‌سازی متغیر هدف (زمان انجام)"""
        df = pd.DataFrame(tasks_data)
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['completed_at'] = pd.to_datetime(df['completed_at'])
        return (df['completed_at'] - df['created_at']).dt.total_seconds() / 3600
    
    def train(self, tasks_data: List[Dict[str, Any]]) -> None:
        """آموزش مدل"""
        if len(tasks_data) < MIN_TASKS_FOR_PREDICTION:
            raise ValueError(f"حداقل {MIN_TASKS_FOR_PREDICTION} وظیفه برای آموزش مدل نیاز است")
        
        X = self.prepare_features(tasks_data)
        y = self.prepare_target(tasks_data)
        
        # نرمال‌سازی ویژگی‌ها
        X_scaled = self.scaler.fit_transform(X)
        
        # آموزش مدل
        self.model.fit(X_scaled, y)
        
        # ذخیره مدل و اسکیلر
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
    
    def load_model(self) -> None:
        """بارگذاری مدل ذخیره شده"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
    
    def predict(self, task_features: Dict[str, Any]) -> float:
        """پیش‌بینی زمان انجام وظیفه"""
        if not hasattr(self, 'model') or not hasattr(self, 'scaler'):
            self.load_model()
        
        # آماده‌سازی ویژگی‌ها
        features = pd.DataFrame([task_features])
        features = self.prepare_features(features)
        
        # نرمال‌سازی ویژگی‌ها
        features_scaled = self.scaler.transform(features)
        
        # پیش‌بینی
        prediction = self.model.predict(features_scaled)[0]
        
        # محاسبه فاصله اطمینان
        std = np.std([tree.predict(features_scaled) for tree in self.model.estimators_])
        
        return {
            'prediction': max(0, prediction),
            'confidence': 1 - (std / prediction) if prediction > 0 else 0
        }

class TaskPriorityPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.model_path = 'task_priority_model.joblib'
        self.scaler_path = 'task_priority_scaler.joblib'
    
    def prepare_features(self, tasks_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """آماده‌سازی ویژگی‌ها برای آموزش مدل"""
        df = pd.DataFrame(tasks_data)
        
        # محاسبه ویژگی‌های متنی
        df['description_length'] = df['description'].str.len()
        df['word_count'] = df['description'].str.split().str.len()
        df['tag_count'] = df['tags'].str.split(',').str.len()
        
        # محاسبه ویژگی‌های زمانی
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['hour'] = df['created_at'].dt.hour
        df['day_of_week'] = df['created_at'].dt.dayofweek
        
        # انتخاب ویژگی‌های نهایی
        features = [
            'description_length',
            'word_count',
            'tag_count',
            'hour',
            'day_of_week'
        ]
        
        return df[features]
    
    def prepare_target(self, tasks_data: List[Dict[str, Any]]) -> np.ndarray:
        """آماده‌سازی متغیر هدف (اولویت)"""
        df = pd.DataFrame(tasks_data)
        priority_map = {'low': 1, 'medium': 2, 'high': 3}
        return df['priority'].map(priority_map)
    
    def train(self, tasks_data: List[Dict[str, Any]]) -> None:
        """آموزش مدل"""
        if len(tasks_data) < MIN_TASKS_FOR_PREDICTION:
            raise ValueError(f"حداقل {MIN_TASKS_FOR_PREDICTION} وظیفه برای آموزش مدل نیاز است")
        
        X = self.prepare_features(tasks_data)
        y = self.prepare_target(tasks_data)
        
        # نرمال‌سازی ویژگی‌ها
        X_scaled = self.scaler.fit_transform(X)
        
        # آموزش مدل
        self.model.fit(X_scaled, y)
        
        # ذخیره مدل و اسکیلر
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
    
    def load_model(self) -> None:
        """بارگذاری مدل ذخیره شده"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
    
    def predict(self, task_features: Dict[str, Any]) -> Dict[str, Any]:
        """پیش‌بینی اولویت وظیفه"""
        if not hasattr(self, 'model') or not hasattr(self, 'scaler'):
            self.load_model()
        
        # آماده‌سازی ویژگی‌ها
        features = pd.DataFrame([task_features])
        features = self.prepare_features(features)
        
        # نرمال‌سازی ویژگی‌ها
        features_scaled = self.scaler.transform(features)
        
        # پیش‌بینی
        prediction = self.model.predict(features_scaled)[0]
        
        # تبدیل پیش‌بینی به اولویت
        priority_map = {1: 'low', 2: 'medium', 3: 'high'}
        predicted_priority = priority_map[round(prediction)]
        
        # محاسبه اطمینان
        confidence = 1 - abs(prediction - round(prediction))
        
        return {
            'priority': predicted_priority,
            'confidence': confidence
        } 