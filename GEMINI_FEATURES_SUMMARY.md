# Gemini 功能集成总结

## 概述

本项目已成功集成 Gemini 的两大核心功能：**Google Search（实时搜索）** 和 **Vision（图片理解）**。

## 🎉 新功能一览

### 1. Google Search - 实时信息搜索

✨ **功能特点**：
- 自动判断是否需要搜索
- 获取最新互联网信息
- 显示信息来源和引用
- 综合多个来源给出答案

📚 **详细文档**：[GOOGLE_SEARCH_GUIDE.md](GOOGLE_SEARCH_GUIDE.md)

### 2. Vision - 图片理解

✨ **功能特点**：
- 识别图片中的物体、场景
- OCR 文字识别
- 图片智能问答
- 多轮图片对话

📚 **详细文档**：[VISION_GUIDE.md](VISION_GUIDE.md)

### 3. Token 统计

✨ **功能特点**：
- 实时统计每次对话的 token 使用量
- 分别显示输入和输出 token
- 支持多轮对话的累计统计

## 📊 功能对比表

| 功能 | geminiofficial | deepseek | geminihiapi |
|------|----------------|----------|-------------|
| **Google Search** | ✅ | ❌ | ❌ |
| **图片理解** | ✅ | ❌ | ❌ |
| **Function Calling** | ❌ | ✅ | ✅ |
| **待办管理** | ❌ | ✅ | ✅ |
| **Token 统计** | ✅ | ✅ | ✅ |
| **对话历史** | ✅ | ✅ | ✅ |
| **成本** | 中 | 低 | 低 |
| **响应速度** | 中 | 快 | 快 |

## 🚀 快速开始

### 步骤 1: 安装依赖

```bash
pip install -r requirements.txt
```

### 步骤 2: 选择配置

在 `config.py` 中设置：

```python
# 使用 Gemini 全功能（搜索+图片）
CURRENT_LLM = 'geminiofficial'

# 或使用待办管理功能
CURRENT_LLM = 'deepseek'  # 或 'geminihiapi'
```

### 步骤 3: 启动服务

```bash
python run.py
```

## 💡 使用场景推荐

### 场景 1: 信息查询 + 图片识别

**配置**: `geminiofficial`

**示例**：
```
用户: [发送美食图片]
用户: 这是什么菜？怎么做？

AI: [识别图片] 这是宫保鸡丁
    [搜索网络] 制作方法：...
```

### 场景 2: 日常待办管理

**配置**: `deepseek` 或 `geminihiapi`

**示例**：
```
用户: 明天下午3点开会
AI: [添加待办] ✅ 已为你添加待办事项...

用户: 查看待办
AI: [查询数据库] 你的待办事项：...
```

### 场景 3: 灵活切换

根据需要在配置文件中切换模型：

```python
# 早上查资讯 → geminiofficial
CURRENT_LLM = 'geminiofficial'

# 工作时管理任务 → deepseek
CURRENT_LLM = 'deepseek'
```

## 🔧 技术架构

### 多 SDK 支持

```python
if use_genai_sdk:
    # Google Genai SDK
    # ✅ 支持 Google Search
    # ✅ 支持 Vision
    client = genai.Client(api_key=api_key)
else:
    # OpenAI Compatible SDK
    # ✅ 支持 Function Calling
    client = OpenAI(api_key=api_key, base_url=base_url)
```

### 对话历史管理

```python
{
    "role": "user",
    "content": "文字内容",
    "image_data": {           # 可选
        "bytes": b"...",
        "mime_type": "image/jpeg"
    },
    "timestamp": datetime(...)
}
```

- 最多保留 10 轮对话
- 24 小时内有效
- 自动清理过期记录

## 📈 Token 使用参考

### 普通对话
```
输入: ~100-300 tokens
输出: ~50-200 tokens
总计: ~150-500 tokens
```

### 带 Google Search
```
输入: ~300-800 tokens  (包含搜索结果)
输出: ~100-300 tokens
总计: ~400-1100 tokens
```

### 带图片理解
```
输入: ~500-2000 tokens  (包含图片)
输出: ~100-400 tokens
总计: ~600-2400 tokens
```

### 图片 + 搜索
```
输入: ~800-3000 tokens
输出: ~150-500 tokens
总计: ~950-3500 tokens
```

## 📱 微信使用示例

### Google Search 示例

```
用户: 2024年诺贝尔物理学奖得主是谁？

AI: [自动搜索]
==================================================
本次对话Token统计:
  总输入token: 245
  总输出token: 125
  总计token: 370

📊 Google Search 信息:
  搜索查询: ['2024诺贝尔物理学奖得主']
  参考来源数量: 3
    [1] nobelprize.org: https://...
    [2] bbc.com: https://...
==================================================

2024年诺贝尔物理学奖授予...
```

### Vision 示例

```
用户: [发送食物图片]

AI: ✅ 收到图片！请继续发送您的问题...

用户: 这是什么菜？营养价值如何？

AI: [识别图片 + 搜索营养信息]
==================================================
本次对话Token统计:
  总输入token: 1250
  总输出token: 280
  总计token: 1530

🖼️ 检测到对话历史中包含 True 张图片
📊 Google Search 信息:
  搜索查询: ['宫保鸡丁营养价值']
==================================================

这是一道宫保鸡丁。营养价值：...
```

