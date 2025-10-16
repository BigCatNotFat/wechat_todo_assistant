# -*- coding: utf-8 -*-
"""
项目启动入口
"""
import os
from app import create_app

# 从环境变量获取配置名称，默认为development
config_name = os.environ.get('FLASK_ENV', 'development')

# 创建应用实例
app = create_app(config_name)

if __name__ == '__main__':
    # 获取运行参数
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8000))
    debug = app.config['DEBUG']
    
    print(f"\n{'='*60}")
    print(f"在办小助手服务器启动")
    print(f"运行环境: {config_name}")
    print(f"监听地址: http://{host}:{port}")
    print(f"调试模式: {'开启' if debug else '关闭'}")
    print(f"{'='*60}\n")
    
    # 启动Flask开发服务器
    # 生产环境建议使用Gunicorn等WSGI服务器
    app.run(host=host, port=port, debug=debug)

