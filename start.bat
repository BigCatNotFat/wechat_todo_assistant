@echo off
REM 启动脚本 (Windows)

echo 在办小助手服务器启动脚本
echo ==============================

REM 检查虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装/更新依赖...
pip install -r requirements.txt

REM 检查.env文件
if not exist ".env" (
    echo 警告: .env文件不存在，请复制env.example为.env并配置
    pause
    exit /b 1
)

REM 启动服务
echo 启动服务...
python run.py

pause

