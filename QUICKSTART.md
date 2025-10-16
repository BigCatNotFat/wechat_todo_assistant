# 快速开始指南

5分钟内启动你的在办小助手！

## 第一步：克隆或下载项目

```bash
# 如果是Git仓库
git clone <repository-url>
cd wechat_todo_assistant

# 如果是压缩包，解压后进入目录
cd wechat_todo_assistant
```

## 第二步：安装依赖

### Windows

双击运行 `start.bat`，它会自动：
1. 创建虚拟环境
2. 安装依赖
3. 检查配置

或手动执行：
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Linux/Mac

运行 `start.sh`：
```bash
chmod +x start.sh
./start.sh
```

或手动执行：
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 第三步：配置环境变量

```bash
# 复制示例配置文件
cp env.example .env

# 编辑配置文件
nano .env  # 或使用你喜欢的编辑器
```

**必须配置的项**：

```env
# 微信服务号配置
WECHAT_APP_ID=wx53180dce891e9e7c          # 你的AppID
WECHAT_APP_SECRET=your_app_secret_here    # 你的AppSecret
WECHAT_TOKEN=aVerySecureTokenFor7FloorTop # 自定义Token
WECHAT_AES_KEY=cLQerPqwrZ8ry2Maxf3AfqmTZSVh98mT7xpbDQYC7lH  # 自定义AES Key

# 大模型配置（以OpenAI为例）
LLM_API_KEY=sk-xxxxxxxxxxxxxxxx           # 你的API Key
LLM_API_BASE=https://api.openai.com/v1   # API地址
LLM_MODEL=gpt-3.5-turbo                   # 模型名称
```

### 如何获取微信配置？

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入「开发 - 基本配置」
3. 获取 AppID 和 AppSecret
4. 自定义 Token（3-32位字符）
5. 随机生成 EncodingAESKey（或自定义43位字符）

### 如何获取大模型API Key？

**OpenAI**:
1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册账号并充值
3. 在 API Keys 页面创建新密钥

**智谱GLM**:
1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册并实名认证
3. 创建API Key

**通义千问**:
1. 访问 [阿里云百炼](https://bailian.console.aliyun.com/)
2. 开通服务
3. 获取API Key

## 第四步：测试配置

```bash
python test_setup.py
```

如果所有测试通过，继续下一步。

## 第五步：启动服务

```bash
python run.py
```

看到以下信息表示启动成功：

```
============================================================
在办小助手服务器启动
运行环境: development
监听地址: http://0.0.0.0:8000
调试模式: 开启
============================================================

定时任务调度器已启动，时区: Asia/Shanghai
已添加每日任务 [daily_plan_push]，执行时间: 09:00
数据库初始化完成

注册的路由:
  wechat.wechat_handler: /zaiban [GET, HEAD, OPTIONS, POST]

应用启动完成 (配置: development)
```

## 第六步：配置微信服务号

### 本地测试（需要内网穿透）

使用 ngrok 或其他内网穿透工具：

```bash
# 使用ngrok
ngrok http 8000

# 会得到一个公网地址，如：https://abc123.ngrok.io
```

### 配置服务器地址

1. 登录微信公众平台
2. 进入「开发 - 基本配置 - 服务器配置」
3. 填写：
   - **URL**: `http://your-domain.com/zaiban` (或ngrok地址)
   - **Token**: 与`.env`中的`WECHAT_TOKEN`完全一致
   - **EncodingAESKey**: 与`.env`中的`WECHAT_AES_KEY`完全一致
   - **消息加解密方式**: 选择「安全模式」✅
   - **数据格式**: 选择「XML」✅

4. 点击「提交」，微信会发送验证请求

### 验证成功标志

看到服务器日志：
```
GET请求签名验证成功
```

微信后台显示「配置成功」。

## 第七步：测试功能

### 扫码关注服务号

使用微信扫码关注你的测试服务号。

### 发送测试消息

**测试1: 添加待办**
```
用户: 明天下午3点开会
助手: ✅ 已添加待办：明天下午3点开会
```

**测试2: 查看待办**
```
用户: 查看待办
助手: 📋 您有1个待办事项：...
```

**测试3: 完成任务**
```
用户: 完成任务1
助手: 🎉 太棒了！已完成：明天下午3点开会
```

## 常见问题速查

### ❌ 问题: 启动时提示缺少模块

**解决**:
```bash
pip install -r requirements.txt
```

### ❌ 问题: 微信验证失败

**检查清单**:
- [ ] Token是否完全一致（区分大小写）
- [ ] 服务器是否正在运行
- [ ] URL是否正确（不要忘记 `/zaiban`）
- [ ] 服务器是否可以从公网访问

**查看日志**:
```bash
# 查看服务器日志
tail -f logs/app.log
```

### ❌ 问题: 消息解密失败

**检查清单**:
- [ ] EncodingAESKey是否正确（43位）
- [ ] AppID是否正确
- [ ] 消息加解密方式是否选择"安全模式"

### ❌ 问题: 大模型不回复

**检查清单**:
- [ ] API Key是否有效
- [ ] API Base URL是否正确
- [ ] 模型名称是否正确
- [ ] 账户余额是否充足

**查看日志**:
```python
# 日志中会显示大模型调用信息
```

### ❌ 问题: 端口被占用

**解决**:
```bash
# 修改端口
# 编辑 .env 文件
PORT=8001

# 或使用环境变量
PORT=8001 python run.py
```

## 下一步

✅ 基础功能已经可以使用了！

**进一步学习**:
- 📖 阅读 [使用指南](USAGE.md) 了解更多功能
- 🚀 阅读 [部署指南](DEPLOY.md) 部署到生产环境
- 🔧 阅读 [FAQ](FAQ.md) 解决常见问题
- 📐 阅读 [项目结构](PROJECT_STRUCTURE.md) 了解代码架构

**自定义配置**:
- 修改 `prompts/prompts.yml` 自定义AI回复
- 修改 `config.py` 调整系统参数
- 修改 `DAILY_REPORT_TIME` 调整推送时间

**贡献代码**:
- Fork项目
- 提交Pull Request
- 报告Bug或建议

---

🎉 恭喜！你已经成功启动在办小助手！

有问题？查看 [FAQ](FAQ.md) 或提Issue。

