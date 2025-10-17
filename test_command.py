# -*- coding: utf-8 -*-
"""
测试系统命令功能
独立测试命令服务的各项功能
"""
from app import create_app
from app.services.command_service import CommandService
from app.services.conversation_service import ConversationService
from app.services.todo_service import TodoService


def test_commands():
    """测试系统命令功能"""
    print("=" * 60)
    print("系统命令功能测试")
    print("=" * 60)
    
    # 创建应用上下文
    app = create_app('development')
    
    with app.app_context():
        # 获取服务实例
        command_service = app.command_service
        todo_service = app.todo_service
        conversation_service = app.wechat_service.conversation_service
        
        # 创建测试用户
        test_user = todo_service.get_or_create_user("test_openid_123", "测试用户")
        user_id = test_user.id
        
        print(f"\n✅ 测试用户已创建: ID={user_id}")
        
        # 添加一些测试数据
        print("\n📝 准备测试数据...")
        
        # 添加对话历史
        conversation_service.add_message(user_id, "user", "你好")
        conversation_service.add_message(user_id, "assistant", "你好！有什么可以帮你的？")
        conversation_service.add_message(user_id, "user", "明天开会")
        conversation_service.add_message(user_id, "assistant", "好的，已帮你记录")
        
        # 添加待办事项
        todo_service.create_todo(user_id, "明天开会", "重要会议")
        todo_service.create_todo(user_id, "写报告", "本周五前完成")
        todo_service.create_todo(user_id, "买菜", None)
        
        print("   - 添加了 4 条对话记录")
        print("   - 添加了 3 个待办事项")
        
        # 测试各个命令
        print("\n" + "=" * 60)
        print("开始测试各个系统命令")
        print("=" * 60)
        
        # 1. 测试 help 命令
        print("\n【测试1】help 命令")
        print("-" * 60)
        result = command_service.execute_command("help", user_id)
        print(result)
        
        # 2. 测试 stats 命令
        print("\n【测试2】stats 命令")
        print("-" * 60)
        result = command_service.execute_command("stats", user_id)
        print(result)
        
        # 3. 测试中文命令 统计
        print("\n【测试3】统计 命令（中文）")
        print("-" * 60)
        result = command_service.execute_command("统计", user_id)
        print(result)
        
        # 4. 测试 clear 命令
        print("\n【测试4】clear 命令")
        print("-" * 60)
        result = command_service.execute_command("clear", user_id)
        print(result)
        
        # 5. 验证清除效果
        print("\n【验证】检查对话历史是否已清空")
        print("-" * 60)
        history = conversation_service.get_recent_history(user_id)
        print(f"剩余对话历史: {len(history)} 条")
        
        # 6. 测试命令检测
        print("\n【测试5】is_system_command 检测")
        print("-" * 60)
        test_messages = ["help", "HELP", "  help  ", "帮助", "clear", "你好", "查看待办"]
        for msg in test_messages:
            is_cmd = command_service.is_system_command(msg)
            print(f"   '{msg}' -> {is_cmd}")
        
        # 7. 测试 reset 命令
        print("\n【测试6】reset 命令（慎用）")
        print("-" * 60)
        # 先添加一些数据
        conversation_service.add_message(user_id, "user", "测试消息")
        result = command_service.execute_command("reset", user_id)
        print(result)
        
        # 8. 验证重置效果
        print("\n【验证】检查数据是否已重置")
        print("-" * 60)
        history = conversation_service.get_recent_history(user_id)
        todos = todo_service.get_user_todos(user_id)
        print(f"剩余对话历史: {len(history)} 条")
        print(f"剩余待办事项: {len(todos)} 个")
        
        # 9. 获取所有命令列表
        print("\n【测试7】获取所有支持的命令")
        print("-" * 60)
        all_commands = command_service.get_all_commands()
        print(f"支持的命令: {', '.join(all_commands)}")
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)


if __name__ == '__main__':
    test_commands()

