# -*- coding: utf-8 -*-
"""
测试脚本 - 验证项目配置是否正确
"""
import os
import sys


def test_imports():
    """测试必要的包是否能正常导入"""
    print("测试导入...")
    try:
        import flask
        print("✓ Flask")
        
        import wechatpy
        print("✓ wechatpy")
        
        import openai
        print("✓ openai")
        
        import yaml
        print("✓ PyYAML")
        
        from apscheduler.schedulers.background import BackgroundScheduler
        print("✓ APScheduler")
        
        from flask_sqlalchemy import SQLAlchemy
        print("✓ Flask-SQLAlchemy")
        
        print("\n所有依赖导入成功！")
        return True
    except ImportError as e:
        print(f"\n✗ 导入失败: {e}")
        print("请运行: pip install -r requirements.txt")
        return False


def test_config():
    """测试配置文件"""
    print("\n测试配置...")
    try:
        from config import config
        dev_config = config['development']
        print(f"✓ 配置文件加载成功")
        print(f"  - 数据库: {dev_config.SQLALCHEMY_DATABASE_URI}")
        print(f"  - 微信AppID: {dev_config.WECHAT_APP_ID}")
        print(f"  - 大模型: {dev_config.LLM_MODEL}")
        return True
    except Exception as e:
        print(f"✗ 配置文件测试失败: {e}")
        return False


def test_app_creation():
    """测试应用创建"""
    print("\n测试应用创建...")
    try:
        from app import create_app
        app = create_app('development')
        print("✓ Flask应用创建成功")
        
        with app.app_context():
            from app.database.db import db
            print("✓ 数据库初始化成功")
            
            from app.models import User, TodoItem
            print("✓ 模型加载成功")
        
        return True
    except Exception as e:
        print(f"✗ 应用创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prompts():
    """测试提示词文件"""
    print("\n测试提示词...")
    try:
        if os.path.exists('prompts/prompts.yml'):
            print("✓ 提示词文件存在")
            
            import yaml
            with open('prompts/prompts.yml', 'r', encoding='utf-8') as f:
                prompts = yaml.safe_load(f)
            
            required_prompts = ['system_prompt', 'daily_planning_prompt']
            for prompt_key in required_prompts:
                if prompt_key in prompts:
                    print(f"✓ {prompt_key}")
                else:
                    print(f"✗ 缺少 {prompt_key}")
            
            return True
        else:
            print("✗ 提示词文件不存在")
            return False
    except Exception as e:
        print(f"✗ 提示词测试失败: {e}")
        return False


def test_directory_structure():
    """测试目录结构"""
    print("\n测试目录结构...")
    required_dirs = [
        'app',
        'app/database',
        'app/models',
        'app/services',
        'app/utils',
        'app/wechat',
        'prompts'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✓ {dir_path}")
        else:
            print(f"✗ {dir_path} 不存在")
            all_exist = False
    
    return all_exist


def main():
    """主测试函数"""
    print("="*60)
    print("在办小助手 - 项目配置测试")
    print("="*60)
    
    tests = [
        ("目录结构", test_directory_structure),
        ("依赖导入", test_imports),
        ("配置文件", test_config),
        ("提示词文件", test_prompts),
        ("应用创建", test_app_creation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name}测试异常: {e}")
            results.append((name, False))
    
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 所有测试通过！项目配置正确。")
        print("可以运行 python run.py 启动服务器。")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查配置。")
        return 1


if __name__ == '__main__':
    sys.exit(main())

