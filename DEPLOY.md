# 部署指南

本文档介绍如何在生产环境部署在办小助手。

## 准备工作

### 1. 服务器要求

- 操作系统: Linux (Ubuntu 20.04+ 推荐)
- Python: 3.8+
- 内存: 至少 1GB
- 带宽: 公网IP，支持80/443端口

### 2. 域名和SSL证书

- 准备一个域名
- 配置SSL证书 (推荐使用Let's Encrypt)

## 部署方式

### 方式一：传统部署 (Gunicorn + Nginx)

#### 1. 安装依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和相关工具
sudo apt install python3 python3-pip python3-venv nginx -y

# 安装Supervisor（进程管理）
sudo apt install supervisor -y
```

#### 2. 部署代码

```bash
# 克隆或上传代码到服务器
cd /var/www/
sudo mkdir wechat_todo_assistant
sudo chown $USER:$USER wechat_todo_assistant
cd wechat_todo_assistant

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install gunicorn
```

#### 3. 配置环境变量

```bash
# 复制并编辑.env文件
cp env.example .env
nano .env

# 填写真实配置
# - 微信服务号的AppID、AppSecret、Token、AES Key
# - 大模型的API Key
# - 其他配置
```

#### 4. 测试运行

```bash
# 测试配置
python test_setup.py

# 手动启动测试
gunicorn -w 4 -b 127.0.0.1:8000 run:app
```

#### 5. 配置Supervisor

创建 `/etc/supervisor/conf.d/wechat_todo.conf`:

```ini
[program:wechat_todo]
directory=/var/www/wechat_todo_assistant
command=/var/www/wechat_todo_assistant/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 --timeout 120 run:app
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/wechat_todo.err.log
stdout_logfile=/var/log/wechat_todo.out.log
environment=FLASK_ENV=production
```

启动服务:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start wechat_todo
sudo supervisorctl status
```

#### 6. 配置Nginx

创建 `/etc/nginx/sites-available/wechat_todo`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 日志
    access_log /var/log/nginx/wechat_todo.access.log;
    error_log /var/log/nginx/wechat_todo.error.log;

    # 微信接口
    location /zaiban {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

启用站点:

```bash
sudo ln -s /etc/nginx/sites-available/wechat_todo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 7. 配置SSL (可选但推荐)

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 方式二：Docker部署

#### 1. 安装Docker

```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo apt install docker-compose -y
```

#### 2. 配置环境

```bash
# 编辑.env文件
cp env.example .env
nano .env
```

#### 3. 构建并启动

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看状态
docker-compose ps
```

#### 4. Nginx反向代理

同上配置Nginx，代理到Docker容器的8000端口。

## 微信服务号配置

### 1. 配置服务器地址

1. 登录微信公众平台
2. 进入「开发 - 基本配置」
3. 填写服务器配置：
   - URL: `http://your-domain.com/zaiban` (或 `https://`)
   - Token: 与`.env`中一致
   - EncodingAESKey: 与`.env`中一致
   - 消息加解密方式: **安全模式**
   - 数据格式: **XML**

### 2. 白名单配置

在「基本配置 - IP白名单」中添加服务器IP。

### 3. 测试

使用微信开发者工具或公众平台的「接口调试工具」测试：
- 验证URL
- 发送测试消息

## 监控和维护

### 查看日志

```bash
# Supervisor日志
sudo tail -f /var/log/wechat_todo.err.log
sudo tail -f /var/log/wechat_todo.out.log

# Nginx日志
sudo tail -f /var/log/nginx/wechat_todo.access.log
sudo tail -f /var/log/nginx/wechat_todo.error.log

# Docker日志
docker-compose logs -f
```

### 重启服务

```bash
# Supervisor方式
sudo supervisorctl restart wechat_todo

# Docker方式
docker-compose restart
```

### 更新代码

```bash
# 传统部署
cd /var/www/wechat_todo_assistant
git pull  # 或手动上传
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart wechat_todo

# Docker部署
docker-compose down
git pull
docker-compose build
docker-compose up -d
```

### 数据库备份

```bash
# 定期备份数据库
cp instance/app.db backups/app_$(date +%Y%m%d).db

# 设置定时备份 (crontab)
0 2 * * * /path/to/backup_script.sh
```

## 性能优化

### 1. Gunicorn配置

根据服务器配置调整worker数量：
```bash
# CPU核心数 * 2 + 1
gunicorn -w 9 -b 127.0.0.1:8000 run:app
```

### 2. 数据库优化

生产环境建议使用PostgreSQL或MySQL：

```python
# config.py
SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@localhost/dbname'
```

### 3. 缓存

考虑使用Redis缓存：
- AccessToken
- 用户会话
- 频繁查询的数据

## 故障排查

### 问题1: 微信服务器无法访问

- 检查防火墙: `sudo ufw allow 80/443`
- 检查Nginx状态: `sudo systemctl status nginx`
- 检查应用状态: `sudo supervisorctl status`

### 问题2: 消息解密失败

- 确认Token、AES Key配置正确
- 检查消息加解密模式为"安全模式"
- 查看错误日志

### 问题3: 定时任务不执行

- 检查服务器时区设置
- 查看应用日志
- 确认APScheduler正常启动

## 安全建议

1. **环境变量**: 不要在代码中硬编码密钥
2. **HTTPS**: 生产环境必须使用HTTPS
3. **防火墙**: 只开放必要端口
4. **日志**: 定期清理，避免敏感信息泄露
5. **更新**: 定期更新依赖包
6. **备份**: 定期备份数据库和配置

## 扩展性

当用户量增长时：

1. **负载均衡**: 使用多台服务器 + Nginx负载均衡
2. **数据库**: 使用PostgreSQL + 读写分离
3. **消息队列**: 使用Celery处理异步任务
4. **缓存**: Redis缓存热点数据
5. **监控**: Prometheus + Grafana

---

如有问题，请查看[README.md](README.md)或提Issue。

