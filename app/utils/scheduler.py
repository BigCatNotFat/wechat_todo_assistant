# -*- coding: utf-8 -*-
"""
定时任务调度器
使用APScheduler实现定时任务
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz


class Scheduler:
    """定时任务调度器"""
    
    def __init__(self, timezone='Asia/Shanghai'):
        """
        初始化调度器
        
        Args:
            timezone: 时区
        """
        self.timezone = pytz.timezone(timezone)
        self.scheduler = BackgroundScheduler(timezone=self.timezone)
        self.is_running = False
    
    def start(self):
        """启动调度器"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            print(f"定时任务调度器已启动，时区: {self.timezone}")
    
    def shutdown(self):
        """关闭调度器"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            print("定时任务调度器已关闭")
    
    def add_daily_job(self, func, time_str, job_id=None, **kwargs):
        """
        添加每日定时任务
        
        Args:
            func: 要执行的函数
            time_str: 时间字符串，格式：'HH:MM'
            job_id: 任务ID，用于后续管理
            **kwargs: 传递给函数的其他参数
        """
        try:
            hour, minute = map(int, time_str.split(':'))
            
            trigger = CronTrigger(
                hour=hour,
                minute=minute,
                timezone=self.timezone
            )
            
            self.scheduler.add_job(
                func,
                trigger=trigger,
                id=job_id,
                kwargs=kwargs,
                replace_existing=True
            )
            
            print(f"已添加每日任务 [{job_id}]，执行时间: {time_str}")
        except Exception as e:
            print(f"添加定时任务失败: {e}")
    
    def remove_job(self, job_id):
        """
        移除定时任务
        
        Args:
            job_id: 任务ID
        """
        try:
            self.scheduler.remove_job(job_id)
            print(f"已移除定时任务: {job_id}")
        except Exception as e:
            print(f"移除定时任务失败: {e}")
    
    def get_jobs(self):
        """获取所有任务"""
        return self.scheduler.get_jobs()
    
    def print_jobs(self):
        """打印所有任务"""
        jobs = self.get_jobs()
        if jobs:
            print("\n当前定时任务列表:")
            for job in jobs:
                print(f"  - [{job.id}] 下次执行: {job.next_run_time}")
        else:
            print("\n当前没有定时任务")

