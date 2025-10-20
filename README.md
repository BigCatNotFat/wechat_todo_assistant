# 在办小助手 - 微信待办事项管理服务器

一个基于Flask + 大模型的智能微信服务号后端，用于管理待办事项。

## 功能特性

✅ **智能待办管理**
- 自动识别用户意图，创建、查询、更新、完成、删除待办事项
- 支持优先级设置和截止日期
- 基于大模型的Function Calling自动调用相关函数

📊 **智能任务规划**
- 每天早上9点自动推送每日任务规划
- 结合昨日完成情况和今日任务，科学规划优先级
- 用户可随时请求重新规划

🖼️ **图片理解功能** 🆕
- 支持接收和分析图片（需使用Gemini模型）
- 可连续发送多张图片，一次性提问
- 支持图片说明、内容识别、视觉问答等场景
- 自动会话管理，不同对话间图片互不干扰

🤖 **大模型集成**
- 支持OpenAI、智谱GLM、通义千问等OpenAI兼容接口
- 支持Google Gemini（含图片理解和搜索功能）
- Function Calling实现智能函数调用
- 自然语言理解用户需求

🔒 **微信安全模式**
- 完整支持微信消息加解密
- 签名验证确保请求来源安全
- 使用wechatpy库处理微信协议

## 项目架构

```
/wechat_todo_assistant/
├── run.py                      # 项目启动入口
├── config.py                   # 配置文件
├── requirements.txt            # 项目依赖
│
├── /prompts/
│   └── prompts.yml            # 提示词配置
│
├── /instance/
│   └── app.db                 # SQLite数据库
│
└── /app/
    ├── __init__.py            # 应用工厂
    │
    ├── /wechat/               # 视图层：微信交互
    │   ├── __init__.py
    │   └── routes.py
    │
    ├── /services/             # 服务层：业务逻辑
    │   ├── llm_service.py     # 大模型服务
    │   ├── todo_service.py    # 待办事项服务
    │   ├── wechat_service.py  # 微信API服务
    │   ├── planning_service.py # 任务规划服务
    │   └── image_session_service.py # 图片会话管理服务
    │
    ├── /models/               # 模型层：数据结构
    │   ├── user.py            # 用户模型
    │   └── todo_item.py       # 待办事项模型
    │
    ├── /utils/                # 工具层
    │   ├── llm_tools.py       # Function Calling工具
    │   ├── scheduler.py       # 定时任务调度
    │   └── prompt_manager.py  # 提示词管理
    │
    └── /database/             # 数据库配置
        └── db.py              # SQLAlchemy实例
```

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写：
- 微信服务号的 `WECHAT_APP_ID`, `WECHAT_APP_SECRET`, `WECHAT_TOKEN`, `WECHAT_AES_KEY`
- 大模型的 `LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL`

### 3. 配置微信服务号

1. 登录[微信开发者平台](https://mp.weixin.qq.com/)
2. 进入「开发 - 基本配置 - 服务器配置」
3. 填写：
   - **URL**: `http://your-domain.com/zaiban`
   - **Token**: 与`.env`中的`WECHAT_TOKEN`一致
   - **EncodingAESKey**: 与`.env`中的`WECHAT_AES_KEY`一致
   - **消息加解密方式**: 选择「安全模式」
   - **数据格式**: 选择「XML」

### 4. 启动服务

```bash
python run.py
```

服务将在 `http://0.0.0.0:8000` 启动。

### 5. 使用Nginx反向代理（生产环境）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /zaiban {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 使用说明

### 用户交互示例

1. **添加待办**
   - 用户："明天下午3点要开会"
   - 助手：自动创建待办事项

2. **查看待办**
   - 用户："查看我的任务"
   - 助手：列出所有待办事项

3. **完成任务**
   - 用户："完成任务1"
   - 助手：标记任务为已完成

4. **每日规划**
   - 每天早上9点自动推送
   - 或用户主动说："帮我规划今天的任务"

5. **图片理解** 🆕
   - 用户：发送一张图片
   - 助手："已接收到图片（共1张），是否继续发送图片还是根据图片提问？"
   - 用户："这是什么？"
   - 助手：分析图片并返回详细说明
   
   详细说明请查看：[图片处理功能说明.md](图片处理功能说明.md)

## 大模型配置

### 使用OpenAI

```env
LLM_API_KEY=sk-xxx
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
```

### 使用智谱GLM

```env
LLM_API_KEY=your-zhipu-api-key
LLM_API_BASE=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-4
```

### 使用通义千问

```env
LLM_API_KEY=your-qwen-api-key
LLM_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus
```

### 使用Google Gemini（支持图片理解）

在 `config.py` 中设置：

```python
CURRENT_LLM = 'geminiofficial-flash'  # 或 'geminiofficial-pro'
```

Gemini 模型特性：
- ✅ 支持图片理解
- ✅ 支持网络搜索
- ✅ 思考模式（Thinking）
- ✅ Function Calling

## 定时任务

系统使用APScheduler实现定时任务：

- **每日推送**: 每天早上9点（可在`config.py`中修改`DAILY_REPORT_TIME`）
- **任务内容**: 昨日总结 + 今日任务规划

## 数据库

使用SQLite（开发环境）或PostgreSQL/MySQL（生产环境）。

数据表：
- **users**: 用户信息（openid, nickname）
- **todo_items**: 待办事项（content, status, priority, due_date）

## 开发指南

### 添加新功能

1. **添加新的Function Calling函数**:
   - 在 `app/utils/llm_tools.py` 中定义函数Schema和实现
   - 在 `LLMTools` 类中添加对应方法

2. **修改提示词**:
   - 编辑 `prompts/prompts.yml`
   - 系统会自动加载

3. **添加新服务**:
   - 在 `app/services/` 创建新服务类
   - 在 `app/__init__.py` 中注册

## 生产部署建议

1. 使用Gunicorn替代Flask开发服务器
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 run:app
   ```

2. 使用Supervisor管理进程
3. 使用Nginx作为反向代理
4. 使用PostgreSQL替代SQLite
5. 配置日志系统
6. 设置环境变量，不在代码中硬编码密钥

## 故障排查

### 微信服务器连接超时
- 检查服务器防火墙设置
- 确保公网IP可访问
- 查看Nginx配置

### 消息解密失败
- 确认Token、AES Key、AppID配置正确
- 检查消息加解密方式为"安全模式"

### 大模型调用失败
- 检查API Key是否有效
- 确认API Base URL正确
- 查看余额是否充足

## 许可证

MIT License

## 联系方式

如有问题，请提Issue或联系开发者。

