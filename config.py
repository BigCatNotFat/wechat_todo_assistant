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
            'max_tokens': 8192,
            'use_google_search': False,  # 不支持Google搜索
            'use_genai_sdk': False  # 使用OpenAI SDK
        },
        'geminihiapi': {
            'api_key': 'sk-h0arJk5As1V9XtG776xbLluxo8TcsCGSydGnhtVRDrRGf7pk',
            'api_base': 'https://hiapi.online/v1',
            'model': 'gemini-2.5-pro-thinking',
            'temperature': 0.7,
            'max_tokens': 8192,
            'use_google_search': False,  # 第三方API不支持Google搜索
            'use_genai_sdk': False  # 使用OpenAI SDK
        },
        'geminiofficial-flash': {
            'api_key': 'AIzaSyAX4_vnrJvGsHKmrRlYqJfaTa15ZwoVFE4',
            'api_base': 'https://generativelanguage.googleapis.com/v1beta/openai/',
            'model': 'gemini-2.5-flash',
            'temperature': 0.7,
            'max_tokens': 8192,
            'use_google_search': True,  # 启用搜索功能（通过 Function Calling 方式调用独立的搜索模型）
            'use_genai_sdk': True,  # 使用Google Genai SDK
            'thinking_budget': -1,  # 动态思考（模型自动决定，推荐用于一般任务）
            'include_thoughts': False  # 不输出思考总结（更快的响应）
        },
        'geminiofficial-pro': {
            'api_key': 'AIzaSyAX4_vnrJvGsHKmrRlYqJfaTa15ZwoVFE4',
            'api_base': 'https://generativelanguage.googleapis.com/v1beta/openai/',
            'model': 'gemini-2.5-pro',
            'temperature': 0.7,
            'max_tokens': 8192,
            'use_google_search': True,  # 启用搜索功能（通过 Function Calling 方式调用独立的搜索模型）
            'use_genai_sdk': True,  # 使用Google Genai SDK
            'thinking_budget': -1,  # 动态思考（默认配置）
            'include_thoughts': True  # 出思考总结
        },
        'geminiofficial-promax': {
            'api_key': 'AIzaSyAX4_vnrJvGsHKmrRlYqJfaTa15ZwoVFE4',
            'api_base': 'https://generativelanguage.googleapis.com/v1beta/openai/',
            'model': 'gemini-2.5-pro',
            'temperature': 0.7,
            'max_tokens': 8192,
            'use_google_search': True,  # 启用搜索功能（通过 Function Calling 方式调用独立的搜索模型）
            'use_genai_sdk': True,  # 使用Google Genai SDK
            'thinking_budget': 32768,  # 思考预算（最大值，用于复杂推理任务）
            'include_thoughts': True  # 启用思考总结输出
        }
    }
    
    # 当前使用的模型 (修改这里来切换模型: 'deepseek' 或 'gemini')
    CURRENT_LLM = 'geminiofficial-flash'
    
    # ==================== 搜索模型配置 ====================
    # 当主模型开启 use_google_search 时，使用此配置进行网络搜索
    SEARCH_MODEL_CONFIG = {
        'api_key': 'AIzaSyAX4_vnrJvGsHKmrRlYqJfaTa15ZwoVFE4',
        'model': 'gemini-2.5-flash',  
        'temperature': 0.7
    }
    
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

