# -*- coding: utf-8 -*-
"""
微信服务
处理微信消息的解析、回复和API调用
"""
import time
import re
import json
import requests
from wechatpy import parse_message, create_reply
from wechatpy.replies import TextReply
from app.services.conversation_service import ConversationService


class WeChatService:
    """微信服务"""
    
    def __init__(self, config, image_session_service=None):
        """
        初始化微信服务
        
        Args:
            config: 配置对象
            image_session_service: 图片会话服务实例（可选）
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
        
        # 初始化图片会话服务
        self.image_session_service = image_session_service
    
    @staticmethod
    def clean_markdown(text):
        """
        清理文本中的Markdown格式，使其更适合微信文本消息显示
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的纯文本
        """
        if not text:
            return text
        
        # 移除粗体标记 **text** 或 __text__
        text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        
        # 移除斜体标记 *text* 或 _text_ (但保留作为列表项的星号)
        text = re.sub(r'(?<!\n)\*([^\*\n]+)\*', r'\1', text)
        text = re.sub(r'(?<!\n)_([^_\n]+)_', r'\1', text)
        
        # 移除行内代码标记 `code`
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # 移除标题标记 # 或 ##
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # 移除删除线标记 ~~text~~
        text = re.sub(r'~~([^~]+)~~', r'\1', text)
        
        # 清理多余的空行（超过2个连续换行）
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
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
    
    def _split_message(self, content, max_length=500):
        """
        将长消息分割成多段（每段不超过指定长度）
        
        Args:
            content: 消息内容
            max_length: 每段最大长度（默认500，微信客服消息限制约600字符，留空间给序号标记）
            
        Returns:
            消息段列表
        """
        if len(content) <= max_length:
            return [content]
        
        segments = []
        lines = content.split('\n')
        current_segment = ""
        
        for line in lines:
            # 如果单行就超过长度，需要强制切分
            if len(line) > max_length:
                if current_segment:
                    segments.append(current_segment.strip())
                    current_segment = ""
                
                # 强制切分长行
                for i in range(0, len(line), max_length):
                    segments.append(line[i:i+max_length])
            else:
                # 检查加上当前行是否超长
                if len(current_segment) + len(line) + 1 > max_length:
                    segments.append(current_segment.strip())
                    current_segment = line + '\n'
                else:
                    current_segment += line + '\n'
        
        # 添加最后一段
        if current_segment.strip():
            segments.append(current_segment.strip())
        
        return segments
    
    def send_customer_message(self, openid, content):
        """
        发送客服消息（主动推送）
        支持自动分段发送长消息
        
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
            
            # 清理Markdown格式
            content = self.clean_markdown(content)
            
            # 检查消息长度，微信客服消息限制约为 600 字符
            # 将消息分段（每段500字符，留出空间给序号标记）
            segments = self._split_message(content, max_length=500)
            
            # ⚠️ 微信客服消息限制：单次会话最多发送5条消息（错误码45047）
            MAX_SEGMENTS = 5
            if len(segments) > MAX_SEGMENTS:
                print(f"⚠️ 消息分段超过限制（{len(segments)} > {MAX_SEGMENTS}），将截断到{MAX_SEGMENTS}段")
                segments = segments[:MAX_SEGMENTS]
                # 在最后一段添加省略提示
                segments[-1] += "\n\n... (内容过长，已省略部分信息)"
            
            if len(segments) > 1:
                print(f"📨 消息过长（{len(content)} 字符），将分 {len(segments)} 段发送")
            
            url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
            
            # 发送每一段消息
            all_success = True
            for i, segment in enumerate(segments):
                # 如果有多段，添加序号标记
                if len(segments) > 1:
                    segment_content = f"[{i+1}/{len(segments)}]\n\n{segment}"
                else:
                    segment_content = segment
                
                # 详细日志：显示每段的实际长度
                print(f"📝 第 {i+1}/{len(segments)} 段 - 原始长度: {len(segment)}, 加序号后: {len(segment_content)} 字符")
                
                # 最后安全检查：如果加上序号后还是超长，强制截断到580字符
                if len(segment_content) > 580:
                    print(f"⚠️ 警告：第 {i+1} 段消息超长（{len(segment_content)} 字符），强制截断到580字符")
                    segment_content = segment_content[:580] + "..."
                    print(f"✂️ 截断后长度: {len(segment_content)} 字符")
                
                data = {
                    "touser": openid,
                    "msgtype": "text",
                    "text": {
                        "content": segment_content
                    }
                }
                
                # 手动序列化 JSON，确保中文不被转义
                json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
                
                response = requests.post(
                    url, 
                    data=json_data,
                    headers={'Content-Type': 'application/json; charset=utf-8'},
                    timeout=10
                )
                result = response.json()
                
                if result.get('errcode') == 0:
                    print(f"✅ 成功发送第 {i+1}/{len(segments)} 段消息给: {openid}")
                else:
                    print(f"❌ 发送第 {i+1}/{len(segments)} 段消息失败: {result}")
                    all_success = False
                    # 即使某一段失败，继续发送剩余段
                
                # 如果有多段，添加短暂延迟避免频率限制
                if len(segments) > 1 and i < len(segments) - 1:
                    time.sleep(0.5)
            
            if all_success:
                print(f"✅ 成功发送客服消息给: {openid}")
            else:
                print(f"⚠️ 部分消息发送失败，用户: {openid}")
            
            return all_success
                
        except Exception as e:
            print(f"发送客服消息异常: {e}")
            import traceback
            traceback.print_exc()
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
            # 处理文本消息
            if msg.type == 'text':
                user_message = msg.content.strip()
                print(f"收到用户 {user_id} 的消息: {user_message}")
                
                # ✅ 优先检查是否是系统命令
                if command_service and command_service.is_system_command(user_message):
                    print(f"检测到系统命令: {user_message}")
                    
                    # 检查是否是会清除历史的命令（cls、reset等）
                    command_lower = user_message.strip().lower()
                    is_clear_command = command_lower in ['cls', 'reset', '重置']
                    
                    # 对于非清除历史的命令，先保存用户消息
                    if not is_clear_command:
                        self.conversation_service.add_message(
                            user_id=user_id,
                            role='user',
                            content=user_message
                        )
                    
                    # 执行系统命令
                    reply_content = command_service.execute_command(user_message, user_id)
                    
                    # 对于非清除历史的命令，保存回复到对话历史
                    # 移除 [sys] 标记后再保存，让对话更自然
                    if not is_clear_command and reply_content:
                        # 去除 [sys] 标记（如果有）
                        clean_reply = reply_content.replace('[sys] ', '').strip()
                        self.conversation_service.add_message(
                            user_id=user_id,
                            role='assistant',
                            content=clean_reply
                        )
                    
                    return reply_content
                
                # 检查是否有图片会话
                if self.image_session_service and self.image_session_service.has_active_session(user_id):
                    print(f"用户 {user_id} 有活跃的图片会话，将图片和文本一起发送给AI")
                    
                    # 获取图片路径列表
                    image_paths = self.image_session_service.get_session_images(user_id)
                    print(f"获取到 {len(image_paths)} 张图片: {image_paths}")
                    
                    # 保存用户消息到对话历史（包含图片提示）
                    user_message_with_context = f"[附带{len(image_paths)}张图片] {user_message}"
                    self.conversation_service.add_message(
                        user_id=user_id,
                        role='user',
                        content=user_message_with_context
                    )
                    
                    # 调用大模型处理图片和文本
                    reply_content = llm_service.chat_with_images(
                        user_id=user_id,
                        user_message=user_message,
                        image_paths=image_paths
                    )
                    
                    # 清理Markdown格式
                    reply_content = self.clean_markdown(reply_content)
                    
                    # 保存助手回复到对话历史
                    self.conversation_service.add_message(
                        user_id=user_id,
                        role='assistant',
                        content=reply_content
                    )
                    
                    # 清空图片会话（这次图片处理完成）
                    self.image_session_service.clear_session(user_id)
                    
                    return reply_content
                else:
                    # 正常的文本对话流程
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
                    
                    # 清理Markdown格式，使其更适合微信显示
                    reply_content = self.clean_markdown(reply_content)
                    
                    # 保存助手回复到对话历史
                    self.conversation_service.add_message(
                        user_id=user_id,
                        role='assistant',
                        content=reply_content
                    )
                    
                    return reply_content
            
            # 处理图片消息
            elif msg.type == 'image':
                print(f"收到用户 {user_id} 的图片消息，MediaId: {msg.media_id}")
                
                if not self.image_session_service:
                    return "抱歉，图片处理功能暂时不可用。"
                
                # 获取AccessToken
                access_token = self.get_access_token()
                if not access_token:
                    return "抱歉，无法获取图片，请稍后重试。"
                
                # 下载图片
                image_path = self.image_session_service.download_image_from_wechat(
                    access_token=access_token,
                    media_id=msg.media_id,
                    user_id=user_id
                )
                
                if not image_path:
                    return "抱歉，图片下载失败，请重新发送。"
                
                # 添加图片到会话
                image_count = self.image_session_service.add_image(user_id, image_path)
                
                # 回复用户
                return f"已接收到图片（共{image_count}张），是否继续发送图片还是根据图片提问？"
            
            # 处理事件消息
            elif msg.type == 'event':
                if msg.event == 'subscribe':
                    return '欢迎关注在办小助手！\n\n我可以帮你管理待办事项，你可以：\n• 直接告诉我要做什么，我会帮你记录\n• 说"查看待办"来查看任务列表\n• 说"完成XX"来标记任务完成\n• 发送图片给我，我可以帮你分析图片内容\n• 每天早上9点我会给你发送任务规划\n\n快来试试吧！'
                elif msg.event == 'unsubscribe':
                    print(f"用户取消关注: {msg.source}")
                    # 清空用户的对话历史
                    self.conversation_service.clear_user_history(user_id)
                    # 清空图片会话
                    if self.image_session_service:
                        self.image_session_service.clear_session(user_id)
                    return "success"
                else:
                    return "收到您的消息"
            
            else:
                return "抱歉，我暂时只能处理文字和图片消息哦~"
                
        except Exception as e:
            print(f"处理消息异常: {e}")
            import traceback
            traceback.print_exc()
            return "抱歉，处理消息时出现了问题"

