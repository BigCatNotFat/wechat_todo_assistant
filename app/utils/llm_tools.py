# -*- coding: utf-8 -*-
"""
大模型Function Calling工具集
定义可供大模型调用的函数及其Schema
"""
from datetime import datetime
import difflib


# ==================== 函数Schema定义 ====================
# 这些Schema用于告诉大模型有哪些函数可以调用

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "在互联网上搜索实时信息。当用户询问实时资讯、最新事件、天气、新闻、或任何需要从网络获取最新数据的问题时调用此函数。例如：'今天天气怎么样'、'最新的新闻'、'2024年发生了什么'、'某某明星最近怎么样'等。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询关键词，应该是简洁明确的搜索词（中英文均可）。示例：'北京天气 Beijing weather'、'2024年诺贝尔奖 Nobel Prize 2024'、'最新科技新闻 latest tech news'、'特斯拉股价 Tesla stock price'、'人工智能发展趋势 AI development trends'"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_todo",
            "description": (
                "创建一个新的待办事项。当用户表达要做某事、记录某个任务时调用此函数。\n"
                "典型触发语：\n"
                "· 『我要去北京出差』\n"
                "· 『明天下午四点前把数学作业做完』\n"
                "· 『明晚 20:00 练习吉他』 等。\n"
                "· 『2小时后提醒我晾衣服』\n"
                "· 『今天完成数学作业』\n"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "待办事项的具体内容"
                    },
                    "notes": {
                        "type": "string",
                        "description": "备注信息，可选"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "截止日期，格式：YYYY-MM-DD HH:MM:SS，必填。如果用户明确指定了时间（如'今天完成数学作业'），则设置为具体时间（如2025-09-10 23:59:59）；如果用户没有明确说截止日期，则设置为'无限期'表示无限期的截止日期。"
                    }
                },
                "required": ["content", "due_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_todo_list",
            "description": "查询用户的待办事项列表。可以按状态和日期范围筛选。当用户询问特定时间的任务时，使用以下规则：1) 询问'今天'、'明天'、'本周'等相对时间时，使用date_filter参数；2) 询问'大后天'、'下周三'、'10月20号'等具体日期时，请先计算出具体日期（格式YYYY-MM-DD），然后使用specific_date参数。",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "completed", "all"],
                        "description": "状态筛选：pending(待办)、completed(已完成)、all(全部)，默认为pending"
                    },
                    "date_filter": {
                        "type": "string",
                        "enum": ["all", "today", "tomorrow", "this_week", "overdue"],
                        "description": "相对日期筛选：all(全部，默认)、today(今天)、tomorrow(明天)、this_week(本周)、overdue(已逾期)。注意：如果用户询问具体日期（如'大后天'、'10月20号'），应使用specific_date参数而非此参数。"
                    },
                    "specific_date": {
                        "type": "string",
                        "description": "指定具体日期筛选，格式为YYYY-MM-DD（如'2025-10-20'）。当用户询问'大后天'、'下周三'、'10月20号'等具体日期时使用。你需要根据当前日期计算出目标日期，然后传入此参数。例如：今天是2025-10-17，用户问'大后天'，则传入'2025-10-19'。"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_todo",
            "description": (
                "标记一个待办事项为已完成。当用户说完成了某个任务时调用。\n"
                "可通过 todo_id（精确）或关键词 query（模糊匹配标题）定位任务。\n"
                "典型触发语：\n"
                "· 『把 T0003 标记为已完成』\n"
                "· 『完成上面的任务』\n"

            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "todo_id": {
                        "type": "integer",
                        "description": "待办事项的ID"
                    },
                    "query": {
                        "type": "string",
                        "description": "用于模糊查找待办的关键词（标题中的关键短语）。当不知道todo_id时使用，例如：'开会'、'在803'、'买菜'等"
                    },
                    "completion_reflection": {
                        "type": "string",
                        "description": "完成感想，用户对完成这个任务的感受或总结，可选"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_todo",
            "description": "删除一个待办事项。当用户明确表示要删除某个任务时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "todo_id": {
                        "type": "integer",
                        "description": "待办事项的ID"
                    },
                    "query": {
                        "type": "string",
                        "description": "用于模糊查找待办的关键词（标题中的关键短语）。当不知道todo_id时使用，例如：'开会'、'在803'、'买菜'等"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_todo",
            "description": "更新待办事项的内容、备注或截止日期。",
            "parameters": {
                "type": "object",
                "properties": {
                    "todo_id": {
                        "type": "integer",
                        "description": "待办事项的ID"
                    },
                    "query": {
                        "type": "string",
                        "description": "用于模糊查找待办的关键词（标题中的关键短语）。当不知道todo_id时使用，例如：'开会'、'在803'、'买菜'等"
                    },
                    "content": {
                        "type": "string",
                        "description": "新的待办内容，可选"
                    },
                    "notes": {
                        "type": "string",
                        "description": "新的备注信息，可选"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "新的截止日期，格式：YYYY-MM-DD HH:MM:SS，可选"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "record_expense",
            "description": (
                "记录一笔支出。当用户说花了多少钱、买了什么东西时调用此函数。\n"
                "典型触发语：\n"
                "· 『今天花了50块钱买菜』\n"
                "· 『午饭花了30元』\n"
                "· 『买了一件衣服200块』\n"
                "· 『支出100元，打车费』"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "支出金额（正数）"
                    },
                    "notes": {
                        "type": "string",
                        "description": "支出说明/备注，例如：买菜、午饭、打车等"
                    }
                },
                "required": ["amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "record_income",
            "description": (
                "记录一笔收入。当用户说赚了多少钱、收到了多少钱时调用此函数。\n"
                "典型触发语：\n"
                "· 『今天收入500元』\n"
                "· 『工资到账5000』\n"
                "· 『兼职赚了200块』\n"
                "· 『收到转账1000元』"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "收入金额（正数）"
                    },
                    "notes": {
                        "type": "string",
                        "description": "收入说明/备注，例如：工资、兼职、转账等"
                    }
                },
                "required": ["amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "adjust_balance",
            "description": "矫正账户余额。当用户说要矫正余额、修正账目时调用此函数。可以输入正数或负数来调整余额。",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "矫正金额（正数表示增加，负数表示减少）"
                    },
                    "notes": {
                        "type": "string",
                        "description": "矫正原因说明"
                    }
                },
                "required": ["amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_balance",
            "description": "查询当前账户余额。当用户询问余额、还剩多少钱时调用此函数。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_transactions",
            "description": "查询记账记录。可以按类型（支出/收入/矫正）和时间范围筛选。",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_type": {
                        "type": "string",
                        "enum": ["expense", "income", "adjustment", "all"],
                        "description": "记录类型：expense(支出)、income(收入)、adjustment(矫正)、all(全部)，默认为all"
                    },
                    "days": {
                        "type": "integer",
                        "description": "查询最近N天的记录，例如7表示最近7天，不传则查询所有"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回记录数量限制，默认10条"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_financial_summary",
            "description": "获取收支汇总统计。当用户询问本月花了多少、最近收支情况时调用此函数。",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "统计最近N天，默认30天（一个月）"
                    }
                },
                "required": []
            }
        }
    }
]


