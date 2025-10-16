# 项目结构说明

本文档详细说明项目的文件结构和各模块职责。

## 目录树

```
wechat_todo_assistant/
│
├── 📄 run.py                    # 项目启动入口
├── 📄 config.py                 # 配置文件（各环境配置）
├── 📄 requirements.txt          # Python依赖清单
├── 📄 .gitignore               # Git忽略文件
├── 📄 env.example              # 环境变量示例
│
├── 📜 README.md                # 项目说明文档
├── 📜 USAGE.md                 # 使用指南
├── 📜 DEPLOY.md                # 部署指南
├── 📜 FAQ.md                   # 常见问题
├── 📜 PROJECT_STRUCTURE.md     # 本文件
│
├── 🐳 Dockerfile               # Docker镜像构建文件
├── 🐳 docker-compose.yml       # Docker Compose配置
│
├── 🔧 test_setup.py            # 配置测试脚本
├── 🚀 start.sh                 # Linux/Mac启动脚本
├── 🚀 start.bat                # Windows启动脚本
│
├── 📁 prompts/                 # 提示词配置目录
│   └── prompts.yml            # 提示词配置文件
│
├── 📁 instance/                # 实例文件夹（不提交到Git）
│   └── app.db                 # SQLite数据库文件
│
├── 📁 logs/                    # 日志目录（不提交到Git）
│   └── app.log                # 应用日志
│
└── 📁 app/                     # 主应用包
    │
    ├── 📄 __init__.py          # 应用工厂，初始化Flask App
    │
    ├── 📁 database/            # 数据库层
    │   ├── __init__.py
    │   └── db.py              # SQLAlchemy实例
    │
    ├── 📁 models/              # 数据模型层
    │   ├── __init__.py
    │   ├── user.py            # 用户模型
    │   └── todo_item.py       # 待办事项模型
    │
    ├── 📁 services/            # 业务服务层
    │   ├── __init__.py
    │   ├── todo_service.py    # 待办事项业务逻辑
    │   ├── llm_service.py     # 大模型交互服务
    │   ├── wechat_service.py  # 微信API服务
    │   └── planning_service.py # 任务规划服务
    │
    ├── 📁 utils/               # 工具层
    │   ├── __init__.py
    │   ├── llm_tools.py       # Function Calling工具集
    │   ├── scheduler.py       # 定时任务调度器
    │   └── prompt_manager.py  # 提示词管理器
    │
    └── 📁 wechat/              # 视图层（微信接口）
        ├── __init__.py        # 蓝图定义
        └── routes.py          # 路由处理
```

## 分层架构详解

### 1️⃣ 视图层 (View Layer) - `/app/wechat/`

**职责**: 接收外部请求，返回响应

- `routes.py`: 
  - 处理微信服务器的GET/POST请求
  - 验证签名
  - 消息加密/解密
  - 调用服务层处理业务

**特点**: 
- 只负责HTTP协议相关的事情
- 不包含业务逻辑
- 数据验证和格式转换

### 2️⃣ 服务层 (Service Layer) - `/app/services/`

**职责**: 核心业务逻辑处理

#### `todo_service.py` - 待办事项服务
- 待办事项的增删改查
- 用户管理
- 数据统计

主要方法：
```python
- create_todo()              # 创建待办
- get_user_todos()           # 获取用户待办列表
- mark_todo_as_complete()    # 标记完成
- delete_todo()              # 删除待办
- update_todo()              # 更新待办
- get_today_todos()          # 获取今日待办
- get_yesterday_completed_todos() # 获取昨日完成
- get_or_create_user()       # 获取或创建用户
```

#### `llm_service.py` - 大模型服务
- 与大模型API交互
- Function Calling处理
- 提示词管理
- 对话上下文管理

主要方法：
```python
- chat_with_function_calling() # 对话并支持函数调用
- generate_daily_plan()        # 生成每日规划
```

#### `wechat_service.py` - 微信服务
- 微信消息解析
- 微信消息回复
- AccessToken管理
- 客服消息发送

主要方法：
```python
- get_access_token()      # 获取AccessToken（带缓存）
- parse_message()         # 解析微信消息
- create_text_reply()     # 创建文本回复
- send_customer_message() # 发送客服消息
- handle_message()        # 处理消息（协调器）
```

#### `planning_service.py` - 任务规划服务
- 每日任务规划
- 任务优先级分析
- 批量推送管理

主要方法：
```python
- generate_daily_plan_for_user()  # 为用户生成规划
- send_daily_plan_to_user()       # 发送规划给用户
- send_daily_plan_to_all_users()  # 批量发送
```

### 3️⃣ 数据访问层 (Data Access Layer) - `/app/models/`

**职责**: 数据持久化

#### `user.py` - 用户模型
数据表字段：
```python
- id: 主键
- openid: 微信OpenID（唯一）
- nickname: 昵称
- created_at: 创建时间
- updated_at: 更新时间
- todo_items: 关联的待办事项（一对多）
```

