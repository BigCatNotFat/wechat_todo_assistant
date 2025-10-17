# 消息处理流程图

## 📊 完整流程图

```
┌─────────────────────────────────────────────────────────────────────┐
│                         微信服务器                                    │
│                      发送加密的 XML 消息                               │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  📁 app/wechat/routes.py                                             │
│  └─ wechat_handler()                                                 │
│     ├─ 1. 验证签名 (WeChatCrypto)                                    │
│     ├─ 2. 解密消息体                                                  │
│     └─ 3. 获取服务实例                                                │
│        • wechat_service                                              │
│        • llm_service                                                 │
│        • todo_service                                                │
│        • command_service                                             │
└────────────────────────────┬────────────────────────────────────────┘
                             │ decrypted_xml
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  📁 app/services/wechat_service.py                                   │
│  └─ parse_message(xml_data)                                          │
│     └─ 解析 XML → 消息对象 (msg)                                     │
│        • msg.type = 'text'                                           │
│        • msg.content = "用户输入的内容"                               │
│        • msg.source = "openid"                                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │ msg object
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  📁 app/services/wechat_service.py                                   │
│  └─ handle_message(msg, llm_service, user_id, command_service)      │
│                                                                       │
│     ┌────────────────────────────────────────┐                      │
│     │ 是文本消息吗？ (msg.type == 'text')    │                      │
│     └───────────┬────────────────────────────┘                      │
│                 │ YES                                                │
│                 ▼                                                    │
│     ┌────────────────────────────────────────┐                      │
│     │ 是系统命令吗？                         │                      │
│     │ command_service.is_system_command()    │                      │
│     └───────┬───────────────┬────────────────┘                      │
│             │ YES           │ NO                                     │
└─────────────┼───────────────┼────────────────────────────────────────┘
              │               │
              ▼               ▼
    ┌─────────────────┐   ┌──────────────────────────────────────┐
    │  系统命令处理    │   │  AI 处理流程                          │
    └─────────────────┘   └──────────────────────────────────────┘
              │               │
              │               │
              ▼               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  📁 app/services/command_service.py          【系统命令分支】          │
│  └─ execute_command(message, user_id)                               │
│                                                                       │
│     命令映射表:                                                        │
│     ┌───────────┬──────────────────────┐                            │
│     │ 'clear'   │ → _clear_history()   │                            │
│     │ 'help'    │ → _show_help()       │                            │
│     │ 'stats'   │ → _show_stats()      │                            │
│     │ 'reset'   │ → _reset_all()       │                            │
│     └───────────┴──────────────────────┘                            │
│                                                                       │
│     直接操作:                                                         │
│     • conversation_service (对话历史)                                │
│     • todo_service (待办数据)                                        │
│                                                                       │
│     返回: "[sys] 命令结果..."                                        │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ 系统命令结果
                             │
                             └──────────┐
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│  📁 app/services/conversation_service.py     【AI 处理分支】          │
│  └─ 对话历史管理                                                      │
│     ├─ 1. 保存用户消息                                               │
│     │   add_message(user_id, 'user', content)                       │
│     │                                                                │
│     ├─ 2. 获取历史对话                                               │
│     │   get_recent_history(user_id)                                 │
│     │   └─ 返回最近 10 轮对话（24小时内）                            │
│     │                                                                │
│     └─ 3. 自动清理过期对话                                           │
└────────────────────────────┬────────────────────────────────────────┘
                             │ conversation_history
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  📁 app/services/llm_service.py                                      │
│  └─ chat_with_function_calling(user_id, user_message, history)      │
│                                                                       │
│     ┌──────────────────────────────────────────────┐                │
│     │ 1. 准备消息列表                              │                │
│     │    • System Prompt (从 prompt_manager)       │                │
│     │    • 历史对话 (conversation_history)         │                │
│     │    • 当前用户消息                             │                │
│     └──────────────────────────────────────────────┘                │
│                          │                                           │
│                          ▼                                           │
│     ┌──────────────────────────────────────────────┐                │
│     │ 2. 调用 OpenAI API                           │                │
│     │    • model: gpt-4o-mini                      │                │
│     │    • tools: Function Calling 定义            │                │
│     │    • temperature: 0.7                        │                │
│     └──────────────────────────────────────────────┘                │
│                          │                                           │
│                          ▼                                           │
│     ┌──────────────────────────────────────────────┐                │
│     │ 3. 处理 AI 响应                              │                │
│     │    ├─ 普通文本回复                            │                │
│     │    └─ Function Call 请求                     │                │
│     └──────────────────────────────────────────────┘                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ 是否需要 Function Call?
                             │
              ┌──────────────┴──────────────┐
              │ YES                         │ NO
              ▼                             ▼
┌──────────────────────────────┐   ┌──────────────────┐
│ Function Calling 流程        │   │ 直接返回文本回复  │
└──────────────────────────────┘   └──────────────────┘
              │                             │
              ▼                             │
┌─────────────────────────────────────────────────────────────────────┐
│  📁 app/utils/llm_tools.py                                           │
│  └─ 可调用的函数                                                      │
│                                                                       │
│     ┌──────────────────────────────────────────────┐                │
│     │ create_todo()                                │                │
│     │ • 创建待办事项                                │                │
│     │ • 调用 todo_service.create_todo()            │                │
│     └──────────────────────────────────────────────┘                │
│                                                                       │
│     ┌──────────────────────────────────────────────┐                │
│     │ query_todos()                                │                │
│     │ • 查询待办列表                                │                │
│     │ • 调用 todo_service.get_user_todos()         │                │
│     └──────────────────────────────────────────────┘                │
│                                                                       │
│     ┌──────────────────────────────────────────────┐                │
│     │ mark_todo_complete()                         │                │
│     │ • 标记任务完成                                │                │
│     │ • 调用 todo_service.mark_todo_as_complete()  │                │
│     └──────────────────────────────────────────────┘                │
│                                                                       │
│     ┌──────────────────────────────────────────────┐                │
│     │ delete_todo()                                │                │
│     │ • 删除待办事项                                │                │
│     │ • 调用 todo_service.delete_todo()            │                │
│     └──────────────────────────────────────────────┘                │
│                                                                       │
│     返回: 函数执行结果 (JSON)                                         │
└────────────────────────────┬────────────────────────────────────────┘
                             │ function_result
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  📁 app/services/todo_service.py                                     │
│  └─ 数据库操作                                                        │
│     ├─ create_todo() → INSERT                                        │
│     ├─ get_user_todos() → SELECT                                     │
│     ├─ mark_todo_as_complete() → UPDATE                              │
│     └─ delete_todo() → DELETE                                        │
│                                                                       │
│  ↕ SQLAlchemy ORM                                                    │
│                                                                       │
│  📁 app/database/db.py                                               │
│  └─ SQLite 数据库: instance/app.db                                   │
│                                                                       │
│  📁 app/models/                                                      │
│  ├─ user.py (User 模型)                                              │
│  └─ todo_item.py (TodoItem 模型)                                     │
└────────────────────────────┬────────────────────────────────────────┘
                             │ 数据库操作结果
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  📁 app/services/llm_service.py                                      │
│  └─ 4. 再次调用 OpenAI API                                           │
│     • 携带 function 执行结果                                          │
│     • AI 生成最终的自然语言回复                                       │
│                                                                       │
│     返回: "好的，我帮你记录了待办事项..."                             │
└────────────────────────────┬────────────────────────────────────────┘
                             │ AI 回复
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  📁 app/services/conversation_service.py                             │
│  └─ 保存 AI 回复到历史                                               │
│     add_message(user_id, 'assistant', reply_content)                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
        ┌────────────────────┴──────────────────────┐
        │                                           │
        ▼                                           ▼
  系统命令结果                                   AI 回复
  "[sys] ✅ ..."                                "好的，..."
        │                                           │
        └────────────────────┬──────────────────────┘
                             │ reply_content
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  📁 app/services/wechat_service.py                                   │
│  └─ create_text_reply(content, message)                             │
│     └─ 创建 XML 格式的回复消息                                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │ reply_xml
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  📁 app/wechat/routes.py                                             │
│  └─ wechat_handler()                                                 │
│     ├─ 加密回复消息 (WeChatCrypto)                                  │
│     └─ 返回加密后的 XML                                              │
└────────────────────────────┬────────────────────────────────────────┘
                             │ encrypted_xml
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         微信服务器                                    │
│                    接收并推送给用户                                   │
└─────────────────────────────────────────────────────────────────────┘
```

