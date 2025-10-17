# -*- coding: utf-8 -*-
"""
命令行测试工具
用于本地测试待办助手的所有功能，无需微信接入
"""
import os
import sys
from app import create_app
from app.database.db import db
from app.models.user import User


class MockWeChatMessage:
    """模拟微信消息对象，用于测试"""
    
    def __init__(self, content, source, msg_type='text'):
        self.content = content
        self.source = source
        self.type = msg_type


def create_test_user():
    """创建或获取测试用户"""
    test_openid = "test_user_001"
    user = User.query.filter_by(openid=test_openid).first()
    if not user:
        user = User(openid=test_openid, nickname="测试用户")
        db.session.add(user)
        db.session.commit()
        print(f"✅ 创建测试用户: {user.nickname} (ID: {user.id})")
    return user


def print_banner():
    """打印欢迎横幅"""
    print("=" * 60)
    print("🤖 在办小助手 - 命令行测试工具")
    print("=" * 60)
    print("💡 提示：")
    print("  • 直接输入消息与助手对话")
    print("  • 支持系统命令：help、clear、stats、reset")
    print("  • 输入 'cls' 清屏，'exit' 或 'quit' 退出")
    print("=" * 60)
    print()


def main():
    """主函数"""
    # 创建应用
    print("正在初始化...")
    
    # 确保使用开发环境（避免生产环境配置检查）
    os.environ.setdefault('FLASK_ENV', 'development')
    
    app = create_app('development')
    
    with app.app_context():
        # 创建测试用户
        user = create_test_user()
        
        # 获取服务实例
        wechat_service = app.wechat_service
        llm_service = app.llm_service
        command_service = app.command_service
        
        print("✅ 服务已启动\n")
        
        # 显示欢迎信息
        os.system('cls' if os.name == 'nt' else 'clear')
        print_banner()
        
        while True:
            try:
                # 获取用户输入
                user_input = input("👤 您: ").strip()
                
                if not user_input:
                    continue
                
                # 处理测试工具专用命令
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 再见！")
                    break
                
                if user_input.lower() == 'cls':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print_banner()
                    continue
                

                
                try:
                    # 创建模拟的微信消息对象
                    mock_msg = MockWeChatMessage(
                        content=user_input,
                        source=user.openid,
                        msg_type='text'
                    )
                    
                    # 调用 wechat_service.handle_message 处理消息
                    reply = wechat_service.handle_message(
                        msg=mock_msg,
                        llm_service=llm_service,
                        user_id=user.id,
                        command_service=command_service
                    )
                    
                    print(reply)
                    print()
                    
                except Exception as e:
                    print(f"\n❌ 错误: {e}")
                    import traceback
                    traceback.print_exc()
                    print()
                
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except EOFError:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")
                import traceback
                traceback.print_exc()
                print()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

