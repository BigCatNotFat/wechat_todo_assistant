# Google Search 快速开始

## 5分钟快速上手 Gemini Google Search

### 步骤 1: 安装依赖

```bash
pip install google-genai>=0.2.0
```

### 步骤 2: 配置模型

打开 `config.py`，确保当前使用 Gemini 官方 API：

```python
CURRENT_LLM = 'geminiofficial'  # ✅ 使用此配置
```

### 步骤 3: 测试功能

运行测试脚本：

```bash
python test_google_search.py
```

选择 `1` 进行基础测试。

### 步骤 4: 查看结果

控制台会显示类似以下输出：

```
调用 Gemini API，模型: gemini-2.5-pro，Google Search: True
第1轮调用 - 输入token: 150, 输出token: 80
==================================================
本次对话Token统计:
  总输入token: 150
  总输出token: 80
  总计token: 230

📊 Google Search 信息:
  搜索查询: ['欧洲杯2024冠军']
  参考来源数量: 3
    [1] uefa.com: https://...
    [2] bbc.com: https://...
    [3] sports.com: https://...
==================================================

【回答】:
西班牙队赢得了2024年欧洲杯冠军，他们在决赛中以2-1击败了英格兰队...
```

## 完成！🎉

现在你已经成功启用了 Google Search 功能。

## 常用命令

### 切换到搜索模式
```python
# config.py
CURRENT_LLM = 'geminiofficial'
```

### 切换到待办管理模式
```python
# config.py
CURRENT_LLM = 'deepseek'  # 或 'geminihiapi'
```

### 重启服务
```bash
python run.py
```

## 使用建议

✅ **适合搜索的问题：**
- "2024年诺贝尔奖获得者是谁？"
- "最新的 iPhone 型号是什么？"
- "今天北京的天气怎么样？"

❌ **不适合搜索的问题：**
- "帮我添加待办事项"（使用 deepseek/geminihiapi）
- "查看我的任务列表"（使用 deepseek/geminihiapi）

## 遇到问题？

### 无法搜索
- 检查 `CURRENT_LLM` 是否为 `'geminiofficial'`
- 确认已安装 `google-genai` 包

### API 错误
- 检查 API Key 是否有效
- 确认网络可以访问 Google API

### 想要更多帮助
- 查看 [完整指南](GOOGLE_SEARCH_GUIDE.md)
- 查看 [更新说明](GOOGLE_SEARCH_UPDATE.md)

---

**提示**: 建议将此文件加入书签，方便快速查阅！

