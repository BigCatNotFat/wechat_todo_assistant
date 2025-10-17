# -*- coding: utf-8 -*-
"""
应用工厂
创建和配置Flask应用实例
"""
import os
from flask import Flask
from config import config
from app.database.db import db
from app.utils.prompt_manager import PromptManager
from app.utils.scheduler import Scheduler
from app.services.todo_service import TodoService
from app.services.llm_service import LLMService
from app.services.wechat_service import WeChatService
from app.services.planning_service import PlanningService
from app.services.command_service import CommandService


def create_app(config_name='default'):
    """
    应用工厂函数
    
    Args:
        config_name: 配置名称，可选: development, production, default
        
    Returns:
        Flask应用实例
    """
    # 创建Flask应用
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 确保必要的目录存在
    ensure_directories(app)
    
    # 初始化数据库
    db.init_app(app)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        print("数据库初始化完成")
    
    # 初始化提示词管理器
    prompt_manager = PromptManager(app.config['PROMPTS_FILE'])
    app.prompt_manager = prompt_manager
    
    # 初始化服务层
    todo_service = TodoService()
    app.todo_service = todo_service
    
    wechat_service = WeChatService(app.config)
    app.wechat_service = wechat_service
    
    llm_service = LLMService(app.config, prompt_manager, todo_service)
    app.llm_service = llm_service
    
    # 初始化命令服务
    command_service = CommandService(
        conversation_service=wechat_service.conversation_service,
        todo_service=todo_service
    )
    app.command_service = command_service
    
    planning_service = PlanningService(todo_service, llm_service, wechat_service)
    app.planning_service = planning_service
    
    # 初始化定时任务调度器
    scheduler = Scheduler(app.config['SCHEDULER_TIMEZONE'])
    app.scheduler = scheduler
    
    # 添加每日任务推送定时任务
    scheduler.add_daily_job(
        func=daily_plan_job,
        time_str=app.config['DAILY_REPORT_TIME'],
        job_id='daily_plan_push',
        app=app
    )
    
    # 启动调度器
    scheduler.start()
    
    # 注册蓝图
    from app.wechat import wechat_bp
    app.register_blueprint(wechat_bp)
    
    # 注册错误处理
    register_error_handlers(app)
    
    # 打印路由信息
    print("\n注册的路由:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint}: {rule.rule} [{', '.join(rule.methods)}]")
    
    print(f"\n应用启动完成 (配置: {config_name})")
    
    return app


def ensure_directories(app):
    """确保必要的目录存在"""
    directories = [
        os.path.dirname(app.config['PROMPTS_FILE']),
        os.path.dirname(app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')),
        os.path.dirname(app.config.get('LOG_FILE', 'logs/app.log'))
    ]
    
    for directory in directories:
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"创建目录: {directory}")


def daily_plan_job(app):
    """
    每日任务推送定时任务
    
    Args:
        app: Flask应用实例
    """
    print(f"\n开始执行每日任务推送 - {app.config['DAILY_REPORT_TIME']}")
    
    with app.app_context():
        try:
            app.planning_service.send_daily_plan_to_all_users()
        except Exception as e:
            print(f"每日任务推送失败: {e}")
            import traceback
            traceback.print_exc()


def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(404)
    def not_found(error):
        return "Not Found", 404
    
    @app.errorhandler(500)
    def internal_error(error):
        print(f"内部错误: {error}")
        return "Internal Server Error", 500
    
    @app.errorhandler(403)
    def forbidden(error):
        print(f"禁止访问: {error}")
        return "Forbidden", 403

