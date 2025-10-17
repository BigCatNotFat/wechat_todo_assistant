# -*- coding: utf-8 -*-
"""
微信服务
处理微信消息的解析、回复和API调用
"""
import time
import requests
from wechatpy import parse_message, create_reply
from wechatpy.replies import TextReply
from app.services.conversation_service import ConversationService


class WeChatService:
    """微信服务"""
    
    def __init__(self, config):
        """
        初始化微信服务
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.app_id = config['WECHAT_APP_ID']
        self.app_secret = config['WECHAT_APP_SECRET']
        self.access_token = None
        self.access_token_expires_at = 0
        
        # 初始化对话历史服务
        self.conversation_service = ConversationService(
            max_history_rounds=10,  # 最多保留10轮对话
            max_history_hours=24     # 对话历史保留24小时
        )
    
    def get_access_token(self):
        """
        获取AccessToken（带缓存）
        
        Returns:
            AccessToken字符串
        """
        # 如果token未过期，直接返回
        if self.access_token and time.time() < self.access_token_expires_at:
            return self.access_token
        
        # 否则重新获取
        try:
            url = "https://api.weixin.qq.com/cgi-bin/token"
            params = {
                "grant_type": "client_credential",
                "appid": self.app_id,
                "secret": self.app_secret
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'access_token' in data:
                self.access_token = data['access_token']
                # 提前10分钟过期，留出余量
                self.access_token_expires_at = time.time() + data.get('expires_in', 7200) - 600
                print(f"成功获取AccessToken，有效期至: {time.ctime(self.access_token_expires_at)}")
                return self.access_token
            else:
                print(f"获取AccessToken失败: {data}")
                return None
                
        except Exception as e:
            print(f"获取AccessToken异常: {e}")
            return None
    
    def parse_message(self, xml_data):
        """
        解析微信消息
        
        Args:
            xml_data: 解密后的XML数据
            
        Returns:
            消息对象
        """
        try:
            msg = parse_message(xml_data)
            return msg
        except Exception as e:
            print(f"解析消息失败: {e}")
            return None
    
    def create_text_reply(self, content, message):
        """
        创建文本回复
        
        Args:
            content: 回复内容
            message: 原始消息对象
            
        Returns:
            回复消息的XML字符串
        """
        try:
            reply = create_reply(content, message)
            return reply.render()
        except Exception as e:
            print(f"创建回复失败: {e}")
            return "success"
    
    def send_customer_message(self, openid, content):
        """
        发送客服消息（主动推送）
        
        Args:
            openid: 用户OpenID
            content: 消息内容
            
        Returns:
            是否发送成功
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                print("无法获取AccessToken，发送消息失败")
                return False
            
            url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
            
            data = {
                "touser": openid,
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
            
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('errcode') == 0:
                print(f"成功发送客服消息给: {openid}")
                return True
            else:
                print(f"发送客服消息失败: {result}")
                return False
                
        except Exception as e:
            print(f"发送客服消息异常: {e}")
            return False
    
    def handle_message(self, msg, llm_service, user_id, command_service=None):
        """
        处理微信消息
        
        Args:
            msg: 消息对象
            llm_service: 大模型服务实例
            user_id: 用户ID
            command_service: 命令服务实例（可选）
            
        Returns:
            回复内容
        """
        try:
            # 目前只处理文本消息
            if msg.type == 'text':
                user_message = msg.content.strip()
                print(f"收到用户 {user_id} 的消息: {user_message}")
                
                # ✅ 优先检查是否是系统命令
                if command_service and command_service.is_system_command(user_message):
                    print(f"检测到系统命令: {user_message}")
                    return command_service.execute_command(user_message, user_id)
                
                # 获取用户的对话历史
                conversation_history = self.conversation_service.get_recent_history(user_id)
                print(f"加载了 {len(conversation_history)} 条历史对话记录")
                
                # 保存用户消息到对话历史
                self.conversation_service.add_message(
                    user_id=user_id,
                    role='user',
                    content=user_message
                )
                
                # 调用大模型处理（传入对话历史）
                reply_content = llm_service.chat_with_function_calling(
                    user_id=user_id,
                    user_message=user_message,
                    conversation_history=conversation_history
                )
                
                # 保存助手回复到对话历史
                self.conversation_service.add_message(
                    user_id=user_id,
                    role='assistant',
                    content=reply_content
                )
                
                return reply_content
            
            elif msg.type == 'event':
                # 处理事件消息
                if msg.event == 'subscribe':
                    return '欢迎关注在办小助手！\n\n我可以帮你管理待办事项，你可以：\n• 直接告诉我要做什么，我会帮你记录\n• 说"查看待办"来查看任务列表\n• 说"完成XX"来标记任务完成\n• 每天早上9点我会给你发送任务规划\n\n快来试试吧！'
                elif msg.event == 'unsubscribe':
                    print(f"用户取消关注: {msg.source}")
                    # 清空用户的对话历史
                    self.conversation_service.clear_user_history(user_id)
                    return "success"
                else:
                    return "收到您的消息"
            
            else:
                return "抱歉，我暂时只能处理文字消息哦~"
                
        except Exception as e:
            print(f"处理消息异常: {e}")
            import traceback
            traceback.print_exc()
            return "抱歉，处理消息时出现了问题"