## 📝 文件职责说明

### 视图层 (View Layer)

| 文件 | 职责 | 主要功能 |
|------|------|----------|
| `app/wechat/routes.py` | 路由控制 | • 接收微信请求<br>• 消息加密/解密<br>• 签名验证<br>• 调用服务层 |

### 服务层 (Service Layer)

| 文件 | 职责 | 主要功能 |
|------|------|----------|
| `app/services/wechat_service.py` | 微信消息处理 | • 解析消息<br>• 路由到命令/AI<br>• 创建回复<br>• 管理对话历史 |
| `app/services/command_service.py` | 系统命令处理 | • 命令识别<br>• 命令执行<br>• 返回系统回复 |
| `app/services/llm_service.py` | AI 交互 | • 调用 OpenAI API<br>• Function Calling<br>• 生成 AI 回复 |
| `app/services/todo_service.py` | 待办事项管理 | • CRUD 操作<br>• 业务逻辑<br>• 用户管理 |
| `app/services/conversation_service.py` | 对话历史管理 | • 保存对话<br>• 获取历史<br>• 自动清理 |
| `app/services/planning_service.py` | 任务规划 | • 生成日报<br>• 任务推送 |

### 工具层 (Utility Layer)

| 文件 | 职责 | 主要功能 |
|------|------|----------|
| `app/utils/llm_tools.py` | Function Calling | • 定义可调用函数<br>• 执行实际操作 |
| `app/utils/prompt_manager.py` | 提示词管理 | • 加载提示词<br>• 提供系统提示 |
| `app/utils/scheduler.py` | 定时任务 | • 每日推送 |