## 🎯 最佳实践

### ✅ 推荐做法

1. **明确使用场景**
   - 需要实时信息 → `geminiofficial`
   - 需要图片识别 → `geminiofficial`  
   - 需要任务管理 → `deepseek`/`geminihiapi`

2. **优化图片质量**
   - 清晰、光线充足
   - 大小 < 5MB
   - 主体明确

3. **具体化问题**
   - "这座建筑的历史是什么？" ✅
   - "分析一下" ❌

4. **监控 Token 使用**
   - 查看控制台统计
   - 根据预算调整使用频率

### ❌ 避免的做法

1. **不切换模型就混用功能**
   - 在 deepseek 下要求搜索 ❌
   - 在 deepseek 下发送图片 ❌

2. **发送过大的图片**
   - > 10MB 的文件 ❌

3. **模糊的问题**
   - "这是什么？"（没有上下文）❌

## 📄 完整文档索引

### 快速开始
- [Google Search 快速开始](GOOGLE_SEARCH_QUICKSTART.md)

### 详细指南
- [Google Search 完整指南](GOOGLE_SEARCH_GUIDE.md)
- [Vision 图片理解指南](VISION_GUIDE.md)

### 更新说明
- [Google Search 更新日志](GOOGLE_SEARCH_UPDATE.md)

### 测试脚本
- [test_google_search.py](test_google_search.py) - Google Search 测试

### 项目文档
- [README.md](README.md) - 项目总览
- [USAGE.md](USAGE.md) - 使用说明
- [FAQ.md](FAQ.md) - 常见问题

## 🔍 功能详情

### Google Search 工作原理

1. 用户提问
2. AI 判断是否需要搜索
3. 自动生成搜索查询
4. 执行 Google 搜索
5. 处理搜索结果
6. 综合回答问题
7. 返回答案 + 来源

### Vision 工作原理

1. 用户发送图片
2. 下载图片（WeChat Media API）
3. 保存到对话历史
4. 回复确认消息
5. 用户提问
6. 从历史提取图片
7. 发送图片+问题给 Gemini
8. 返回分析结果

## 🛠️ 配置文件说明

### config.py 结构

```python
LLM_MODELS = {
    'deepseek': {
        'use_google_search': False,
        'use_genai_sdk': False,
        'support_vision': False
    },
    'geminihiapi': {
        'use_google_search': False,
        'use_genai_sdk': False,
        'support_vision': False
    },
    'geminiofficial': {
        'use_google_search': True,   # ✅
        'use_genai_sdk': True,        # ✅
        'support_vision': True        # ✅
    }
}
```

## 💰 成本预估

### 按 Token 计费（参考）

假设费率：$0.002 / 1K tokens（Gemini Pro）

**日常对话** (500 tokens/次)
- 100 次/天 = 50K tokens = $0.10

**带搜索** (1000 tokens/次)
- 50 次/天 = 50K tokens = $0.10

**带图片** (2000 tokens/次)
- 30 次/天 = 60K tokens = $0.12

**图片+搜索** (3000 tokens/次)
- 20 次/天 = 60K tokens = $0.12

**月度预估** (混合使用)
- 约 $5-15/月（轻度使用）
- 约 $15-50/月（中度使用）
- 约 $50-150/月（重度使用）

## ⚠️ 注意事项

1. **API Key 安全**
   - 不要提交到 Git
   - 使用环境变量
   - 定期轮换

2. **Token 限制**
   - 注意月度配额
   - 设置预算提醒
   - 监控使用量

3. **功能限制**
   - Google Search 和 Function Calling 不能同时使用
   - 图片功能仅限 geminiofficial
   - 微信图片有大小限制

4. **网络要求**
   - 需要访问 Google API
   - 稳定的网络连接
   - 可能需要代理

## 🐛 故障排除

### 问题 1: Google Search 不工作

**检查**：
- `CURRENT_LLM = 'geminiofficial'`
- `use_google_search: True`
- API Key 有效
- 网络可访问 Google

### 问题 2: 图片无法识别

**检查**：
- `CURRENT_LLM = 'geminiofficial'`
- `support_vision: True`
- 图片格式支持
- 图片大小 < 10MB

### 问题 3: Token 消耗过快

**解决**：
- 压缩图片
- 减少搜索频率
- 清理对话历史
- 使用更便宜的模型

## 📞 技术支持

如遇到问题：

1. 查看控制台日志
2. 阅读相关文档
3. 检查配置文件
4. 查看 FAQ.md

## 🎊 总结

通过集成 Google Search 和 Vision 功能，你的微信助手现在可以：

✅ 回答实时信息问题  
✅ 理解和分析图片  
✅ 管理待办事项  
✅ 智能对话记忆  
✅ 统计 Token 使用  

根据不同场景选择合适的模型，充分发挥各功能的优势！

---

**版本**: 1.0.0  
**更新日期**: 2024-10-17  
**维护者**: AI Assistant

