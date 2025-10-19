# -*- coding: utf-8 -*-
"""
记账服务
处理用户收支记录的业务逻辑
"""
from datetime import datetime, timedelta
from app.database.db import db
from app.models.transaction import Transaction
from app.models.user import User


class TransactionService:
    """记账服务"""
    
    @staticmethod
    def create_expense(user_id, amount, notes=None):
        """
        创建支出记录
        
        Args:
            user_id: 用户ID
            amount: 支出金额（正数）
            notes: 备注说明
            
        Returns:
            创建的Transaction对象
        """
        # 确保金额为负数（支出）
        if amount > 0:
            amount = -amount
        
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            type='expense',
            notes=notes
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction
    
    @staticmethod
    def create_income(user_id, amount, notes=None):
        """
        创建收入记录
        
        Args:
            user_id: 用户ID
            amount: 收入金额（正数）
            notes: 备注说明
            
        Returns:
            创建的Transaction对象
        """
        # 确保金额为正数（收入）
        if amount < 0:
            amount = -amount
        
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            type='income',
            notes=notes
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction
    
    @staticmethod
    def adjust_balance(user_id, amount, notes=None):
        """
        资金矫正（用于修正账户余额）
        
        Args:
            user_id: 用户ID
            amount: 矫正金额（可正可负）
            notes: 矫正说明
            
        Returns:
            创建的Transaction对象
        """
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            type='adjustment',
            notes=notes or '资金矫正'
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction
    
    @staticmethod
    def get_user_transactions(user_id, transaction_type=None, limit=None, days=None):
        """
        获取用户的记账记录
        
        Args:
            user_id: 用户ID
            transaction_type: 类型筛选（expense/income/adjustment），None表示全部
            limit: 返回数量限制
            days: 查询最近N天的记录
            
        Returns:
            Transaction对象列表
        """
        query = Transaction.query.filter_by(user_id=user_id)
        
        if transaction_type:
            query = query.filter_by(type=transaction_type)
        
        if days:
            start_date = datetime.now() - timedelta(days=days)
            query = query.filter(Transaction.created_at >= start_date)
        
        query = query.order_by(Transaction.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_balance(user_id):
        """
        获取用户当前余额（所有记录的金额总和）
        
        Args:
            user_id: 用户ID
            
        Returns:
            当前余额
        """
        result = db.session.query(db.func.sum(Transaction.amount)).filter_by(user_id=user_id).scalar()
        return result if result else 0.0
    
    @staticmethod
    def get_period_summary(user_id, days=30):
        """
        获取指定时间段的收支汇总
        
        Args:
            user_id: 用户ID
            days: 统计最近N天，默认30天
            
        Returns:
            字典，包含总收入、总支出、净收益
        """
        start_date = datetime.now() - timedelta(days=days)
        
        # 查询该时间段内的所有记录
        transactions = Transaction.query.filter_by(user_id=user_id).filter(
            Transaction.created_at >= start_date
        ).all()
        
        total_income = sum(t.amount for t in transactions if t.type == 'income')
        total_expense = sum(abs(t.amount) for t in transactions if t.type == 'expense')
        total_adjustment = sum(t.amount for t in transactions if t.type == 'adjustment')
        
        return {
            'period_days': days,
            'total_income': total_income,
            'total_expense': total_expense,
            'net_income': total_income - total_expense,
            'total_adjustment': total_adjustment,
            'transaction_count': len(transactions)
        }
    
    @staticmethod
    def delete_transaction(transaction_id, user_id):
        """
        删除记账记录
        
        Args:
            transaction_id: 记账记录ID
            user_id: 用户ID（用于权限验证）
            
        Returns:
            是否删除成功
        """
        transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
        if transaction:
            db.session.delete(transaction)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_transaction_by_id(transaction_id, user_id=None):
        """
        根据ID获取记账记录
        
        Args:
            transaction_id: 记账记录ID
            user_id: 用户ID，用于权限验证
            
        Returns:
            Transaction对象或None
        """
        query = Transaction.query.filter_by(id=transaction_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.first()


