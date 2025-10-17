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
    SECRET_KEY = 'your-secret-key-change-this-in-production'
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 8000
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 微信服务号配置
    WECHAT_TOKEN = 'aVerySecureTokenFor7FloorTop'
    WECHAT_AES_KEY = 'cLQerPqwrZ8ry2Maxf3AfqmTZSVh98mT7xpbDQYC7lH'
    WECHAT_APP_ID = 'wx53180dce891e9e7c'
    WECHAT_APP_SECRET = 'your_wechat_app_secret_here'
    
    # ==================== 大模型配置 ====================
    # 支持多种大模型API (OpenAI兼容接口)
    
    # 可用的模型配置
    LLM_MODELS = {
        'deepseek': {
            'api_key': 'sk-ab5927c3a14543af94bdca454ba541aa',
            'api_base': 'https://api.deepseek.com',
            'model': 'deepseek-chat',
            'temperature': 0.3,
            'max_tokens': 1000
        },
        'gemini': {
            'api_key': 'sk-h0arJk5As1V9XtG776xbLluxo8TcsCGSydGnhtVRDrRGf7pk',
            'api_base': 'https://hiapi.online/v1',
            'model': 'gemini-2.5-pro-thinking',
            'temperature': 0.7,
            'max_tokens': 1000
        }
    }
    
    # 当前使用的模型 (修改这里来切换模型: 'deepseek' 或 'gemini')
    CURRENT_LLM = 'gemini'
    
    # 从选中的模型配置中加载参数
    LLM_API_KEY = LLM_MODELS[CURRENT_LLM]['api_key']
    LLM_API_BASE = LLM_MODELS[CURRENT_LLM]['api_base']
    LLM_MODEL = LLM_MODELS[CURRENT_LLM]['model']
    LLM_TEMPERATURE = LLM_MODELS[CURRENT_LLM]['temperature']
    LLM_MAX_TOKENS = LLM_MODELS[CURRENT_LLM]['max_tokens']
    
    # 定时任务配置
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'
    DAILY_REPORT_TIME = '09:00'  # 每天早上9点发送日报
    
    # 提示词配置文件路径
    PROMPTS_FILE = os.path.join(BASE_DIR, 'prompts', 'prompts.yml')
    
    # AccessToken缓存配置
    ACCESS_TOKEN_CACHE_TIME = 7000  # 秒，微信AccessToken有效期为7200秒
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = os.path.join(BASE_DIR, 'logs', 'app.log')


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

