# -*- coding: utf-8 -*-
"""
微信蓝图包初始化
"""
from flask import Blueprint

# 创建微信蓝图
wechat_bp = Blueprint('wechat', __name__, url_prefix='')

# 导入路由（放在最后避免循环导入）
from app.wechat import routes