# ==================== 函数实现 ====================
# 这些函数会被大模型通过Function Calling调用
# 它们会调用相应的服务层方法来执行实际操作

class LLMTools:
    """大模型工具类，封装所有可被Function Calling调用的函数"""
    
    def __init__(self, todo_service, user_id, search_client=None, search_model=None, search_temperature=None, transaction_service=None):
        """
        初始化LLM工具类
        
        Args:
            todo_service: 待办事项服务实例
            user_id: 当前用户ID
            search_client: 搜索专用的 Google Genai 客户端（可选）
            search_model: 搜索专用的模型名称（可选）
            search_temperature: 搜索模型的温度参数（可选，从配置文件读取）
            transaction_service: 记账服务实例（可选）
        """
        self.todo_service = todo_service
        self.user_id = user_id
        self.search_client = search_client
        self.search_model = search_model
        self.search_temperature = search_temperature if search_temperature is not None else 0.7
        self.transaction_service = transaction_service
    
    def search_web(self, query):
        """
        搜索网络信息（使用独立配置的搜索模型）
        
        Args:
            query: 搜索查询关键词
            
        Returns:
            搜索结果字典
        """
        try:
            # 检查是否有 search_client
            if not self.search_client:
                return {
                    "success": False,
                    "message": "搜索功能不可用，未配置搜索客户端"
                }
            
            # 导入 types
            try:
                from google.genai import types
            except ImportError:
                return {
                    "success": False,
                    "message": "搜索功能不可用，请安装 google-genai"
                }
            
            print(f"🔍 执行网络搜索: {query}")
            print(f"📌 使用搜索模型: {self.search_model}")
            
            # 使用 Google Search 工具调用搜索专用模型
            grounding_tool = types.Tool(google_search=types.GoogleSearch())
            config = types.GenerateContentConfig(
                tools=[grounding_tool],
                temperature=self.search_temperature
            )
            
            # 构建搜索提示
            search_prompt = f"请搜索并回答：{query}"
            
            response = self.search_client.models.generate_content(
                model=self.search_model,
                contents=search_prompt,
                config=config
            )
            
            # 提取搜索结果
            answer = response.text if hasattr(response, 'text') else "未找到相关信息"
            
            # 提取 grounding metadata
            sources = []
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    metadata = candidate.grounding_metadata
                    
                    # 提取来源
                    if hasattr(metadata, 'grounding_chunks') and metadata.grounding_chunks:
                        for chunk in metadata.grounding_chunks[:5]:  # 最多5个来源
                            if hasattr(chunk, 'web') and chunk.web:
                                sources.append({
                                    "title": chunk.web.title if hasattr(chunk.web, 'title') else "未知来源",
                                    "url": chunk.web.uri if hasattr(chunk.web, 'uri') else ""
                                })
            
            print(f"✅ 搜索完成，找到 {len(sources)} 个来源")
            
            # 返回简化的结果，不包含详细答案和来源（只告知AI已完成搜索）
            return {
                "success": True,
                "query": query,
                "answer": answer,  # 保留给AI使用，但不显示给用户
                "sources": sources,  # 保留给AI使用，但不显示给用户
                "message": f"已搜索：{query}",
                "for_ai_only": True  # 标记：这些信息仅供AI参考，不直接返回给用户
            }
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": f"搜索失败：{str(e)}"
            }
    
    def create_todo(self, content, notes=None, due_date=None):
        """
        创建待办事项
        
        Args:
            content: 待办内容
            notes: 备注
            due_date: 截止日期字符串
            
        Returns:
            操作结果字典
        """
        try:
            # 解析截止日期
            due_date_obj = None
            if due_date:
                try:
                    due_date_obj = datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S')
                except:
                    try:
                        due_date_obj = datetime.strptime(due_date, '%Y-%m-%d')
                    except:
                        pass
            
            todo = self.todo_service.create_todo(
                user_id=self.user_id,
                content=content,
                notes=notes,
                due_date=due_date_obj
            )
            
            return {
                "success": True,
                "message": f"已创建待办事项：{content}",
                "todo": todo.to_dict()
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"创建失败：{str(e)}"
            }
    
    def get_todo_list(self, status='pending', date_filter='all', specific_date=None):
        """
        获取待办列表（支持日期筛选和指定具体日期）
        
        Args:
            status: 状态筛选
            date_filter: 相对日期筛选（all/today/tomorrow/this_week/overdue）
            specific_date: 具体日期筛选（格式：YYYY-MM-DD）
            
        Returns:
            待办列表
        """
        try:
            # 优先处理具体日期筛选
            if specific_date:
                todos = self._filter_todos_by_specific_date(specific_date, status)
            # 其次处理相对日期筛选
            elif date_filter != 'all':
                todos = self._filter_todos_by_date_range(date_filter, status)
            else:
                # 默认：按状态筛选全部
                todos = self.todo_service.get_user_todos(
                    user_id=self.user_id,
                    status=None if status == 'all' else status
                )
            
            todo_list = [todo.to_dict() for todo in todos]
            
            return {
                "success": True,
                "count": len(todo_list),
                "todos": todo_list,
                "date_filter": date_filter,
                "specific_date": specific_date
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"查询失败：{str(e)}"
            }
    
    def _filter_todos_by_date_range(self, date_range, status='pending'):
        """
        按日期范围筛选待办事项
        
        Args:
            date_range: 日期范围（today/tomorrow/this_week/overdue）
            status: 状态筛选
            
        Returns:
            TodoItem对象列表
        """
        from datetime import datetime, timedelta
        from sqlalchemy import or_
        
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # 获取所有待办
        from app.models.todo_item import TodoItem
        query = TodoItem.query.filter_by(user_id=self.user_id)
        
        if status and status != 'all':
            query = query.filter_by(status=status)
        
        if date_range == 'today':
            # 今天的任务：
            # 1. 截止日期在今天的任务
            # 2. 逾期但未完成的任务（应该今天完成）
            # 3. 没有截止日期但今天创建的任务
            query = query.filter(
                or_(
                    # 截止日期在今天
                    (TodoItem.due_date >= today_start) & (TodoItem.due_date <= today_end),
                    # 逾期未完成
                    (TodoItem.due_date < today_start) & (TodoItem.status == 'pending'),
                    # 没有截止日期但今天创建
                    (TodoItem.due_date.is_(None)) & (TodoItem.created_at >= today_start)
                )
            )
        elif date_range == 'tomorrow':
            # 明天：due_date 在明天这一天
            tomorrow_start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow_end = tomorrow_start.replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.filter(
                TodoItem.due_date >= tomorrow_start,
                TodoItem.due_date <= tomorrow_end
            )
        elif date_range == 'this_week':
            # 本周：从今天到本周日
            days_until_sunday = 6 - now.weekday()  # weekday(): 0=周一, 6=周日
            week_end = (now + timedelta(days=days_until_sunday)).replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.filter(
                TodoItem.due_date >= today_start,
                TodoItem.due_date <= week_end
            )
        elif date_range == 'overdue':
            # 逾期：due_date < 今天开始时间，且未完成
            query = query.filter(
                TodoItem.due_date < today_start,
                TodoItem.status == 'pending'
            )
        
        return query.order_by(TodoItem.due_date.asc()).all()
    
    def _filter_todos_by_specific_date(self, target_date_str, status='pending'):
        """
        按具体日期筛选待办事项
        
        Args:
            target_date_str: 目标日期字符串（格式：YYYY-MM-DD）
            status: 状态筛选
            
        Returns:
            TodoItem对象列表
        """
        from datetime import datetime
        
        try:
            # 解析目标日期
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
            target_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            target_end = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        except ValueError:
            # 日期格式错误，返回空列表
            print(f"⚠️ 日期格式错误: {target_date_str}，应为 YYYY-MM-DD")
            return []
        
        # 获取所有待办
        from app.models.todo_item import TodoItem
        query = TodoItem.query.filter_by(user_id=self.user_id)
        
        if status and status != 'all':
            query = query.filter_by(status=status)
        
        # 筛选目标日期的任务
        query = query.filter(
            TodoItem.due_date >= target_start,
            TodoItem.due_date <= target_end
        )
        
        return query.order_by(TodoItem.due_date.asc()).all()
    
    def _fuzzy_match_todo(self, keyword, status='pending', threshold=0.3):
        """
        模糊匹配待办事项
        
        Args:
            keyword: 关键词
            status: 任务状态（默认pending）
            threshold: 相似度阈值（0-1，默认0.3）
            
        Returns:
            匹配的待办事项ID，如果没有匹配则返回None
        """
        # 获取用户的待办任务
        todos = self.todo_service.get_user_todos(
            user_id=self.user_id,
            status=status
        )
        
        if not todos:
            return None
        
        # 模糊匹配
        keyword_lower = keyword.lower().strip()
        best_todo_id = None
        best_score = 0.0
        
        for todo in todos:
            content_lower = todo.content.lower()
            # 使用 SequenceMatcher 计算相似度
            score = difflib.SequenceMatcher(None, keyword_lower, content_lower).ratio()
            
            if score > best_score:
                best_todo_id = todo.id
                best_score = score
        
        # 如果最佳匹配分数大于阈值，返回该任务ID
        if best_score >= threshold:
            return best_todo_id, best_score
        
        return None, 0.0
    
    def complete_todo(self, todo_id=None, query=None, completion_reflection=None):
        """
        完成待办事项（支持模糊匹配）
        
        Args:
            todo_id: 待办事项ID（优先使用）
            query: 任务内容关键词（用于模糊匹配，当todo_id为空时使用）
            completion_reflection: 完成感想
            
        Returns:
            操作结果
        """
        try:
            # 如果没有提供 todo_id，尝试通过 query 模糊匹配
            if todo_id is None and query:
                matched_id, score = self._fuzzy_match_todo(query)
                if matched_id:
                    todo_id = matched_id
                    print(f"✨ 模糊匹配成功: 关键词'{query}' -> 任务ID {todo_id} (相似度: {score:.2%})")
                else:
                    return {
                        "success": False,
                        "message": f"未找到与'{query}'匹配的待办任务，请提供更准确的描述或任务ID"
                    }
            
            if todo_id is None:
                return {
                    "success": False,
                    "message": "请提供任务ID或任务内容关键词"
                }
            
            # 标记任务完成
            todo = self.todo_service.mark_todo_as_complete(todo_id, self.user_id, completion_reflection)
            if todo:
                return {
                    "success": True,
                    "message": f"已完成：{todo.content}",
                    "todo": todo.to_dict()
                }
            else:
                return {
                    "success": False,
                    "message": "待办事项不存在或无权操作"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"操作失败：{str(e)}"
            }
    
    def delete_todo(self, todo_id=None, query=None):
        """
        删除待办事项
        
        Args:
            todo_id: 待办事项ID（优先使用）
            query: 任务内容关键词（用于模糊匹配，当todo_id为空时使用）
            
        Returns:
            操作结果
        """
        try:
            if todo_id is None and query:
                matched_id, score = self._fuzzy_match_todo(query)
                if matched_id:
                    todo_id = matched_id
                    print(f"✨ 模糊匹配成功: 关键词'{query}' -> 任务ID {todo_id} (相似度: {score:.2%})")
                else:
                    return {
                        "success": False,
                        "message": f"未找到与'{query}'匹配的待办任务，请提供更准确的描述或任务ID"
                    }
            
            if todo_id is None:
                return {
                    "success": False,
                    "message": "请提供任务ID或任务内容关键词"
                }
            success = self.todo_service.delete_todo(todo_id, self.user_id)
            if success:
                return {
                    "success": True,
                    "message": "已删除待办事项"
                }
            else:
                return {
                    "success": False,
                    "message": "待办事项不存在或无权操作"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"删除失败：{str(e)}"
            }
    
    def update_todo(self, todo_id=None, query=None, content=None, notes=None, due_date=None):
        """
        更新待办事项
        
        Args:
            todo_id: 待办事项ID（优先使用）
            query: 任务内容关键词（用于模糊匹配，当todo_id为空时使用）
            content: 新内容
            notes: 新备注
            due_date: 新截止日期
            
        Returns:
            操作结果
        """
        try:
            if todo_id is None and query:
                matched_id, score = self._fuzzy_match_todo(query)
                if matched_id:
                    todo_id = matched_id
                    print(f"✨ 模糊匹配成功: 关键词'{query}' -> 任务ID {todo_id} (相似度: {score:.2%})")
                else:
                    return {
                        "success": False,
                        "message": f"未找到与'{query}'匹配的待办任务，请提供更准确的描述或任务ID"
                    }
            
            if todo_id is None:
                return {
                    "success": False,
                    "message": "请提供任务ID或任务内容关键词"
                }
            # 解析截止日期
            due_date_obj = None
            if due_date:
                try:
                    due_date_obj = datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S')
                except:
                    try:
                        due_date_obj = datetime.strptime(due_date, '%Y-%m-%d')
                    except:
                        pass
            
            todo = self.todo_service.update_todo(
                todo_id=todo_id,
                user_id=self.user_id,
                content=content,
                notes=notes,
                due_date=due_date_obj
            )
            

            if todo:
                return {
                    "success": True,
                    "message": "已更新待办事项",
                    "todo": todo.to_dict()
                }
            else:
                return {
                    "success": False,
                    "message": "待办事项不存在或无权操作"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"更新失败：{str(e)}"
            }
    
    def record_expense(self, amount, notes=None):
        """
        记录支出
        
        Args:
            amount: 支出金额
            notes: 支出说明
            
        Returns:
            操作结果字典
        """
        try:
            if not self.transaction_service:
                return {
                    "success": False,
                    "message": "记账服务未初始化"
                }
            
            transaction = self.transaction_service.create_expense(
                user_id=self.user_id,
                amount=amount,
                notes=notes
            )
            
            # 获取当前余额
            balance = self.transaction_service.get_balance(self.user_id)
            
            return {
                "success": True,
                "message": f"已记录支出：{abs(transaction.amount)}元",
                "transaction": transaction.to_dict(),
                "current_balance": balance
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"记录失败：{str(e)}"
            }
    
    def record_income(self, amount, notes=None):
        """
        记录收入
        
        Args:
            amount: 收入金额
            notes: 收入说明
            
        Returns:
            操作结果字典
        """
        try:
            if not self.transaction_service:
                return {
                    "success": False,
                    "message": "记账服务未初始化"
                }
            
            transaction = self.transaction_service.create_income(
                user_id=self.user_id,
                amount=amount,
                notes=notes
            )
            
            # 获取当前余额
            balance = self.transaction_service.get_balance(self.user_id)
            
            return {
                "success": True,
                "message": f"已记录收入：{transaction.amount}元",
                "transaction": transaction.to_dict(),
                "current_balance": balance
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"记录失败：{str(e)}"
            }
    
    def adjust_balance(self, amount, notes=None):
        """
        资金矫正
        
        Args:
            amount: 矫正金额
            notes: 矫正说明
            
        Returns:
            操作结果字典
        """
        try:
            if not self.transaction_service:
                return {
                    "success": False,
                    "message": "记账服务未初始化"
                }
            
            transaction = self.transaction_service.adjust_balance(
                user_id=self.user_id,
                amount=amount,
                notes=notes
            )
            
            # 获取当前余额
            balance = self.transaction_service.get_balance(self.user_id)
            
            return {
                "success": True,
                "message": f"已矫正余额：{amount}元",
                "transaction": transaction.to_dict(),
                "current_balance": balance
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"矫正失败：{str(e)}"
            }
    
    def get_balance(self):
        """
        获取当前余额
        
        Returns:
            余额信息字典
        """
        try:
            if not self.transaction_service:
                return {
                    "success": False,
                    "message": "记账服务未初始化"
                }
            
            balance = self.transaction_service.get_balance(self.user_id)
            
            return {
                "success": True,
                "balance": balance,
                "message": f"当前余额：{balance}元"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"查询失败：{str(e)}"
            }
    
    def get_transactions(self, transaction_type='all', days=None, limit=10):
        """
        获取记账记录
        
        Args:
            transaction_type: 记录类型
            days: 最近N天
            limit: 返回数量限制
            
        Returns:
            记账记录列表
        """
        try:
            if not self.transaction_service:
                return {
                    "success": False,
                    "message": "记账服务未初始化"
                }
            
            # 如果类型是all，则传入None
            type_filter = None if transaction_type == 'all' else transaction_type
            
            transactions = self.transaction_service.get_user_transactions(
                user_id=self.user_id,
                transaction_type=type_filter,
                limit=limit,
                days=days
            )
            
            transaction_list = [t.to_dict() for t in transactions]
            
            return {
                "success": True,
                "count": len(transaction_list),
                "transactions": transaction_list,
                "transaction_type": transaction_type,
                "days": days
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"查询失败：{str(e)}"
            }
    
    def get_financial_summary(self, days=30):
        """
        获取收支汇总统计
        
        Args:
            days: 统计最近N天
            
        Returns:
            收支汇总字典
        """
        try:
            if not self.transaction_service:
                return {
                    "success": False,
                    "message": "记账服务未初始化"
                }
            
            summary = self.transaction_service.get_period_summary(
                user_id=self.user_id,
                days=days
            )
            
            # 获取当前总余额
            balance = self.transaction_service.get_balance(self.user_id)
            summary['current_balance'] = balance
            
            return {
                "success": True,
                "summary": summary,
                "message": f"最近{days}天收支汇总"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"查询失败：{str(e)}"
            }
    
    def execute_tool_call(self, function_name, arguments):
        """
        执行工具调用
        
        Args:
            function_name: 函数名
            arguments: 参数字典
            
        Returns:
            执行结果
        """
        # 获取对应的方法
        method = getattr(self, function_name, None)
        if method and callable(method):
            return method(**arguments)
        else:
            return {
                "success": False,
                "message": f"未知的函数：{function_name}"
            }