### 数据层 (Data Layer)

| 文件 | 职责 | 主要功能 |
|------|------|----------|
| `app/database/db.py` | 数据库连接 | • SQLAlchemy 实例 |
| `app/models/user.py` | 用户模型 | • User 表定义 |
| `app/models/todo_item.py` | 待办模型 | • TodoItem 表定义 |

### 配置层

| 文件 | 职责 |
|------|------|
| `config.py` | 全局配置 |
| `prompts/prompts.yml` | 提示词配置 |

## 🔀 决策点详解

### 决策点1：是否是系统命令？

```python
# app/services/wechat_service.py
if command_service and command_service.is_system_command(user_message):
    # → 系统命令分支
    return command_service.execute_command(user_message, user_id)
else:
    # → AI 处理分支
    ...
```

**判断依据**：
- `clear`, `help`, `帮助`, `stats`, `统计`, `reset`, `重置`
- 完全匹配（忽略大小写和首尾空格）

### 决策点2：是否需要 Function Call？

```python
# app/services/llm_service.py
if response.choices[0].message.tool_calls:
    # → 执行 Function Calling
    for tool_call in tool_calls:
        function_result = execute_function(tool_call)
    # → 再次调用 LLM 生成自然语言回复
else:
    # → 直接返回文本回复
    return response.choices[0].message.content
```

**判断依据**：
- OpenAI API 返回是否包含 `tool_calls`
- AI 判断用户意图是否需要调用函数

## 📊 数据流转示例

### 示例1：系统命令 "stats"

