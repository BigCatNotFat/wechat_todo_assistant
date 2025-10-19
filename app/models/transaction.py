# -*- coding: utf-8 -*-
"""
记账模型
存储用户的收支记录
"""
from datetime import datetime
from app.database.db import db


class Transaction(db.Model):
    """记账表"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True, comment='用户ID')
    amount = db.Column(db.Float, nullable=False, comment='金额（正数为收入，负数为支出）')
    type = db.Column(db.String(20), nullable=False, comment='类型: expense支出, income收入, adjustment矫正')
    notes = db.Column(db.Text, comment='备注说明')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='记录时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def __repr__(self):
        return f'<Transaction {self.id}: {self.type} {self.amount}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'type': self.type,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


