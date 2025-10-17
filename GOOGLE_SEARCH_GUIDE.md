# Gemini Google Search 集成指南

## 功能概述

本应用已集成 Gemini 的原生 Google Search 功能，可以让 AI 助手在回答问题时自动搜索最新的互联网信息。

## 功能特点

- ✅ **自动搜索**：AI 会自动判断是否需要搜索
- ✅ **实时信息**：获取最新的网络数据
- ✅ **来源追溯**：显示信息来源和引用
- ✅ **智能综合**：AI 会综合多个来源给出答案

## 配置说明

### 1. 安装依赖

```bash
pip install google-genai>=0.2.0
```

### 2. 配置模型

在 `config.py` 中，Gemini 官方 API 配置已包含以下设置：

```python
'geminiofficial': {
    'api_key': 'YOUR_API_KEY',
    'api_base': 'https://generativelanguage.googleapis.com/v1beta/openai/',
    'model': 'gemini-2.5-pro',
    'temperature': 0.7,
    'max_tokens': 10000,
    'use_google_search': True,   # 启用Google搜索
    'use_genai_sdk': True         # 使用Google Genai SDK
}
```

### 3. 切换模型

在 `config.py` 中设置当前使用的模型：

```python
CURRENT_LLM = 'geminiofficial'  # 使用 Gemini 官方 API
```

## 使用方式

### 适合使用 Google Search 的场景

1. **实时信息查询**
   - "2024年欧洲杯谁赢了？"
   - "今天北京的天气如何？"
   - "最新的 Python 版本是什么？"

2. **时事新闻**
   - "最近有什么重要的科技新闻？"
   - "今天的股市行情怎么样？"

3. **事实核查**
   - "地球到月球的距离是多少？"
   - "世界上最高的建筑是什么？"

### 不适合使用 Google Search 的场景

1. **个人待办事项管理**（使用内置的 Function Calling）
   - "帮我添加一个待办事项"
   - "查看我的待办列表"

2. **对话和建议**
   - "给我一些工作建议"
   - "帮我写一封邮件"

## 响应格式

当启用 Google Search 时，控制台会显示额外的搜索信息：

```
调用 Gemini API，模型: gemini-2.5-pro，Google Search: True
第1轮调用 - 输入token: 150, 输出token: 80
==================================================
本次对话Token统计:
  总输入token: 150
  总输出token: 80
  总计token: 230

📊 Google Search 信息:
  搜索查询: ['UEFA Euro 2024 winner', 'who won euro 2024']
  参考来源数量: 3
    [1] aljazeera.com: https://...
    [2] uefa.com: https://...
    [3] bbc.com: https://...
==================================================
```

## 技术细节

### Grounding Metadata

API 返回的 `groundingMetadata` 包含：

- **webSearchQueries**: 执行的搜索查询列表
- **groundingChunks**: 信息来源（URL 和标题）
- **groundingSupports**: 答案文本与来源的映射关系
- **searchEntryPoint**: 可选的搜索入口 HTML 组件

### 与 Function Calling 的区别

| 特性 | Google Search | Function Calling |
|------|--------------|------------------|
| 用途 | 获取实时互联网信息 | 操作本地数据（待办事项等）|
| 数据源 | Google 搜索结果 | 本地数据库 |
| 响应速度 | 较慢（需要搜索） | 较快 |
| 适用场景 | 实时信息、事实查询 | 业务逻辑、数据管理 |

## 注意事项

⚠️ **重要提醒**

1. **仅 Gemini 官方 API 支持**
   - Google Search 功能只能在使用 `geminiofficial` 配置时启用
   - 使用其他模型（如 deepseek、geminihiapi）时会自动禁用此功能

2. **API 费用**
   - 使用 Google Search 可能会增加 token 消耗
   - 请注意监控 API 使用量和费用

3. **网络要求**
   - 需要能够访问 Google 服务
   - 确保网络连接稳定

4. **Function Calling 暂不支持**
   - 当前使用 Genai SDK 时，待办事项的 Function Calling 功能不可用
   - 建议根据使用场景选择合适的模型：
     - 需要搜索 → 使用 `geminiofficial`
     - 需要待办管理 → 使用 `deepseek` 或 `geminihiapi`

## 多模型切换策略

### 推荐配置

1. **日常待办管理**：使用 `deepseek` 或 `geminihiapi`
   - 支持完整的 Function Calling
   - 成本较低
   - 响应速度快

2. **需要实时信息查询**：临时切换到 `geminiofficial`
   - 启用 Google Search
   - 获取最新信息
   - 用完后切回日常模型

### 快速切换

在 `config.py` 中修改：

```python
# 待办管理模式
CURRENT_LLM = 'deepseek'

# 搜索模式  
CURRENT_LLM = 'geminiofficial'
```

## 故障排除

### 问题：Google Search 未生效

**解决方案**：
1. 检查是否使用 `geminiofficial` 模型
2. 确认 `use_google_search: True`
3. 查看控制台是否有 "使用 Google Genai SDK" 提示

### 问题：导入错误

**解决方案**：
```bash
pip install --upgrade google-genai
```

### 问题：API 调用失败

**解决方案**：
1. 检查 API Key 是否有效
2. 确认网络可以访问 Google API
3. 查看控制台错误日志

## 示例代码

### 测试 Google Search

```python
from app.services.llm_service import LLMService
from config import Config

# 使用 geminiofficial 配置
config = Config.__dict__
config['CURRENT_LLM'] = 'geminiofficial'

# 创建服务实例
llm_service = LLMService(config, prompt_manager, todo_service)

# 测试搜索功能
response = llm_service.chat_with_function_calling(
    user_id=1,
    user_message="2024年诺贝尔物理学奖颁给了谁？"
)

print(response)
```

## 更新日志

- **2024-10-17**: 初始版本，集成 Gemini Google Search 功能

## 相关文档

- [Google Genai Python SDK](https://ai.google.dev/gemini-api/docs/quickstart?lang=python)
- [Grounding with Google Search](https://ai.google.dev/gemini-api/docs/grounding)
- [项目使用指南](USAGE.md)

