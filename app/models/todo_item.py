# -*- coding: utf-8 -*-
"""
待办事项模型
存储用户的待办任务
"""
from datetime import datetime
from app.database.db import db


class TodoItem(db.Model):
    """待办事项表"""
    __tablename__ = 'todo_items'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True, comment='用户ID')
    content = db.Column(db.Text, nullable=False, comment='待办内容')
    status = db.Column(db.String(20), default='pending', comment='状态: pending待办, completed已完成, cancelled已取消')
    notes = db.Column(db.Text, comment='备注')
    due_date = db.Column(db.DateTime, comment='截止日期')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    completed_at = db.Column(db.DateTime, comment='完成时间')
    completion_reflection = db.Column(db.Text, comment='完成感想')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def __repr__(self):
        return f'<TodoItem {self.id}: {self.content[:20]}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'status': self.status,
            'notes': self.notes,
            'due_date': self.due_date.strftime('%Y-%m-%d %H:%M:%S') if self.due_date else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.completed_at else None,
            'completion_reflection': self.completion_reflection,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

