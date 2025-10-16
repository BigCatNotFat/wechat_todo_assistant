# -*- coding: utf-8 -*-
"""
SQLAlchemy实例
解决循环导入问题，提供全局db对象
"""
from flask_sqlalchemy import SQLAlchemy

# 创建SQLAlchemy实例
db = SQLAlchemy()