```
用户输入: "stats"
    ↓
routes.py (解密)
    ↓
wechat_service.parse_message()
    ↓
wechat_service.handle_message()
    ↓
command_service.is_system_command("stats") → True
    ↓
command_service.execute_command("stats", user_id)
    ↓
command_service._show_stats(user_id)
    ├─ conversation_service.get_recent_history()
    └─ todo_service.get_user_todos()
    ↓
返回: "[sys] 📊 数据统计\n..."
    ↓
wechat_service.create_text_reply()
    ↓
routes.py (加密)
    ↓
发送给微信服务器
```

**耗时**: ~50ms
**经过文件**: 4个
**是否调用 AI**: ❌ 否

### 示例2：普通对话 "明天开会"

```
用户输入: "明天开会"
    ↓
routes.py (解密)
    ↓
wechat_service.parse_message()
    ↓
wechat_service.handle_message()
    ↓
command_service.is_system_command("明天开会") → False
    ↓
conversation_service.add_message('user', '明天开会')
conversation_service.get_recent_history() → [...]
    ↓
llm_service.chat_with_function_calling()
    ├─ 准备消息列表
    ├─ 调用 OpenAI API (第1次)
    ├─ AI 返回: tool_call(create_todo)
    ├─ 执行 llm_tools.create_todo()
    │   └─ todo_service.create_todo() → 数据库 INSERT
    ├─ 调用 OpenAI API (第2次，携带函数结果)
    └─ AI 返回: "好的，我帮你记录了..."
    ↓
conversation_service.add_message('assistant', '好的，...')
    ↓
wechat_service.create_text_reply()
    ↓
routes.py (加密)
    ↓
发送给微信服务器
```

**耗时**: ~2-3秒
**经过文件**: 8个
**是否调用 AI**: ✅ 是 (2次)
**数据库操作**: ✅ 是 (INSERT)

### 示例3：查询待办 "查看待办"

```
用户输入: "查看待办"
    ↓
[前面流程同上]
    ↓
llm_service.chat_with_function_calling()
    ├─ 调用 OpenAI API (第1次)
    ├─ AI 返回: tool_call(query_todos)
    ├─ 执行 llm_tools.query_todos()
    │   └─ todo_service.get_user_todos() → 数据库 SELECT
    ├─ 调用 OpenAI API (第2次)
    └─ AI 返回: "您当前有3个待办事项..."
    ↓
[后续流程同上]
```

**耗时**: ~2-3秒
**数据库操作**: ✅ 是 (SELECT)

## 🎯 性能对比

| 操作类型 | 响应时间 | AI 调用 | 数据库操作 |
|---------|---------|---------|------------|
| 系统命令 (clear) | ~50ms | ❌ | ❌ |
| 系统命令 (stats) | ~100ms | ❌ | ✅ |
| 创建待办 | ~2-3s | ✅ (2次) | ✅ (INSERT) |
| 查询待办 | ~2-3s | ✅ (2次) | ✅ (SELECT) |
| 完成任务 | ~2-3s | ✅ (2次) | ✅ (UPDATE) |
| 普通对话 | ~1-2s | ✅ (1次) | ❌ |

## 💡 关键点总结

1. **系统命令优先级最高**：先判断系统命令，再走 AI 流程
2. **对话历史自动管理**：每次对话都会记录和清理
3. **Function Calling 自动化**：AI 自动判断是否需要调用函数
4. **分层架构清晰**：视图→服务→数据，职责明确
5. **异步友好**：各层之间松耦合，易于扩展

## 📚 相关文档

- **SYSTEM_COMMANDS.md** - 系统命令详细说明
- **PROJECT_STRUCTURE.md** - 项目结构文档
- **TEST_GUIDE.md** - 测试指南

---

**图例说明**：
- `📁` 表示文件
- `→` 表示数据流向
- `↓` 表示流程继续
- `├─` 表示步骤分支
- `└─` 表示最后一个步骤

