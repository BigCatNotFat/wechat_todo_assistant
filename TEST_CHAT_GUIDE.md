# test_chat.py 使用指南

## 📖 概述

`test_chat.py` 是一个命令行测试工具，用于在本地测试待办助手的所有功能，无需微信接入。

**最新更新**：现在通过 `wechat_service.handle_message()` 处理所有消息，完全模拟微信消息处理流程，支持系统命令测试。

## 🚀 启动方式

```bash
python test_chat.py
```

## 💬 命令类型说明

### 1. 测试工具专用命令（本地命令）

这些命令只在测试工具中有效，**不会发送给助手**：

| 命令 | 功能 |
|------|------|
| `todos` | 显示所有待办事项（格式化显示） |
| `history` / `h` | 查看对话历史（带时间戳） |
| `cls` | 清屏 |
| `exit` / `quit` / `q` | 退出程序 |

### 2. 系统命令

这些命令会发送给助手，由 `CommandService` 处理，**不经过 AI**：

| 命令 | 功能 |
|------|------|
| `help` / `帮助` | 显示系统命令帮助 |
| `clear` | 清空对话历史 |
| `stats` / `统计` | 查看数据统计 |
| `reset` / `重置` | 重置所有数据（慎用） |

### 3. 普通对话

其他所有输入都会通过 `wechat_service` 处理，由 AI 智能识别并执行：

```
明天下午3点开会         → 创建待办
查看待办                → 查看待办列表
完成第一个任务          → 标记任务完成
删除任务2               → 删除任务
帮我规划今天的任务      → 任务规划建议
```

## 🔄 消息处理流程

```
用户输入
  ↓
是测试工具专用命令？
  ↓ YES → 本地处理（todos, history, cls, exit）
  ↓ NO
创建 MockWeChatMessage
  ↓
wechat_service.handle_message()
  ↓
是系统命令？
  ↓ YES → command_service 处理（help, clear, stats, reset）
  ↓ NO
  ↓
llm_service 处理（AI 对话 + Function Calling）
```

## ✨ 特性

### 1. 完整的消息处理流程模拟

通过创建 `MockWeChatMessage` 对象，完全模拟微信消息：

```python
mock_msg = MockWeChatMessage(
    content=user_input,
    source=user.openid,
    msg_type='text'
)
```

### 2. 自动测试系统命令

现在可以直接测试系统命令功能：

```
👤 您: help
🤖 助手: 📖 系统命令帮助
...

👤 您: stats
🤖 助手: 📊 数据统计
...

👤 您: clear
🤖 助手: ✅ 已清空对话历史！共清除了 4 条记录。
```

### 3. 支持上下文记忆

对话历史自动管理，AI 可以记住之前的对话：

```
👤 您: 明天开会
🤖 助手: 好的，我帮你记录了...

👤 您: 几点开会来着？
🤖 助手: 您之前说的是明天开会...
```

### 4. Function Calling 支持

AI 会自动识别意图并调用相应的功能：

```
👤 您: 查看我的待办
🤖 助手: [调用 query_todos 函数]
您当前有 3 个待办事项...
```

## 📋 使用示例

### 示例1：测试系统命令

```
👤 您: stats
🤖 助手: 📊 数据统计

💬 对话数据：
• 历史对话：6 条

✅ 待办数据：
• 总计：3 个
• 待完成：2 个
• 已完成：1 个
• 完成率：33.3%
```

### 示例2：查看本地历史

```
👤 您: history
====================================================
📜 对话历史
====================================================
1. [14:23:45] 👤 明天开会...
2. [14:23:47] 🤖 好的，我帮你记录了...
3. [14:24:10] 👤 查看待办...
4. [14:24:12] 🤖 您当前有 3 个待办事项...

共 4 条消息
====================================================
```

### 示例3：清空对话历史

```
👤 您: clear
🤖 助手: ✅ 已清空对话历史！
共清除了 4 条记录。

👤 您: history
====================================================
📜 对话历史
====================================================
暂无历史记录
====================================================
```

## 🎯 与微信实际运行的区别

| 特性 | test_chat.py | 微信运行 |
|------|-------------|----------|
| 消息对象 | MockWeChatMessage | 真实微信消息对象 |
| 消息加密 | 无 | WeChatCrypto 加密/解密 |
| 用户识别 | 固定测试用户 | 真实 OpenID |
| 响应方式 | 命令行打印 | 微信消息推送 |
| 处理流程 | ✅ 完全一致 | ✅ 完全一致 |

## 🔧 代码结构

### MockWeChatMessage 类

```python
class MockWeChatMessage:
    """模拟微信消息对象，用于测试"""
    
    def __init__(self, content, source, msg_type='text'):
        self.content = content    # 消息内容
        self.source = source      # 发送者 OpenID
        self.type = msg_type      # 消息类型
```

### 核心调用

```python
reply = wechat_service.handle_message(
    msg=mock_msg,
    llm_service=llm_service,
    user_id=user.id,
    command_service=command_service
)
```

## 🐛 常见问题

### Q: 为什么 'clear' 是系统命令，'cls' 是清屏？

A: 
- `clear` - 发送给助手，清空对话历史（系统命令）
- `cls` - 测试工具命令，清空终端屏幕

### Q: 如何区分系统命令和普通对话？

A: 系统命令会立即返回结果，不经过 AI 处理，速度更快。普通对话需要等待 AI 思考和响应。

### Q: 对话历史保存在哪里？

A: 保存在内存中（`ConversationService`），重启应用后会丢失。微信实际运行时也是这样设计的。

### Q: 待办事项保存在哪里？

A: 保存在 SQLite 数据库中（`instance/app.db`），持久化存储。

## 💡 开发建议

### 添加新的测试工具命令

在 `main()` 函数中添加：

```python
if user_input.lower() == 'mycommand':
    # 处理逻辑
    print("执行了 mycommand")
    continue
```

### 测试新的系统命令

直接在对话中输入即可，无需修改 `test_chat.py`：

```
👤 您: mycommand
🤖 助手: [由 CommandService 处理]
```

### 调试技巧

1. 查看日志输出（控制台）
2. 使用 `history` 查看对话历史
3. 使用 `todos` 查看数据库状态
4. 使用 `stats` 查看统计信息

## 📚 相关文档

- **SYSTEM_COMMANDS.md** - 系统命令详细说明
- **IMPLEMENTATION_SUMMARY.md** - 系统命令实施总结
- **TEST_GUIDE.md** - 完整测试指南

## ✅ 总结

`test_chat.py` 现在是一个完整的测试工具，支持：

✅ 完整的消息处理流程模拟
✅ 系统命令测试
✅ 对话上下文记忆
✅ Function Calling 测试
✅ 友好的命令行界面
✅ 本地调试辅助功能

完美的本地测试环境！🚀

