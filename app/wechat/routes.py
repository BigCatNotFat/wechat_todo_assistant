# -*- coding: utf-8 -*-
"""
微信路由
处理微信服务器的请求
"""
from flask import request, current_app, abort
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException, InvalidAppIdException
from wechatpy.crypto import WeChatCrypto
from app.wechat import wechat_bp


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
        
        # 创建加解密工具
        crypto = WeChatCrypto(token, aes_key, app_id)
        
        try:
            # 解密消息
            decrypted_xml = crypto.decrypt_message(
                request.data,
                msg_signature,
                timestamp,
                nonce
            )
            
            print(f"收到消息: {decrypted_xml[:200]}")  # 打印前200字符
            
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
                
                # 处理消息并获取回复（传入命令服务）
                reply_content = wechat_service.handle_message(msg, llm_service, user.id, command_service)
                
                # 创建回复
                if reply_content and reply_content != "success":
                    reply_xml = wechat_service.create_text_reply(reply_content, msg)
                    
                    # 加密回复
                    encrypted_xml = crypto.encrypt_message(
                        reply_xml,
                        nonce,
                        timestamp
                    )
                    return encrypted_xml
                else:
                    return "success"
            else:
                return "success"
                
        except (InvalidSignatureException, InvalidAppIdException) as e:
            print(f"消息解密或签名验证失败: {e}")
            abort(403)
        except Exception as e:
            print(f"处理消息异常: {e}")
            import traceback
            traceback.print_exc()
            return "success"
    
    return "success"

