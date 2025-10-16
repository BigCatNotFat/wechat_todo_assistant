# 常见问题 FAQ

## 安装和部署

### Q1: 如何安装依赖？

```bash
pip install -r requirements.txt
```

如果遇到安装问题，可以尝试：
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

### Q2: 提示缺少某个模块怎么办？

首先确认虚拟环境已激活，然后重新安装依赖：
```bash
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### Q3: 数据库如何初始化？

首次运行时会自动创建数据库表。如需手动初始化：
```python
from app import create_app
from app.database.db import db

app = create_app()
with app.app_context():
    db.create_all()
```

### Q4: 如何更换数据库？

在 `.env` 文件中修改 `DATABASE_URL`:

```env
# SQLite (默认)
DATABASE_URL=sqlite:///instance/app.db

# MySQL
DATABASE_URL=mysql+pymysql://user:pass@localhost/dbname

# PostgreSQL
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

## 微信配置

### Q5: 微信服务器验证失败？

1. 检查Token是否与配置文件一致
2. 确认服务器可以从公网访问
3. 查看服务器日志：`tail -f logs/app.log`
4. 使用微信提供的"接口调试工具"测试

### Q6: 消息解密失败怎么办？

1. 确认 `WECHAT_AES_KEY` 配置正确（43位字符）
2. 确认 `WECHAT_APP_ID` 正确
3. 确认消息加解密方式选择"安全模式"
4. 查看错误日志获取详细信息

### Q7: 收不到微信消息？

1. 检查服务器是否正常运行
2. 查看微信公众平台的"接口报警"
3. 确认URL配置正确
4. 测试服务器是否可访问：`curl http://your-domain.com/zaiban`

### Q8: 如何获取微信AppSecret？

1. 登录微信公众平台
2. 进入「开发 - 基本配置」
3. 点击"重置"按钮
4. 扫码验证后即可查看

## 大模型配置

### Q9: 支持哪些大模型？

支持所有兼容OpenAI API的模型：
- OpenAI GPT系列
- 智谱GLM
- 通义千问
- 文心一言
- Claude (通过中转)
- 本地部署的模型 (如Ollama)

### Q10: 如何配置智谱GLM？

```env
LLM_API_KEY=your_zhipu_api_key
LLM_API_BASE=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-4
```

### Q11: 如何配置通义千问？

```env
LLM_API_KEY=your_qwen_api_key
LLM_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus
```

### Q12: 大模型调用失败怎么办？

1. 检查API Key是否有效
2. 确认余额充足
3. 检查API Base URL是否正确
4. 查看错误日志：模型名称、网络连接等
5. 尝试降低 `LLM_TEMPERATURE` 或 `LLM_MAX_TOKENS`

### Q13: Function Calling不工作？

1. 确认使用的模型支持Function Calling
2. 检查 `llm_tools.py` 中的函数Schema格式
3. 查看日志中是否有函数调用记录
4. 测试简单的指令，如"添加任务：测试"

## 功能问题

### Q14: 定时任务不执行？

1. 检查服务器时区设置：`date`
2. 确认 `SCHEDULER_TIMEZONE` 配置正确
3. 查看日志是否有调度器启动信息
4. 手动触发测试：
   ```python
   from app import create_app
   app = create_app()
   with app.app_context():
       app.planning_service.send_daily_plan_to_all_users()
   ```

### Q15: 如何修改每日推送时间？

在 `config.py` 中修改：
```python
DAILY_REPORT_TIME = '08:30'  # 改为8:30
```

### Q16: 待办事项保存失败？

1. 检查数据库连接
2. 查看是否有权限问题
3. 检查磁盘空间
4. 查看错误日志

### Q17: 如何导出待办数据？

使用数据库工具或脚本：
```python
from app import create_app
from app.models import TodoItem
import json

app = create_app()
with app.app_context():
    todos = TodoItem.query.all()
    data = [todo.to_dict() for todo in todos]
    with open('todos_backup.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

## 性能和优化

### Q18: 响应速度慢怎么办？

1. 检查大模型API响应时间
2. 优化数据库查询（添加索引）
3. 使用缓存（Redis）
4. 增加Gunicorn worker数量
5. 考虑使用更快的模型

### Q19: 如何提高并发能力？

1. 增加worker数量：
   ```bash
   gunicorn -w 8 -b 0.0.0.0:8000 run:app
   ```
2. 使用异步worker：
   ```bash
   gunicorn -k gevent -w 4 run:app
   ```
3. 使用负载均衡
4. 数据库连接池配置

### Q20: 内存占用过高？

1. 减少Gunicorn worker数量
2. 使用更轻量的模型
3. 定期重启服务
4. 检查是否有内存泄漏

## 错误排查

### Q21: 运行时报错 "No module named 'xxx'"？

```bash
pip install xxx
# 或重新安装所有依赖
pip install -r requirements.txt
```

### Q22: 数据库错误 "database is locked"？

SQLite在高并发时可能出现。解决方案：
1. 使用PostgreSQL或MySQL
2. 减少并发写操作
3. 增加超时时间

### Q23: 端口已被占用？

```bash
# 查看占用端口的进程
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# 结束进程或更换端口
```

### Q24: ImportError: cannot import name 'db'？

可能是循环导入问题，检查：
1. `app/database/db.py` 是否正确
2. 模型文件中的导入顺序
3. 重启Python解释器

## 开发相关

### Q25: 如何调试代码？

1. 开启DEBUG模式：
   ```python
   DEBUG = True  # config.py
   ```
2. 使用print或logging查看日志
3. 使用IDE断点调试
4. 使用 `python -m pdb run.py` 命令行调试

### Q26: 如何添加新功能？

1. 在 `llm_tools.py` 定义函数和Schema
2. 在相应Service中实现逻辑
3. 更新提示词
4. 测试功能

### Q27: 如何修改提示词？

编辑 `prompts/prompts.yml` 文件，系统会自动加载。

### Q28: 如何贡献代码？

1. Fork项目
2. 创建功能分支
3. 提交代码
4. 发起Pull Request

## 安全问题

### Q29: 如何保护API密钥？

1. 使用 `.env` 文件，不提交到Git
2. 生产环境使用环境变量
3. 定期更换密钥
4. 使用密钥管理服务

### Q30: 数据会泄露吗？

1. 所有数据本地存储
2. 微信通信使用AES加密
3. 建议使用HTTPS
4. 定期备份数据

## 其他

### Q31: 可以商用吗？

请查看LICENSE文件。建议：
1. 遵守微信公众平台规范
2. 遵守大模型API使用协议
3. 注意用户隐私保护

### Q32: 如何获取帮助？

1. 查看文档：README.md, USAGE.md
2. 搜索已有Issue
3. 提交新Issue
4. 联系开发者

### Q33: 项目更新频率？

根据需求和反馈不定期更新。建议：
1. Star项目关注更新
2. 定期 `git pull` 获取最新代码
3. 查看CHANGELOG

---

如果你的问题没有在这里找到答案，欢迎提Issue！

