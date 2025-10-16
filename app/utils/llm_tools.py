# -*- coding: utf-8 -*-
"""
大模型Function Calling工具集
定义可供大模型调用的函数及其Schema
"""
from datetime import datetime


# ==================== 函数Schema定义 ====================
# 这些Schema用于告诉大模型有哪些函数可以调用

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "create_todo",
            "description": "创建一个新的待办事项。当用户表达要做某事、记录某个任务时调用此函数。",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "待办事项的具体内容"
                    },
                    "notes": {
                        "type": "string",
                        "description": "备注信息，可选"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "截止日期，格式：YYYY-MM-DD HH:MM:SS，可选"
                    }
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_todo_list",
            "description": "查询用户的待办事项列表。可以按状态筛选。",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "completed", "all"],
                        "description": "状态筛选：pending(待办)、completed(已完成)、all(全部)，默认为pending"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_todo",
            "description": "标记一个待办事项为已完成。当用户说完成了某个任务时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "todo_id": {
                        "type": "integer",
                        "description": "待办事项的ID"
                    },
                    "completion_reflection": {
                        "type": "string",
                        "description": "完成感想，用户对完成这个任务的感受或总结，可选"
                    }
                },
                "required": ["todo_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_todo",
            "description": "删除一个待办事项。当用户明确表示要删除某个任务时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "todo_id": {
                        "type": "integer",
                        "description": "待办事项的ID"
                    }
                },
                "required": ["todo_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_todo",
            "description": "更新待办事项的内容、备注或截止日期。",
            "parameters": {
                "type": "object",
                "properties": {
                    "todo_id": {
                        "type": "integer",
                        "description": "待办事项的ID"
                    },
                    "content": {
                        "type": "string",
                        "description": "新的待办内容，可选"
                    },
                    "notes": {
                        "type": "string",
                        "description": "新的备注信息，可选"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "新的截止日期，格式：YYYY-MM-DD HH:MM:SS，可选"
                    }
                },
                "required": ["todo_id"]
            }
        }
    }
]


# ==================== 函数实现 ====================
# 这些函数会被大模型通过Function Calling调用
# 它们会调用相应的服务层方法来执行实际操作

class LLMTools:
    """大模型工具类，封装所有可被Function Calling调用的函数"""
    
    def __init__(self, todo_service, user_id):
        """
        初始化LLM工具类
        
        Args:
            todo_service: 待办事项服务实例
            user_id: 当前用户ID
        """
        self.todo_service = todo_service
        self.user_id = user_id
    
    def create_todo(self, content, notes=None, due_date=None):
        """
        创建待办事项
        
        Args:
            content: 待办内容
            notes: 备注
            due_date: 截止日期字符串
            
        Returns:
            操作结果字典
        """
        try:
            # 解析截止日期
            due_date_obj = None
            if due_date:
                try:
                    due_date_obj = datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S')
                except:
                    try:
                        due_date_obj = datetime.strptime(due_date, '%Y-%m-%d')
                    except:
                        pass
            
            todo = self.todo_service.create_todo(
                user_id=self.user_id,
                content=content,
                notes=notes,
                due_date=due_date_obj
            )
            
            return {
                "success": True,
                "message": f"已创建待办事项：{content}",
                "todo": todo.to_dict()
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"创建失败：{str(e)}"
            }
    
    def get_todo_list(self, status='pending'):
        """
        获取待办列表
        
        Args:
            status: 状态筛选
            
        Returns:
            待办列表
        """
        try:
            todos = self.todo_service.get_user_todos(
                user_id=self.user_id,
                status=None if status == 'all' else status
            )
            
            todo_list = [todo.to_dict() for todo in todos]
            
            return {
                "success": True,
                "count": len(todo_list),
                "todos": todo_list
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"查询失败：{str(e)}"
            }
    
    def complete_todo(self, todo_id, completion_reflection=None):
        """
        完成待办事项
        
        Args:
            todo_id: 待办事项ID
            completion_reflection: 完成感想
            
        Returns:
            操作结果
        """
        try:
            todo = self.todo_service.mark_todo_as_complete(todo_id, self.user_id, completion_reflection)
            if todo:
                return {
                    "success": True,
                    "message": f"已完成：{todo.content}",
                    "todo": todo.to_dict()
                }
            else:
                return {
                    "success": False,
                    "message": "待办事项不存在或无权操作"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"操作失败：{str(e)}"
            }
    
    def delete_todo(self, todo_id):
        """
        删除待办事项
        
        Args:
            todo_id: 待办事项ID
            
        Returns:
            操作结果
        """
        try:
            success = self.todo_service.delete_todo(todo_id, self.user_id)
            if success:
                return {
                    "success": True,
                    "message": "已删除待办事项"
                }
            else:
                return {
                    "success": False,
                    "message": "待办事项不存在或无权操作"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"删除失败：{str(e)}"
            }
    
    def update_todo(self, todo_id, content=None, notes=None, due_date=None):
        """
        更新待办事项
        
        Args:
            todo_id: 待办事项ID
            content: 新内容
            notes: 新备注
            due_date: 新截止日期
            
        Returns:
            操作结果
        """
        try:
            # 解析截止日期
            due_date_obj = None
            if due_date:
                try:
                    due_date_obj = datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S')
                except:
                    try:
                        due_date_obj = datetime.strptime(due_date, '%Y-%m-%d')
                    except:
                        pass
            
            todo = self.todo_service.update_todo(
                todo_id=todo_id,
                user_id=self.user_id,
                content=content,
                notes=notes,
                due_date=due_date_obj
            )
            
            if todo:
                return {
                    "success": True,
                    "message": "已更新待办事项",
                    "todo": todo.to_dict()
                }
            else:
                return {
                    "success": False,
                    "message": "待办事项不存在或无权操作"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"更新失败：{str(e)}"
            }
    
    def execute_tool_call(self, function_name, arguments):
        """
        执行工具调用
        
        Args:
            function_name: 函数名
            arguments: 参数字典
            
        Returns:
            执行结果
        """
        # 获取对应的方法
        method = getattr(self, function_name, None)
        if method and callable(method):
            return method(**arguments)
        else:
            return {
                "success": False,
                "message": f"未知的函数：{function_name}"
            }

