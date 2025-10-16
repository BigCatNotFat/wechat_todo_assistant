# -*- coding: utf-8 -*-
"""
待办事项服务
处理待办事项的增删改查业务逻辑
"""
from datetime import datetime
from app.database.db import db
from app.models.todo_item import TodoItem
from app.models.user import User


class TodoService:
    """待办事项服务"""
    
    @staticmethod
    def create_todo(user_id, content, notes=None, due_date=None):
        """
        创建待办事项
        
        Args:
            user_id: 用户ID
            content: 待办内容
            notes: 备注
            due_date: 截止日期
            
        Returns:
            创建的TodoItem对象
        """
        todo = TodoItem(
            user_id=user_id,
            content=content,
            notes=notes,
            due_date=due_date,
            status='pending'
        )
        db.session.add(todo)
        db.session.commit()
        return todo
    
    @staticmethod
    def get_user_todos(user_id, status=None, limit=None):
        """
        获取用户的待办列表
        
        Args:
            user_id: 用户ID
            status: 状态筛选，None表示全部
            limit: 返回数量限制
            
        Returns:
            TodoItem对象列表
        """
        query = TodoItem.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(TodoItem.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_todo_by_id(todo_id, user_id=None):
        """
        根据ID获取待办事项
        
        Args:
            todo_id: 待办事项ID
            user_id: 用户ID，用于权限验证
            
        Returns:
            TodoItem对象或None
        """
        query = TodoItem.query.filter_by(id=todo_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.first()
    
    @staticmethod
    def mark_todo_as_complete(todo_id, user_id, completion_reflection=None):
        """
        标记待办事项为已完成
        
        Args:
            todo_id: 待办事项ID
            user_id: 用户ID
            completion_reflection: 完成感想
            
        Returns:
            更新后的TodoItem对象或None
        """
        todo = TodoService.get_todo_by_id(todo_id, user_id)
        if todo:
            todo.status = 'completed'
            todo.completed_at = datetime.now()
            if completion_reflection:
                todo.completion_reflection = completion_reflection
            db.session.commit()
        return todo
    
    @staticmethod
    def delete_todo(todo_id, user_id):
        """
        删除待办事项
        
        Args:
            todo_id: 待办事项ID
            user_id: 用户ID
            
        Returns:
            是否删除成功
        """
        todo = TodoService.get_todo_by_id(todo_id, user_id)
        if todo:
            db.session.delete(todo)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def update_todo(todo_id, user_id, content=None, notes=None, due_date=None):
        """
        更新待办事项
        
        Args:
            todo_id: 待办事项ID
            user_id: 用户ID
            content: 新内容
            notes: 新备注
            due_date: 新截止日期
            
        Returns:
            更新后的TodoItem对象或None
        """
        todo = TodoService.get_todo_by_id(todo_id, user_id)
        if todo:
            if content is not None:
                todo.content = content
            if notes is not None:
                todo.notes = notes
            if due_date is not None:
                todo.due_date = due_date
            db.session.commit()
        return todo
    
    @staticmethod
    def get_today_todos(user_id):
        """
        获取今天的待办事项（未完成的）
        
        Args:
            user_id: 用户ID
            
        Returns:
            TodoItem对象列表
        """
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 获取所有未完成的待办
        return TodoItem.query.filter_by(
            user_id=user_id,
            status='pending'
        ).filter(
            (TodoItem.created_at >= today_start) | (TodoItem.due_date >= today_start)
        ).order_by(TodoItem.created_at.asc()).all()
    
    @staticmethod
    def get_yesterday_completed_todos(user_id):
        """
        获取昨天完成的待办事项
        
        Args:
            user_id: 用户ID
            
        Returns:
            TodoItem对象列表
        """
        from datetime import timedelta
        yesterday_start = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_end = yesterday_start.replace(hour=23, minute=59, second=59)
        
        return TodoItem.query.filter_by(
            user_id=user_id,
            status='completed'
        ).filter(
            TodoItem.completed_at >= yesterday_start,
            TodoItem.completed_at <= yesterday_end
        ).order_by(TodoItem.completed_at.desc()).all()
    
    @staticmethod
    def get_or_create_user(openid, nickname=None):
        """
        获取或创建用户
        
        Args:
            openid: 微信OpenID
            nickname: 昵称
            
        Returns:
            User对象
        """
        user = User.query.filter_by(openid=openid).first()
        if not user:
            user = User(openid=openid, nickname=nickname)
            db.session.add(user)
            db.session.commit()
        return user

