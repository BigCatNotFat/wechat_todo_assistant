# 系统命令使用指南

## 📖 概述

系统命令功能允许用户通过发送特定的关键词来执行系统级操作，这些命令不会经过大模型处理，而是直接由 `CommandService` 处理，响应速度更快且更可靠。

## 🎯 架构说明

### 处理流程

```
微信消息 → routes.py (解密)
          ↓
    wechat_service.handle_message()
          ↓
    ┌─────────────────┐
    │ 是系统命令吗？   │
    └─────────────────┘
          ↓ YES              ↓ NO
   command_service     →   llm_service
   (立即返回结果)         (AI处理)
```

### 代码位置

- **命令服务**: `app/services/command_service.py`
- **服务注册**: `app/__init__.py`
- **消息路由**: `app/wechat/routes.py`
- **消息处理**: `app/services/wechat_service.py`

## 📋 当前支持的命令

| 命令 | 别名 | 功能 | 示例 |
|------|------|------|------|
| `clear` | - | 清空对话历史 | 发送 "clear" |
| `help` | `帮助` | 显示帮助信息 | 发送 "help" 或 "帮助" |
| `stats` | `统计` | 查看统计数据 | 发送 "stats" 或 "统计" |
| `reset` | `重置` | 重置所有数据（慎用） | 发送 "reset" 或 "重置" |

## 🛠️ 如何添加新命令

### 方法1: 简单命令（推荐）

在 `app/services/command_service.py` 中添加：

```python
def __init__(self, conversation_service, todo_service):
    # ... 现有代码 ...
    
    self.commands = {
        # ... 现有命令 ...
        'version': self._show_version,  # 添加新命令
        '版本': self._show_version,     # 中文别名
    }

def _show_version(self, user_id):
    """显示版本信息"""
    return """📦 在办小助手 v1.0.0
    
功能特性：
• 智能待办管理
• 对话上下文记忆
• 每日任务规划

更新时间: 2024-10-17"""
```

### 方法2: 需要参数的命令

```python
def __init__(self, conversation_service, todo_service):
    # 特殊处理：带参数的命令需要单独检测
    pass

def is_system_command(self, message):
    """判断是否是系统命令"""
    msg = message.strip().lower()
    
    # 精确匹配的命令
    if msg in self.commands:
        return True
    
    # 带参数的命令（例如: delete 1）
    if msg.startswith('delete '):
        return True
    
    return False

def execute_command(self, message, user_id):
    """执行系统命令"""
    msg = message.strip().lower()
    
    # 处理带参数的命令
    if msg.startswith('delete '):
        todo_id = msg.split(' ')[1]
        return self._delete_todo(user_id, todo_id)
    
    # 处理普通命令
    if msg in self.commands:
        return self.commands[msg](user_id)
    
    return None

def _delete_todo(self, user_id, todo_id):
    """删除待办"""
    try:
        success = self.todo_service.delete_todo(int(todo_id), user_id)
        if success:
            return f"✅ 已删除待办事项 #{todo_id}"
        else:
            return f"❌ 待办事项 #{todo_id} 不存在"
    except ValueError:
        return "❌ 待办ID必须是数字"
```

## 📝 命令设计最佳实践

### 1. 命令命名规范

- ✅ 使用简短、易记的英文单词
- ✅ 提供中文别名以提升用户体验
- ✅ 命令名不区分大小写
- ✅ 自动去除前后空格

```python
# 好的例子
'clear'  → 清空
'help'   → 帮助
'stats'  → 统计

# 不好的例子
'clearconversationhistory'  # 太长
'clr'                       # 不直观
```

### 2. 返回消息格式

使用表情符号和格式化文本提升可读性：

```python
def _example_command(self, user_id):
    return """✅ 操作成功

📊 统计数据：
• 项目1: 10
• 项目2: 20

💡 提示：可以使用 help 查看更多命令"""
```

### 3. 错误处理

所有命令处理函数都应包含异常处理：

```python
def _risky_command(self, user_id):
    """可能出错的命令"""
    try:
        # 执行可能出错的操作
        result = self.do_something(user_id)
        return f"✅ 操作成功: {result}"
    except ValueError as e:
        return f"❌ 参数错误: {str(e)}"
    except Exception as e:
        print(f"命令执行异常: {e}")
        import traceback
        traceback.print_exc()
        return "❌ 操作失败，请稍后重试"
```

## 🧪 测试命令

### 运行测试脚本

```bash
python test_command.py
```

### 手动测试

1. 启动应用：`python run.py`
2. 在微信中发送命令关键词
3. 查看控制台输出和微信回复

### 测试清单

- [ ] 命令能正确识别（包括大小写、空格）
- [ ] 中文别名能正常工作
- [ ] 返回消息格式正确、清晰
- [ ] 错误情况有友好的提示
- [ ] 不影响正常的AI对话功能

## 🔍 调试技巧

### 查看命令是否被识别

在 `app/services/wechat_service.py` 的 `handle_message()` 中有日志：

```python
if command_service and command_service.is_system_command(user_message):
    print(f"检测到系统命令: {user_message}")  # 这里会打印
    return command_service.execute_command(user_message, user_id)
```

### 查看所有注册的命令

```python
# 在代码中
all_commands = app.command_service.get_all_commands()
print(f"支持的命令: {all_commands}")
```

## ⚠️ 注意事项

### 1. 命令优先级

系统命令的优先级**高于** AI 对话处理，这意味着：

- ✅ 用户发送 "help" 会触发系统帮助，而不是 AI 回答
- ⚠️ 避免使用常见词作为命令（如 "你好"、"谢谢"）
- ⚠️ 命令关键词应该足够特殊，不易误触发

### 2. 对话历史

- 系统命令**不会**被记录到对话历史中
- 系统命令的回复**也不会**被记录到对话历史
- 这样可以保持对话上下文的纯净

### 3. 性能考虑

- 系统命令直接返回，不调用 LLM，速度更快
- 适合频繁使用的功能（如查看统计、清空历史）
- 不适合需要自然语言理解的功能

## 📚 扩展示例

### 示例1: 导出待办事项

```python
def _export_todos(self, user_id):
    """导出待办事项为文本格式"""
    todos = self.todo_service.get_user_todos(user_id)
    
    if not todos:
        return "📭 暂无待办事项"
    
    result = ["📋 我的待办事项\n"]
    
    for i, todo in enumerate(todos, 1):
        status = "✅" if todo.status == 'completed' else "⏳"
        result.append(f"{i}. {status} {todo.content}")
        if todo.due_date:
            result.append(f"   ⏰ {todo.due_date.strftime('%Y-%m-%d')}")
    
    return "\n".join(result)
```

### 示例2: 快捷回复

```python
def _quick_reply(self, user_id):
    """常用快捷回复"""
    return """⚡ 快捷操作：
    
回复数字选择：
1️⃣ 查看今日待办
2️⃣ 查看本周待办
3️⃣ 添加新待办
4️⃣ 返回主菜单

请直接回复数字..."""
```

## 🎓 总结

系统命令功能提供了一种快速、可靠的方式来处理特定操作，适合：

- ✅ 系统管理类操作（清空、重置）
- ✅ 查询统计信息
- ✅ 显示帮助文档
- ✅ 快捷功能入口

不适合：

- ❌ 需要自然语言理解的任务
- ❌ 复杂的业务逻辑
- ❌ 需要上下文理解的对话

合理使用系统命令可以提升用户体验，让常用操作更快捷！