#### `todo_item.py` - 待办事项模型
数据表字段：
```python
- id: 主键
- user_id: 用户ID（外键）
- content: 待办内容
- status: 状态（pending/completed/cancelled）
- priority: 优先级（high/medium/low）
- due_date: 截止日期
- created_at: 创建时间
- completed_at: 完成时间
- updated_at: 更新时间
```

### 4️⃣ 工具层 (Utils) - `/app/utils/`

**职责**: 提供通用工具和辅助功能

#### `llm_tools.py` - Function Calling工具
- 定义可供大模型调用的函数
- 函数Schema定义
- 函数执行逻辑

定义的函数：
```python
- create_todo()      # 创建待办
- get_todo_list()    # 查询待办列表
- complete_todo()    # 完成待办
- delete_todo()      # 删除待办
- update_todo()      # 更新待办
```

#### `scheduler.py` - 定时任务调度器
- 基于APScheduler
- 支持Cron表达式
- 任务管理

主要方法：
```python
- start()           # 启动调度器
- shutdown()        # 关闭调度器
- add_daily_job()   # 添加每日任务
- remove_job()      # 移除任务
```

#### `prompt_manager.py` - 提示词管理器
- 加载YAML提示词配置
- 提示词模板填充
- 热重载支持

主要方法：
```python
- load_prompts()    # 加载提示词
- get_prompt()      # 获取并格式化提示词
- reload()          # 重新加载
```

### 5️⃣ 数据库层 - `/app/database/`

**职责**: SQLAlchemy实例管理

- `db.py`: 创建全局db对象，避免循环导入

### 6️⃣ 配置层 - 根目录

#### `config.py` - 配置管理
- 不同环境的配置类
- 从环境变量读取敏感信息
- 提供配置字典

配置类：
```python
- Config              # 基础配置
- DevelopmentConfig   # 开发环境
- ProductionConfig    # 生产环境
```

#### `run.py` - 启动入口
- 创建Flask应用实例
- 启动开发服务器
- 环境检测

## 数据流向

### 用户发送消息流程

```
用户微信 
  ↓
微信服务器 (加密消息)
  ↓
routes.py (解密、验证)
  ↓
wechat_service.py (解析消息)
  ↓
llm_service.py (理解意图)
  ↓
llm_tools.py (执行函数)
  ↓
todo_service.py (业务处理)
  ↓
models (数据库操作)
  ↓
返回结果
  ↓
wechat_service.py (创建回复)
  ↓
routes.py (加密回复)
  ↓
微信服务器
  ↓
用户微信
```

### 定时任务流程

```
scheduler.py (定时触发)
  ↓
planning_service.py
  ↓
todo_service.py (获取数据)
  ↓
llm_service.py (生成规划)
  ↓
wechat_service.py (发送客服消息)
  ↓
微信服务器
  ↓
用户微信
```

## 关键技术点

### 1. 应用工厂模式

使用 `create_app()` 工厂函数创建应用，便于：
- 测试时创建多个实例
- 不同环境使用不同配置
- 延迟初始化扩展

### 2. 蓝图 (Blueprint)

模块化路由管理：
- `wechat_bp`: 微信接口路由
- 便于扩展更多功能模块

### 3. 依赖注入

服务实例通过 `app` 对象传递：
```python
app.todo_service
app.llm_service
app.wechat_service
app.planning_service
```

### 4. 环境变量管理

敏感信息通过环境变量配置：
- `.env` 文件 (开发)
- 系统环境变量 (生产)

### 5. 定时任务

APScheduler后台调度器：
- 每日定时推送
- 异步执行
- 持久化任务

### 6. Function Calling

大模型函数调用：
- Schema定义
- 参数验证
- 结果处理

## 扩展指南

### 添加新功能

1. **添加数据模型**:
   - 在 `app/models/` 创建新模型
   - 定义字段和关系
   - 更新 `__init__.py`

2. **添加业务服务**:
   - 在 `app/services/` 创建服务类
   - 实现业务逻辑
   - 在 `app/__init__.py` 注册

3. **添加Function Calling**:
   - 在 `llm_tools.py` 定义Schema
   - 实现函数逻辑
   - 更新提示词

4. **添加路由**:
   - 在蓝图中添加路由
   - 或创建新蓝图

### 修改配置

1. **修改提示词**: 编辑 `prompts/prompts.yml`
2. **修改配置**: 编辑 `config.py` 或 `.env`
3. **修改定时任务**: 在 `app/__init__.py` 中调整

## 开发建议

### 代码规范

- 遵循PEP8规范
- 函数添加文档字符串
- 合理使用类型注解
- 适当的错误处理

### 调试技巧

- 开启DEBUG模式查看详细日志
- 使用 `test_setup.py` 测试配置
- 查看各层日志定位问题
- 使用微信调试工具

### 安全注意

- 不要提交 `.env` 文件
- 敏感信息使用环境变量
- 定期更换密钥
- HTTPS传输

---

希望这份文档能帮助你快速理解项目结构！

