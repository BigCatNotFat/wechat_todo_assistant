# -*- coding: utf-8 -*-
"""
对话历史管理服务
基于内存存储用户的对话历史，支持上下文记忆
"""
from datetime import datetime, timedelta
from collections import defaultdict
import threading


class ConversationService:
    """对话历史管理服务"""
    
    def __init__(self, max_history_rounds=10, max_history_hours=24):
        """
        初始化对话服务
        
        Args:
            max_history_rounds: 最多保留多少轮对话（每轮包含用户+助手两条消息）
            max_history_hours: 对话历史最长保留时间（小时）
        """
        self.max_history_rounds = max_history_rounds
        self.max_history_hours = max_history_hours
        
        # 存储结构: {user_id: [{"role": "user/assistant", "content": "...", "timestamp": datetime}, ...]}
        self.conversations = defaultdict(list)
        
        # 线程锁，确保并发安全
        self.lock = threading.Lock()
        
        print(f"对话历史服务已启动 - 最多保留{max_history_rounds}轮对话，{max_history_hours}小时内有效")
    
    def add_message(self, user_id, role, content, image_data=None):
        """
        添加一条消息到对话历史
        
        Args:
            user_id: 用户ID
            role: 角色 (user/assistant)
            content: 消息内容
            image_data: 图片数据（可选），格式为 {"bytes": bytes, "mime_type": str}
        """
        with self.lock:
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.now()
            }
            
            # 如果有图片数据，添加到消息中
            if image_data:
                message["image_data"] = image_data
            
            self.conversations[user_id].append(message)
            
            # 自动清理过期和超量的历史记录
            self._cleanup_history(user_id)
    
    def get_recent_history(self, user_id, include_timestamp=False):
        """
        获取用户最近的对话历史
        
        Args:
            user_id: 用户ID
            include_timestamp: 是否包含时间戳（默认False，返回给LLM时不需要）
            
        Returns:
            对话历史列表，格式为 [{"role": "user", "content": "...", "image_data": {...}}, ...]
        """
        with self.lock:
            # 先清理过期记录
            self._cleanup_history(user_id)
            
            if user_id not in self.conversations:
                return []
            
            # 返回历史记录
            if include_timestamp:
                return self.conversations[user_id].copy()
            else:
                # 不包含时间戳，返回role、content和image_data（供LLM使用）
                result = []
                for msg in self.conversations[user_id]:
                    history_msg = {"role": msg["role"], "content": msg["content"]}
                    # 如果有图片数据，也包含进去
                    if "image_data" in msg:
                        history_msg["image_data"] = msg["image_data"]
                    result.append(history_msg)
                return result
    
    def clear_user_history(self, user_id):
        """
        清空指定用户的对话历史
        
        Args:
            user_id: 用户ID
            
        Returns:
            清除的消息数量
        """
        with self.lock:
            if user_id in self.conversations:
                cleared_count = len(self.conversations[user_id])
                del self.conversations[user_id]
                print(f"已清空用户 {user_id} 的对话历史（{cleared_count} 条消息）")
                return cleared_count
            return 0
    
    def get_user_count(self):
        """
        获取当前有对话历史的用户数量
        
        Returns:
            用户数量
        """
        with self.lock:
            return len(self.conversations)
    
    def get_total_messages(self):
        """
        获取所有用户的总消息数
        
        Returns:
            消息总数
        """
        with self.lock:
            return sum(len(msgs) for msgs in self.conversations.values())
    
    def _cleanup_history(self, user_id):
        """
        清理用户的对话历史（内部方法）
        
        清理策略：
        1. 删除超过时间限制的消息
        2. 如果消息数量超过限制，保留最近的N条
        
        Args:
            user_id: 用户ID
        """
        if user_id not in self.conversations:
            return
        
        messages = self.conversations[user_id]
        
        # 1. 按时间清理：删除过期消息
        cutoff_time = datetime.now() - timedelta(hours=self.max_history_hours)
        messages = [msg for msg in messages if msg["timestamp"] > cutoff_time]
        
        # 2. 按数量清理：保留最近的消息
        # max_history_rounds是轮数，每轮有2条消息（user+assistant）
        max_messages = self.max_history_rounds * 2
        if len(messages) > max_messages:
            messages = messages[-max_messages:]
        
        # 更新存储
        if messages:
            self.conversations[user_id] = messages
        else:
            # 如果没有消息了，删除该用户
            del self.conversations[user_id]
    
    def cleanup_all_expired(self):
        """
        清理所有用户的过期对话历史（可用于定时任务）
        
        Returns:
            清理的用户数量
        """
        with self.lock:
            user_ids = list(self.conversations.keys())
            cleaned_count = 0
            
            for user_id in user_ids:
                before_count = len(self.conversations.get(user_id, []))
                self._cleanup_history(user_id)
                after_count = len(self.conversations.get(user_id, []))
                
                if before_count != after_count:
                    cleaned_count += 1
            
            return cleaned_count
    
    def get_stats(self):
        """
        获取对话历史统计信息
        
        Returns:
            统计信息字典
        """
        with self.lock:
            return {
                "total_users": self.get_user_count(),
                "total_messages": self.get_total_messages(),
                "avg_messages_per_user": round(self.get_total_messages() / max(self.get_user_count(), 1), 2),
                "max_history_rounds": self.max_history_rounds,
                "max_history_hours": self.max_history_hours
            }

