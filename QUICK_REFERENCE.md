# 快速参考卡片

## 🎯 功能选择器

```
需要什么功能？
│
├─ 📱 查询实时信息（新闻、天气、事实）
│  └─> 使用 geminiofficial + Google Search
│
├─ 🖼️ 识别图片、OCR文字
│  └─> 使用 geminiofficial + Vision
│
├─ 📝 管理待办事项
│  └─> 使用 deepseek 或 geminihiapi
│
└─ 💬 普通对话
   └─> 任何模型都可以
```

## ⚙️ 配置速查

### geminiofficial（全功能）
```python
CURRENT_LLM = 'geminiofficial'
```
- ✅ Google Search（实时搜索）
- ✅ Vision（图片理解）
- ❌ Function Calling（待办管理）
- 💰 成本：中等

### deepseek（待办专用）
```python
CURRENT_LLM = 'deepseek'
```
- ❌ Google Search
- ❌ Vision
- ✅ Function Calling（待办管理）
- 💰 成本：低

### geminihiapi（待办专用）
```python
CURRENT_LLM = 'geminihiapi'
```
- ❌ Google Search
- ❌ Vision
- ✅ Function Calling（待办管理）
- 💰 成本：低

## 📋 使用示例速查

### Google Search
```
用户: 2024年奥运会在哪举办？
AI: [自动搜索] 2024年夏季奥运会在法国巴黎举办...
```

### Vision
```
用户: [发送图片]
AI: ✅ 收到图片！
用户: 这是什么？
AI: [分析图片] 这是...
```

### 待办管理
```
用户: 明天开会
AI: [添加待办] ✅ 已添加...
```

## 🔄 切换模型流程

1. 打开 `config.py`
2. 找到 `CURRENT_LLM = '...'`
3. 改成想要的模型名称
4. 重启服务：`python run.py`

## 💡 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python run.py

# 测试搜索
python test_google_search.py

# 查看日志
tail -f logs/app.log
```

## 📊 Token 消耗速查

| 场景 | 预估Token | 成本参考 |
|------|-----------|---------|
| 普通对话 | 150-500 | $0.0003-0.001 |
| +搜索 | 400-1100 | $0.0008-0.002 |
| +图片 | 600-2400 | $0.001-0.005 |
| 图片+搜索 | 950-3500 | $0.002-0.007 |

*基于 Gemini Pro $0.002/1K tokens*

## ⚡ 快捷键盘

### 微信命令
```
#清空历史    - 清除对话记录
#历史状态    - 查看历史统计
查看待办     - 查看任务列表
完成XXX     - 标记任务完成
```

## 🎨 响应格式示例

### 带搜索的响应
```
==================================================
本次对话Token统计:
  总输入token: 245
  总输出token: 125
  总计token: 370

📊 Google Search 信息:
  搜索查询: ['查询关键词']
  参考来源数量: 3
    [1] 网站名: URL
==================================================
```

### 带图片的响应
```
🖼️ 检测到对话历史中包含图片
==================================================
本次对话Token统计:
  总输入token: 1250
  总输出token: 280
  总计token: 1530
==================================================
```

## 🚨 错误码速查

| 错误信息 | 原因 | 解决方法 |
|---------|------|---------|
| "不支持图片" | 模型配置错误 | 切换到 geminiofficial |
| "搜索失败" | 网络问题 | 检查网络/API Key |
| "Token超限" | 配额用完 | 检查账户余额 |
| "下载图片失败" | 图片过大 | 压缩图片 |

## 📱 微信使用流程图

```
用户输入
   │
   ├─ 文字消息
   │  ├─ 系统命令（#开头）→ 执行命令
   │  └─ 普通对话 → 调用 LLM
   │     ├─ geminiofficial → 可能触发搜索
   │     └─ deepseek/geminihiapi → Function Calling
   │
   └─ 图片消息
      ├─ geminiofficial → 保存图片 + 回复确认
      └─ 其他模型 → 提示不支持
