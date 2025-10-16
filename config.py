# -*- coding: utf-8 -*-
"""
配置文件
存储所有配置信息，包括微信配置、数据库配置、大模型配置等
"""
import os

class Config:
    """基础配置"""
    # 项目根目录
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 微信服务号配置
    WECHAT_TOKEN = os.environ.get('WECHAT_TOKEN') or 'aVerySecureTokenFor7FloorTop'
    WECHAT_AES_KEY = os.environ.get('WECHAT_AES_KEY') or 'cLQerPqwrZ8ry2Maxf3AfqmTZSVh98mT7xpbDQYC7lH'
    WECHAT_APP_ID = os.environ.get('WECHAT_APP_ID') or 'wx53180dce891e9e7c'
    WECHAT_APP_SECRET = os.environ.get('WECHAT_APP_SECRET') or 'your_app_secret_here'
    
    # 大模型配置 (支持多种大模型API)
    # 这里以OpenAI兼容接口为例，可以对接OpenAI、智谱GLM、通义千问等
    LLM_API_KEY = os.environ.get('LLM_API_KEY') or 'your_llm_api_key_here'
    LLM_API_BASE = os.environ.get('LLM_API_BASE') or 'https://api.openai.com/v1'
    LLM_MODEL = os.environ.get('LLM_MODEL') or 'gpt-3.5-turbo'
    LLM_TEMPERATURE = float(os.environ.get('LLM_TEMPERATURE') or '0.7')
    LLM_MAX_TOKENS = int(os.environ.get('LLM_MAX_TOKENS') or '1000')
    
    # 定时任务配置
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'
    DAILY_REPORT_TIME = '09:00'  # 每天早上9点发送日报
    
    # 提示词配置文件路径
    PROMPTS_FILE = os.path.join(BASE_DIR, 'prompts', 'prompts.yml')
    
    # AccessToken缓存配置
    ACCESS_TOKEN_CACHE_TIME = 7000  # 秒，微信AccessToken有效期为7200秒
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.path.join(BASE_DIR, 'logs', 'app.log')


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    
    # 生产环境必须设置环境变量
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("生产环境必须设置SECRET_KEY环境变量")


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

