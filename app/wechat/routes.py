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
                # 获取或创建用户
                openid = msg.source
                user = todo_service.get_or_create_user(openid)

                # 处理消息并获取回复内容
                reply_content = wechat_service.handle_message(msg, llm_service, user.id, command_service)

                # 如果有回复内容，通过客服消息接口发送
                if reply_content and reply_content != "success":
                    # 注意：这里不再是创建XML回复，而是调用客服接口主动发送消息
                    # 你需要在wechat_service中实现一个发送客服消息的方法
                    # 示例：wechat_service.send_text_message(openid, reply_content)
                    
                    # 为了演示，我们先打印出来
                    print(f"准备向 {openid} 发送客服消息: {reply_content}")
                    
                    # 假设你的wechat_service有一个client实例可以发送消息
                    # from wechatpy import WeChatClient
                    # client = WeChatClient(current_app.config['WECHAT_APP_ID'], current_app.config['WECHAT_APP_SECRET'])
                    # client.message.send_text(openid, reply_content)


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