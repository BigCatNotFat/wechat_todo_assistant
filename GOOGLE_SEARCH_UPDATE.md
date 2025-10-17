
# Google Search 功能更新说明

## 更新日期
2024-10-17

## 更新内容

### ✨ 新增功能

1. **Gemini Google Search 集成**
   - 集成了 Gemini 原生的 Google Search 功能
   - AI 可以自动搜索最新的互联网信息来回答问题
   - 支持实时信息查询、事实核查等场景

2. **多 SDK 支持**
   - 支持 OpenAI SDK（用于 DeepSeek 等模型）
   - 支持 Google Genai SDK（用于 Gemini 官方 API）
   - 根据模型配置自动选择合适的 SDK

3. **搜索结果展示**
   - 显示搜索查询关键词
   - 显示参考来源数量和 URL
   - 提供完整的 grounding metadata 信息

### 📝 文件修改

#### 1. `requirements.txt`
添加了 Google Genai SDK 依赖：
```
google-genai>=0.2.0
```

#### 2. `config.py`
为每个模型配置添加了两个新字段：
- `use_google_search`: 是否启用 Google Search
- `use_genai_sdk`: 是否使用 Google Genai SDK

```python
'geminiofficial': {
    'api_key': 'YOUR_API_KEY',
    'api_base': 'https://generativelanguage.googleapis.com/v1beta/openai/',
    'model': 'gemini-2.5-pro',
    'temperature': 0.7,
    'max_tokens': 10000,
    'use_google_search': True,   # ✅ 新增
    'use_genai_sdk': True         # ✅ 新增
}
```

#### 3. `app/services/llm_service.py`
- 添加了 Google Genai SDK 导入和可用性检查
- 在 `__init__` 方法中添加了 SDK 选择逻辑
- 新增 `_chat_with_genai_sdk` 方法用于处理 Gemini API 调用
- 修改 `chat_with_function_calling` 方法以支持多 SDK
- 增强了 Token 统计功能，支持 Gemini 的 usage_metadata
- 添加了 grounding metadata 的解析和展示

### 📚 新增文件

1. **GOOGLE_SEARCH_GUIDE.md**
   - 完整的功能使用指南
   - 配置说明和示例
   - 适用场景和注意事项
   - 故障排除指南

2. **test_google_search.py**
   - Google Search 功能测试脚本
   - 支持基础测试和对比测试
   - 可交互式运行

3. **GOOGLE_SEARCH_UPDATE.md**（本文件）
   - 更新说明和总结

## 使用方法

### 快速开始

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **配置模型**
在 `config.py` 中设置：
```python
CURRENT_LLM = 'geminiofficial'
```

3. **测试功能**
```bash
python test_google_search.py
```

### 切换模式

**使用 Google Search（实时信息查询）**
```python
CURRENT_LLM = 'geminiofficial'  # 启用 Google Search
```

**使用 Function Calling（待办管理）**
```python
CURRENT_LLM = 'deepseek'  # 或 'geminihiapi'
```

## 兼容性

### ✅ 向后兼容
- 所有现有功能保持不变
- 不使用 Google Search 时行为与之前完全一致
- 可以随时在不同模型间切换

### ⚠️ 限制说明
- Google Search 仅在 `geminiofficial` 配置下可用
- 使用 Genai SDK 时暂不支持 Function Calling（待办事项管理功能）
- 建议根据使用场景选择合适的模型

## 性能影响

### Token 消耗
- 启用 Google Search 会增加 token 消耗
- 搜索结果会作为上下文加入对话
- 建议监控 API 使用量

### 响应时间
- 搜索操作会增加响应时间（通常 2-5 秒）
- 适合对实时性要求不高的查询场景

## 示例场景

### 适合使用 Google Search
```
用户: 2024年欧洲杯谁赢了？
助手: [自动搜索] 西班牙队赢得了2024年欧洲杯冠军...
```

### 适合使用 Function Calling
```
用户: 帮我添加一个待办事项：明天下午3点开会
助手: [调用函数] 好的，我已经为你添加了待办事项...
```

## 技术细节

### SDK 选择逻辑
```python
if use_genai_sdk and GENAI_AVAILABLE:
    # 使用 Google Genai SDK
    self.genai_client = genai.Client(api_key=api_key)
else:
    # 使用 OpenAI SDK
    self.client = OpenAI(api_key=api_key, base_url=base_url)
```

### Google Search 工具配置
```python
grounding_tool = types.Tool(
    google_search=types.GoogleSearch()
)

config = types.GenerateContentConfig(
    tools=[grounding_tool],
    temperature=0.7,
    max_output_tokens=10000
)
```

### Grounding Metadata 结构
```python
{
    'web_search_queries': ['搜索查询1', '搜索查询2'],
    'grounding_chunks': [
        {'web': {'uri': 'https://...', 'title': '网站标题'}}
    ],
    'grounding_supports': [...]
}
```

## 安全性

- API Key 保存在配置文件中，请勿提交到版本控制
- 建议使用环境变量存储敏感信息
- 生产环境应使用 `ProductionConfig` 并设置合适的权限

## 监控建议

1. **Token 使用量监控**
   - 控制台会输出每次调用的 token 统计
   - 建议设置月度预算提醒

2. **错误日志**
   - 所有 API 错误会输出到控制台
   - 建议配置日志文件进行持久化

3. **性能指标**
   - 响应时间
   - 搜索成功率
   - Token 效率比

## 未来计划

- [ ] 支持 Function Calling 与 Google Search 同时使用
- [ ] 添加搜索结果缓存
- [ ] 优化 token 使用效率
- [ ] 添加更多搜索配置选项
- [ ] 支持自定义搜索范围

## 问题反馈

如遇到问题，请检查：
1. 是否正确安装了 `google-genai` 包
2. 是否使用了 `geminiofficial` 配置
3. API Key 是否有效
4. 网络连接是否正常

## 相关文档

- [完整使用指南](GOOGLE_SEARCH_GUIDE.md)
- [测试脚本说明](test_google_search.py)
- [项目使用文档](USAGE.md)
- [Google Genai API 文档](https://ai.google.dev/gemini-api/docs)

---

**版本**: 1.0.0  
**更新日期**: 2024-10-17  
**作者**: AI Assistant