```

## 🔧 调试检查清单

### 搜索功能不工作
- [ ] CURRENT_LLM = 'geminiofficial'
- [ ] use_google_search = True
- [ ] API Key 有效
- [ ] 网络可访问 Google
- [ ] 查看控制台日志

### 图片功能不工作  
- [ ] CURRENT_LLM = 'geminiofficial'
- [ ] support_vision = True
- [ ] 图片 < 10MB
- [ ] 图片格式正确（jpg/png/gif）
- [ ] 查看控制台日志

### 待办功能不工作
- [ ] CURRENT_LLM = 'deepseek' 或 'geminihiapi'
- [ ] 数据库文件存在
- [ ] 查看控制台日志

## 📚 文档导航

```
快速上手
├─ QUICK_REFERENCE.md          (本文件)
├─ GOOGLE_SEARCH_QUICKSTART.md (搜索快速开始)
└─ GEMINI_FEATURES_SUMMARY.md  (功能总结)

详细指南
├─ GOOGLE_SEARCH_GUIDE.md      (搜索完整指南)
├─ VISION_GUIDE.md             (图片完整指南)
└─ USAGE.md                    (项目使用说明)

技术文档
├─ GOOGLE_SEARCH_UPDATE.md     (搜索更新说明)
├─ PROJECT_STRUCTURE.md        (项目结构)
└─ IMPLEMENTATION_SUMMARY.md   (实现总结)

测试相关
├─ test_google_search.py       (搜索测试脚本)
└─ TEST_GUIDE.md               (测试指南)
```

## 💼 场景速查表

| 我想... | 使用配置 | 发送内容 | 期望结果 |
|---------|---------|---------|---------|
| 查天气 | geminiofficial | "今天天气" | 搜索并返回天气 |
| 识别图片 | geminiofficial | [图片]+"是什么" | 分析图片内容 |
| 添加待办 | deepseek | "明天开会" | 创建待办事项 |
| 查询新闻 | geminiofficial | "最新科技新闻" | 搜索返回新闻 |
| OCR文字 | geminiofficial | [图片]+"识别文字" | 提取图片文字 |
| 查看任务 | deepseek | "查看待办" | 列出待办列表 |

## 🎓 学习路径

### 第1天：基础配置
1. 安装依赖
2. 配置 API Key
3. 选择模型
4. 启动服务

### 第2天：功能测试
1. 测试普通对话
2. 测试待办管理
3. 测试 Google Search
4. 测试图片识别

### 第3天：深入使用
1. 理解 Token 消耗
2. 优化提示词
3. 监控使用量
4. 调整配置

### 第4天：高级应用
1. 组合使用功能
2. 自定义欢迎语
3. 添加自定义命令
4. 性能优化

## 🌟 最佳实践提示

### ✅ DO
- 根据场景选择合适模型
- 定期查看 Token 使用量
- 清晰描述问题
- 保持图片清晰
- 定期清理历史

### ❌ DON'T
- 在不支持的模型上使用功能
- 发送过大图片
- 提出模糊问题
- 忽略 Token 统计
- 混用不同功能

## 🔗 快速链接

- 📖 [README](README.md) - 项目介绍
- 🚀 [QUICKSTART](QUICKSTART.md) - 快速开始
- 📊 [功能总结](GEMINI_FEATURES_SUMMARY.md) - 完整功能
- 🔍 [搜索指南](GOOGLE_SEARCH_GUIDE.md) - Google Search
- 🖼️ [图片指南](VISION_GUIDE.md) - Vision
- ❓ [FAQ](FAQ.md) - 常见问题

## 📞 获取帮助

1. 查看文档（上方链接）
2. 查看控制台日志
3. 检查配置文件
4. 重启服务尝试

---

**💡 提示**：建议收藏本页面，方便随时查阅！

