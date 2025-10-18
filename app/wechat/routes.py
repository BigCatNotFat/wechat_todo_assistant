# -*- coding: utf-8 -*-
"""
微信路由
处理微信服务器的请求
"""
import threading
from flask import request, current_app, abort
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException, InvalidAppIdException
from wechatpy.crypto import WeChatCrypto
from app.wechat import wechat_bp
from collections import deque
from datetime import datetime, timedelta

# 消息去重：使用双端队列存储最近处理过的消息ID（MsgId）
# 格式: (msg_id, timestamp)
processed_messages = deque(maxlen=1000)  # 最多保留1000条记录
processing_lock = threading.Lock()  # 线程锁，确保并发安全


def is_message_processed(msg_id):
    """
    检查消息是否已经处理过（去重）
    
    Args:
        msg_id: 消息ID（MsgId）
        
    Returns:
        True: 已处理过（重复消息）
        False: 未处理过（新消息）
    """
    with processing_lock:
        # 清理5分钟前的旧记录
        cutoff_time = datetime.now() - timedelta(minutes=5)
        while processed_messages and processed_messages[0][1] < cutoff_time:
            processed_messages.popleft()
        
        # 检查是否已处理
        for processed_id, _ in processed_messages:
            if processed_id == msg_id:
                return True
        
        # 标记为已处理
        processed_messages.append((msg_id, datetime.now()))
        return False


def process_message(app, decrypted_xml, nonce, timestamp):
    """
    在后台线程中异步处理消息的函数
    """
    # Flask的后台线程需要应用上下文才能访问current_app等变量
    with app.app_context():
        try:
            # 获取服务实例
            wechat_service = current_app.wechat_service
            llm_service = current_app.llm_service
            todo_service = current_app.todo_service
            command_service = current_app.command_service

            # 解析消息
            msg = wechat_service.parse_message(decrypted_xml)

            if msg:
                # 消息去重：检查MsgId是否已处理过
                msg_id = getattr(msg, 'id', None)
                if msg_id and is_message_processed(msg_id):
                    print(f"⚠️ 检测到重复消息（MsgId: {msg_id}），跳过处理")
                    return
                
                # 获取或创建用户
                openid = msg.source
                user = todo_service.get_or_create_user(openid)

                # 处理消息并获取回复内容
                reply_content = wechat_service.handle_message(msg, llm_service, user.id, command_service)

                # 如果有回复内容，通过客服消息接口发送
                if reply_content and reply_content != "success":
                    print(f"准备向 {openid} 发送客服消息: {reply_content[:100]}...")
                    
                    # 调用客服消息接口发送回复
                    success = wechat_service.send_customer_message(openid, reply_content)
                    
                    if success:
                        print(f"✅ 成功发送回复给用户 {openid}")
                    else:
                        print(f"❌ 发送回复失败，用户: {openid}")


        except Exception as e:
            print(f"后台处理消息异常: {e}")
            import traceback
            traceback.print_exc()


@wechat_bp.route('/zaiban', methods=['GET', 'POST'])
def wechat_handler():
    """
    微信服务器接口
    处理验证和消息接收
    """
    # 获取配置
    config = current_app.config
    token = config['WECHAT_TOKEN']
    aes_key = config['WECHAT_AES_KEY']
    app_id = config['WECHAT_APP_ID']

    # 获取URL参数
    signature = request.args.get('signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')

    # GET请求：验证服务器
    if request.method == 'GET':
        echo_str = request.args.get('echostr', '')
        try:
            check_signature(token, signature, timestamp, nonce)
            print("GET请求签名验证成功")
            return echo_str
        except InvalidSignatureException:
            print("GET请求签名验证失败!")
            abort(403)

    # POST请求：处理消息
    elif request.method == 'POST':
        msg_signature = request.args.get('msg_signature', '')
        crypto = WeChatCrypto(token, aes_key, app_id)

        try:
            # 解密消息
            decrypted_xml = crypto.decrypt_message(
                request.data,
                msg_signature,
                timestamp,
                nonce
            )
            print(f"收到消息: {decrypted_xml[:200]}")

            # ================ 核心修改点 ================
            # 创建一个后台线程来处理耗时任务
            # 需要传递current_app._get_current_object()以在线程中正确使用app上下文
            thread = threading.Thread(
                target=process_message,
                args=(current_app._get_current_object(), decrypted_xml, nonce, timestamp)
            )
            thread.start() # 启动线程

            # 立即返回success，避免微信超时重试
            return "success"
            # ============================================

        except (InvalidSignatureException, InvalidAppIdException) as e:
            print(f"消息解密或签名验证失败: {e}")
            abort(403)
        except Exception as e:
            print(f"处理消息异常: {e}")
            import traceback
            traceback.print_exc()
            # 即使出现其他异常，也应立即返回success
            return "success"

    return "success"