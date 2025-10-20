# -*- coding: utf-8 -*-
"""
图片会话管理服务
管理用户发送图片的会话状态
"""
import os
import requests
import time
from datetime import datetime, timedelta
from collections import defaultdict
import threading


class ImageSessionService:
    """图片会话管理服务"""
    
    def __init__(self, upload_dir='uploads'):
        """
        初始化图片会话服务
        
        Args:
            upload_dir: 图片上传目录
        """
        self.upload_dir = upload_dir
        
        # 确保上传目录存在
        os.makedirs(upload_dir, exist_ok=True)
        
        # 存储结构: {user_id: {"images": [{"path": "...", "timestamp": datetime}], "last_update": datetime}}
        self.sessions = defaultdict(lambda: {"images": [], "last_update": None})
        
        # 线程锁，确保并发安全
        self.lock = threading.Lock()
        
        # 会话超时时间（分钟）
        self.session_timeout_minutes = 10
        
        print(f"图片会话服务已启动 - 上传目录: {upload_dir}, 会话超时: {self.session_timeout_minutes}分钟")
    
    def download_image_from_wechat(self, access_token, media_id, user_id):
        """
        从微信服务器下载图片
        
        Args:
            access_token: 微信AccessToken
            media_id: 微信媒体ID
            user_id: 用户ID
            
        Returns:
            图片保存路径（成功）或 None（失败）
        """
        try:
            # 微信临时素材下载接口
            url = f"https://api.weixin.qq.com/cgi-bin/media/get?access_token={access_token}&media_id={media_id}"
            
            # 发送请求下载图片
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                # 检查是否是图片
                content_type = response.headers.get('Content-Type', '')
                if 'image' not in content_type:
                    print(f"警告: 下载的文件不是图片，Content-Type: {content_type}")
                    return None
                
                # 根据时间生成文件名
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                
                # 从Content-Type获取文件扩展名
                ext = 'jpg'  # 默认扩展名
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = 'jpg'
                elif 'png' in content_type:
                    ext = 'png'
                elif 'gif' in content_type:
                    ext = 'gif'
                elif 'webp' in content_type:
                    ext = 'webp'
                
                # 构建文件路径
                filename = f"{user_id}_{timestamp}.{ext}"
                filepath = os.path.join(self.upload_dir, filename)
                
                # 保存文件
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ 图片下载成功: {filepath} ({len(response.content)} 字节)")
                return filepath
            else:
                print(f"❌ 下载图片失败，HTTP状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                return None
                
        except Exception as e:
            print(f"下载图片异常: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def add_image(self, user_id, image_path):
        """
        添加图片到用户会话
        
        Args:
            user_id: 用户ID
            image_path: 图片路径
            
        Returns:
            当前会话中的图片数量
        """
        with self.lock:
            session = self.sessions[user_id]
            
            # 添加图片
            session["images"].append({
                "path": image_path,
                "timestamp": datetime.now()
            })
            
            # 更新会话时间
            session["last_update"] = datetime.now()
            
            image_count = len(session["images"])
            print(f"用户 {user_id} 的图片会话已更新，当前图片数: {image_count}")
            
            return image_count
    
    def get_session_images(self, user_id):
        """
        获取用户会话中的所有图片
        
        Args:
            user_id: 用户ID
            
        Returns:
            图片路径列表
        """
        with self.lock:
            # 检查会话是否过期
            self._cleanup_expired_session(user_id)
            
            if user_id not in self.sessions:
                return []
            
            return [img["path"] for img in self.sessions[user_id]["images"]]
    
    def clear_session(self, user_id):
        """
        清空用户的图片会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            清除的图片数量
        """
        with self.lock:
            if user_id in self.sessions:
                image_count = len(self.sessions[user_id]["images"])
                del self.sessions[user_id]
                print(f"已清空用户 {user_id} 的图片会话（{image_count} 张图片）")
                return image_count
            return 0
    
    def has_active_session(self, user_id):
        """
        检查用户是否有活跃的图片会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否有活跃会话
        """
        with self.lock:
            # 清理过期会话
            self._cleanup_expired_session(user_id)
            
            if user_id not in self.sessions:
                return False
            
            return len(self.sessions[user_id]["images"]) > 0
    
    def _cleanup_expired_session(self, user_id):
        """
        清理过期的会话（内部方法）
        
        Args:
            user_id: 用户ID
        """
        if user_id not in self.sessions:
            return
        
        session = self.sessions[user_id]
        last_update = session.get("last_update")
        
        if last_update:
            # 检查是否超时
            cutoff_time = datetime.now() - timedelta(minutes=self.session_timeout_minutes)
            if last_update < cutoff_time:
                print(f"用户 {user_id} 的图片会话已过期，自动清空")
                del self.sessions[user_id]
    
    def cleanup_all_expired_sessions(self):
        """
        清理所有过期的会话（可用于定时任务）
        
        Returns:
            清理的会话数量
        """
        with self.lock:
            user_ids = list(self.sessions.keys())
            cleaned_count = 0
            
            cutoff_time = datetime.now() - timedelta(minutes=self.session_timeout_minutes)
            
            for user_id in user_ids:
                session = self.sessions[user_id]
                last_update = session.get("last_update")
                
                if last_update and last_update < cutoff_time:
                    del self.sessions[user_id]
                    cleaned_count += 1
                    print(f"清理过期会话: 用户 {user_id}")
            
            return cleaned_count
    
    def get_stats(self):
        """
        获取图片会话统计信息
        
        Returns:
            统计信息字典
        """
        with self.lock:
            total_sessions = len(self.sessions)
            total_images = sum(len(session["images"]) for session in self.sessions.values())
            
            return {
                "total_sessions": total_sessions,
                "total_images": total_images,
                "avg_images_per_session": round(total_images / max(total_sessions, 1), 2),
                "session_timeout_minutes": self.session_timeout_minutes
            }

