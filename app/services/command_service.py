# -*- coding: utf-8 -*-
"""
系统命令服务
处理系统级别的命令（不经过LLM）
"""


class CommandService:
    """系统命令服务"""
    
    def __init__(self, conversation_service, todo_service):
        """
        初始化命令服务
        
        Args:
            conversation_service: 对话历史服务实例
            todo_service: 待办事项服务实例
        """
        self.conversation_service = conversation_service
        self.todo_service = todo_service
        
        # 定义系统命令映射（命令名 -> 处理函数）
        self.commands = {
            'clear': self._clear_history,
            'help': self._show_help,
            '帮助': self._show_help,
            'reset': self._reset_all,
            '重置': self._reset_all,
            'stats': self._show_stats,
            '统计': self._show_stats,
        }
    
    def is_system_command(self, message):
        """
        判断是否是系统命令
        
        Args:
            message: 用户消息
            
        Returns:
            是否是系统命令
        """
        return message.strip().lower() in self.commands
    
    def execute_command(self, message, user_id):
        """
        执行系统命令
        
        Args:
            message: 用户消息
            user_id: 用户ID
            
        Returns:
            命令执行结果（文本）
        """
        command = message.strip().lower()
        if command in self.commands:
            try:
                return self.commands[command](user_id)
            except Exception as e:
                print(f"执行命令 '{command}' 失败: {e}")
                import traceback
                traceback.print_exc()
                return f"[sys] ❌ 命令执行失败：{str(e)}"
        return None
    
    def _clear_history(self, user_id):
        """
        清空对话历史
        
        Args:
            user_id: 用户ID
            
        Returns:
            执行结果
        """
        cleared_count = self.conversation_service.clear_user_history(user_id)
        return f"[sys] ✅ 已清空对话历史！\n共清除了 {cleared_count} 条记录。"
    
    def _show_help(self, user_id):
        """
        显示帮助信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            帮助文本
        """
        help_text = """[sys] 📖 系统命令帮助

🔧 系统命令（直接输入即可）：
• clear - 清空对话历史
• help / 帮助 - 显示此帮助信息
• stats / 统计 - 查看统计信息
• reset / 重置 - 重置所有数据（慎用）

💡 使用提示：
直接和我说话，我会帮你管理待办事项！
例如：
• "明天下午开会"
• "查看我的待办"
• "完成第一个任务"
"""
        return help_text
    
    def _reset_all(self, user_id):
        """
        重置所有数据（慎用）
        
        Args:
            user_id: 用户ID
            
        Returns:
            执行结果
        """
        # 清空对话历史
        history_count = self.conversation_service.clear_user_history(user_id)
        
        # 删除所有待办事项
        todos = self.todo_service.get_user_todos(user_id)
        todo_count = len(todos)
        for todo in todos:
            self.todo_service.delete_todo(todo.id, user_id)
        
        return f"""[sys] ⚠️ 已重置所有数据！

清除内容：
• 对话历史：{history_count} 条
• 待办事项：{todo_count} 个

现在可以重新开始使用了！"""
    
    def _show_stats(self, user_id):
        """
        显示统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            统计信息文本
        """
        # 获取对话历史数量
        conversation_history = self.conversation_service.get_recent_history(user_id)
        history_count = len(conversation_history)
        
        # 获取待办事项统计
        all_todos = self.todo_service.get_user_todos(user_id)
        pending_todos = self.todo_service.get_user_todos(user_id, status='pending')
        completed_todos = self.todo_service.get_user_todos(user_id, status='completed')
        
        # 计算完成率
        completion_rate = 0
        if len(all_todos) > 0:
            completion_rate = (len(completed_todos) / len(all_todos)) * 100
        
        stats_text = f"""[sys] 📊 数据统计

💬 对话数据：
• 历史对话：{history_count} 条

✅ 待办数据：
• 总计：{len(all_todos)} 个
• 待完成：{len(pending_todos)} 个
• 已完成：{len(completed_todos)} 个
• 完成率：{completion_rate:.1f}%

🎯 继续加油！"""
        
        return stats_text
    
    def get_all_commands(self):
        """
        获取所有支持的系统命令
        
        Returns:
            命令列表
        """
        return list(self.commands.keys())

