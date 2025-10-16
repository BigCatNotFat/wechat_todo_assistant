#!/bin/bash
# 启动脚本 (Linux/Mac)

echo "在办小助手服务器启动脚本"
echo "=============================="

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装/更新依赖..."
pip install -r requirements.txt

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "警告: .env文件不存在，请复制env.example为.env并配置"
    exit 1
fi

# 启动服务
echo "启动服务..."
python run.py

