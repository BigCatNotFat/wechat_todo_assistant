# -*- coding: utf-8 -*-
"""
测试 Gemini Google Search 功能
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import DevelopmentConfig
from app.utils.prompt_manager import PromptManager
from app.services.todo_service import TodoService
from app.services.llm_service import LLMService
from app.database.db import db
from flask import Flask


def create_test_app():
    """创建测试应用"""
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    db.init_app(app)
    return app


def test_google_search():
    """测试 Google Search 功能"""
    print("=" * 60)
    print("测试 Gemini Google Search 功能")
    print("=" * 60)
    
    # 创建应用上下文
    app = create_test_app()
    
    with app.app_context():
        # 初始化服务
        config = DevelopmentConfig.__dict__
        prompt_manager = PromptManager(config['PROMPTS_FILE'])
        todo_service = TodoService()
        llm_service = LLMService(config, prompt_manager, todo_service)
        
        # 检查配置
        print(f"\n当前模型: {config['CURRENT_LLM']}")
        print(f"使用 Genai SDK: {llm_service.use_genai_sdk}")
        print(f"启用 Google Search: {llm_service.use_google_search}")
        
        if not llm_service.use_google_search:
            print("\n⚠️  警告: Google Search 未启用")
            print("请在 config.py 中设置 CURRENT_LLM = 'geminiofficial'")
            return
        
        # 测试问题列表
        test_questions = [
            "2024年欧洲杯冠军是哪个国家？",
            "最新的 Python 版本是什么？",
            "今天是几月几号？"
        ]
        
        print("\n" + "=" * 60)
        print("开始测试问题")
        print("=" * 60)
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n【问题 {i}】: {question}")
            print("-" * 60)
            
            try:
                response = llm_service.chat_with_function_calling(
                    user_id=1,
                    user_message=question
                )
                
                print(f"\n【回答】:\n{response}")
                print("\n" + "=" * 60)
                
            except Exception as e:
                print(f"\n❌ 错误: {e}")
                import traceback
                traceback.print_exc()
                print("=" * 60)
        
        print("\n✅ 测试完成！")


def test_model_comparison():
    """对比不同模型的响应（带/不带 Google Search）"""
    print("=" * 60)
    print("对比测试：Google Search vs 普通模式")
    print("=" * 60)
    
    app = create_test_app()
    
    with app.app_context():
        prompt_manager = PromptManager(DevelopmentConfig.PROMPTS_FILE)
        todo_service = TodoService()
        
        test_question = "2024年诺贝尔物理学奖获得者是谁？"
        
        # 测试不同模型
        models_to_test = ['deepseek', 'geminiofficial']
        
        for model_name in models_to_test:
            print(f"\n{'=' * 60}")
            print(f"测试模型: {model_name}")
            print(f"{'=' * 60}")
            
            # 创建临时配置
            config = DevelopmentConfig.__dict__.copy()
            config['CURRENT_LLM'] = model_name
            
            # 重新加载配置
            llm_config = config['LLM_MODELS'][model_name]
            config['LLM_API_KEY'] = llm_config['api_key']
            config['LLM_API_BASE'] = llm_config['api_base']
            config['LLM_MODEL'] = llm_config['model']
            config['LLM_TEMPERATURE'] = llm_config['temperature']
            config['LLM_MAX_TOKENS'] = llm_config['max_tokens']
            
            try:
                llm_service = LLMService(config, prompt_manager, todo_service)
                
                print(f"\n问题: {test_question}\n")
                
                response = llm_service.chat_with_function_calling(
                    user_id=1,
                    user_message=test_question
                )
                
                print(f"\n回答:\n{response}")
                
            except Exception as e:
                print(f"\n❌ 错误: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'=' * 60}")
        print("对比测试完成！")
        print(f"{'=' * 60}")


if __name__ == '__main__':
    print("\n请选择测试模式：")
    print("1. 基础测试（仅 Google Search）")
    print("2. 对比测试（多模型对比）")
    
    choice = input("\n请输入选项 (1 或 2): ").strip()
    
    if choice == '1':
        test_google_search()
    elif choice == '2':
        test_model_comparison()
    else:
        print("无效选项，执行基础测试...")
        test_google_search()

