# -*- coding: utf-8 -*-
"""
系统命令服务
处理系统级别的命令（不经过LLM）
"""


class CommandService:
    """系统命令服务"""
    
    def __init__(self, conversation_service, todo_service, app_config=None, app_context=None):
        """
        初始化命令服务
        
        Args:
            conversation_service: 对话历史服务实例
            todo_service: 待办事项服务实例
            app_config: Flask 应用配置（用于模型切换）
            app_context: Flask 应用上下文（用于获取服务实例）
        """
        self.conversation_service = conversation_service
        self.todo_service = todo_service
        self.app_config = app_config
        self.app_context = app_context
        
        # 定义系统命令映射（命令名 -> 处理函数）
        self.commands = {
            'cls': self._clear_history,
            'help': self._show_help,
            '帮助': self._show_help,
            'reset': self._reset_all,
            '重置': self._reset_all,
            'stats': self._show_stats,
            '统计': self._show_stats,
            'models': self._list_models,
            'model': self._show_current_model,
            '模型': self._show_current_model,
            'plan': self._generate_plan,
            '规划': self._generate_plan,
        }
    
    def is_system_command(self, message):
        """
        判断是否是系统命令
        
        Args:
            message: 用户消息
            
        Returns:
            是否是系统命令
        """
        msg = message.strip().lower()
        # 支持固定命令
        if msg in self.commands:
            return True
        # 支持模型切换命令：use flash, use pro, use promax 等
        if msg.startswith('use '):
            return True
        # 支持中文模型切换命令
        if msg.startswith('切换') or msg.startswith('使用'):
            return True
        return False
    
    def execute_command(self, message, user_id):
        """
        执行系统命令
        
        Args:
            message: 用户消息
            user_id: 用户ID
            
        Returns:
            命令执行结果（文本）
        """
        command = message.strip().lower()
        
        # 处理模型切换命令
        if command.startswith('use '):
            model_name = command[4:].strip()
            return self._switch_model(user_id, model_name)
        
        if command.startswith('切换') or command.startswith('使用'):
            # 提取模型名称
            model_name = command.replace('切换', '').replace('使用', '').strip()
            return self._switch_model(user_id, model_name)
        
        # 处理固定命令
        if command in self.commands:
            try:
                return self.commands[command](user_id)
            except Exception as e:
                print(f"执行命令 '{command}' 失败: {e}")
                import traceback
                traceback.print_exc()
                return f"[sys] ❌ 命令执行失败：{str(e)}"
        return None
    
    def _clear_history(self, user_id):
        """
        清空对话历史
        
        Args:
            user_id: 用户ID
            
        Returns:
            执行结果
        """
        cleared_count = self.conversation_service.clear_user_history(user_id)
        return f"[sys] ✅ 已清空对话历史！\n共清除了 {cleared_count} 条记录。"
    
    def _show_help(self, user_id):
        """
        显示帮助信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            帮助文本
        """
        help_text = """[sys] 📖 系统命令帮助

🔧 系统命令（直接输入即可）：
• cls - 清空对话历史
• help / 帮助 - 显示此帮助信息
• stats / 统计 - 查看统计信息
• reset / 重置 - 重置所有数据（慎用）
• plan / 规划 - 生成今明两天的任务规划

🤖 模型管理：
• models - 查看所有可用模型
• model / 模型 - 查看当前模型
• use <模型> - 切换模型（如: use promax）
• 切换/使用 <模型> - 切换模型（中文）

💡 使用提示：
直接和我说话，我会帮你管理待办事项！
例如：
• "明天下午开会"
• "查看我的待办"
• "完成第一个任务"
"""
        return help_text
    
    def _reset_all(self, user_id):
        """
        重置所有数据（慎用）
        
        Args:
            user_id: 用户ID
            
        Returns:
            执行结果
        """
        # 清空对话历史
        history_count = self.conversation_service.clear_user_history(user_id)
        
        # 删除所有待办事项
        todos = self.todo_service.get_user_todos(user_id)
        todo_count = len(todos)
        for todo in todos:
            self.todo_service.delete_todo(todo.id, user_id)
        
        return f"""[sys] ⚠️ 已重置所有数据！

清除内容：
• 对话历史：{history_count} 条
• 待办事项：{todo_count} 个

现在可以重新开始使用了！"""
    
    def _show_stats(self, user_id):
        """
        显示统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            统计信息文本
        """
        # 获取对话历史数量
        conversation_history = self.conversation_service.get_recent_history(user_id)
        history_count = len(conversation_history)
        
        # 获取待办事项统计
        all_todos = self.todo_service.get_user_todos(user_id)
        pending_todos = self.todo_service.get_user_todos(user_id, status='pending')
        completed_todos = self.todo_service.get_user_todos(user_id, status='completed')
        
        # 计算完成率
        completion_rate = 0
        if len(all_todos) > 0:
            completion_rate = (len(completed_todos) / len(all_todos)) * 100
        
        stats_text = f"""[sys] 📊 数据统计

💬 对话数据：
• 历史对话：{history_count} 条

✅ 待办数据：
• 总计：{len(all_todos)} 个
• 待完成：{len(pending_todos)} 个
• 已完成：{len(completed_todos)} 个
• 完成率：{completion_rate:.1f}%

🎯 继续加油！"""
        
        return stats_text
    
    def _list_models(self, user_id):
        """
        列出所有可用的模型
        
        Args:
            user_id: 用户ID
            
        Returns:
            模型列表文本
        """
        if not self.app_config:
            return "[sys] ❌ 无法访问配置"
        
        available_models = self.app_config.get('LLM_MODELS', {})
        current_model = self.app_config.get('CURRENT_LLM', 'unknown')
        
        model_list = "[sys] 🤖 可用模型列表\n\n"
        
        for model_key, model_config in available_models.items():
            model_name = model_config.get('model', 'unknown')
            use_search = "✅" if model_config.get('use_google_search', False) else "❌"
            thinking_budget = model_config.get('thinking_budget')
            
            # 标记当前使用的模型
            current_mark = "👉 " if model_key == current_model else "   "
            
            # 构建描述
            desc_parts = [f"模型: {model_name}"]
            desc_parts.append(f"搜索: {use_search}")
            
            if thinking_budget is not None:
                if thinking_budget == -1:
                    desc_parts.append("思考: 动态")
                elif thinking_budget == 0:
                    desc_parts.append("思考: 关闭")
                else:
                    desc_parts.append(f"思考: {thinking_budget}")
            
            model_list += f"{current_mark}• {model_key}\n"
            model_list += f"   {' | '.join(desc_parts)}\n\n"
        
        model_list += "💡 使用方法：\n"
        model_list += "• 输入 'use flash' 切换到 flash 模型\n"
        model_list += "• 输入 'use promax' 切换到 promax 模型\n"
        model_list += "• 或使用完整名称，如 'use geminiofficial-pro'"
        
        return model_list
    
    def _show_current_model(self, user_id):
        """
        显示当前使用的模型
        
        Args:
            user_id: 用户ID
            
        Returns:
            当前模型信息
        """
        if not self.app_config:
            return "[sys] ❌ 无法访问配置"
        
        current_model_key = self.app_config.get('CURRENT_LLM', 'unknown')
        available_models = self.app_config.get('LLM_MODELS', {})
        
        if current_model_key not in available_models:
            return f"[sys] ⚠️ 当前模型: {current_model_key} (配置不存在)"
        
        model_config = available_models[current_model_key]
        model_name = model_config.get('model', 'unknown')
        use_search = "已启用" if model_config.get('use_google_search', False) else "未启用"
        thinking_budget = model_config.get('thinking_budget')
        
        info = f"[sys] 🤖 当前使用的模型\n\n"
        info += f"• 配置名: {current_model_key}\n"
        info += f"• 模型: {model_name}\n"
        info += f"• 网络搜索: {use_search}\n"
        
        if thinking_budget is not None:
            if thinking_budget == -1:
                info += f"• 思考模式: 动态思考\n"
            elif thinking_budget == 0:
                info += f"• 思考模式: 已关闭\n"
            else:
                info += f"• 思考预算: {thinking_budget} tokens\n"
        
        info += "\n💡 输入 'models' 查看所有可用模型"
        
        return info
    
    def _switch_model(self, user_id, model_identifier):
        """
        切换模型
        
        Args:
            user_id: 用户ID
            model_identifier: 模型标识符（可以是简称或完整名称）
            
        Returns:
            切换结果
        """
        if not self.app_config or not self.app_context:
            return "[sys] ❌ 模型切换功能不可用"
        
        available_models = self.app_config.get('LLM_MODELS', {})
        
        # 模型简称映射
        model_shortcuts = {
            'flash': 'geminiofficial-flash',
            'pro': 'geminiofficial-pro',
            'promax': 'geminiofficial-promax',
            'deepseek': 'deepseek',
            'hiapi': 'geminihiapi'
        }
        
        # 尝试匹配简称或完整名称
        target_model = None
        if model_identifier in model_shortcuts:
            target_model = model_shortcuts[model_identifier]
        elif model_identifier in available_models:
            target_model = model_identifier
        
        # 如果没有找到，尝试模糊匹配
        if not target_model:
            for key in available_models.keys():
                if model_identifier in key.lower():
                    target_model = key
                    break
        
        if not target_model or target_model not in available_models:
            return f"[sys] ❌ 未找到模型: {model_identifier}\n\n💡 输入 'models' 查看可用模型"
        
        # 检查是否已经是当前模型
        current_model = self.app_config.get('CURRENT_LLM')
        if target_model == current_model:
            return f"[sys] ℹ️ 已经在使用 {target_model} 模型"
        
        try:
            # 更新配置
            self.app_config['CURRENT_LLM'] = target_model
            
            # 重新加载模型参数
            model_config = available_models[target_model]
            self.app_config['LLM_API_KEY'] = model_config['api_key']
            self.app_config['LLM_API_BASE'] = model_config['api_base']
            self.app_config['LLM_MODEL'] = model_config['model']
            self.app_config['LLM_TEMPERATURE'] = model_config['temperature']
            self.app_config['LLM_MAX_TOKENS'] = model_config['max_tokens']
            
            # 重新初始化 LLM 服务
            from app.services.llm_service import LLMService
            
            llm_service = LLMService(
                self.app_config,
                self.app_context.prompt_manager,
                self.app_context.todo_service,
                self.app_context.transaction_service  # 传递记账服务
            )
            
            # 更新应用上下文中的 llm_service
            self.app_context.llm_service = llm_service
            
            # 构建切换成功消息
            model_name = model_config.get('model', target_model)
            use_search = "✅" if model_config.get('use_google_search', False) else "❌"
            thinking_budget = model_config.get('thinking_budget')
            
            result = f"[sys] ✅ 已切换到模型: {target_model}\n\n"
            result += f"• 模型: {model_name}\n"
            result += f"• 搜索: {use_search}\n"
            
            if thinking_budget is not None:
                if thinking_budget == -1:
                    result += f"• 思考: 动态\n"
                elif thinking_budget == 0:
                    result += f"• 思考: 关闭\n"
                else:
                    result += f"• 思考: {thinking_budget} tokens\n"
            
            print(f"✅ 用户 {user_id} 切换模型: {current_model} -> {target_model}")
            
            return result
            
        except Exception as e:
            print(f"❌ 切换模型失败: {e}")
            import traceback
            traceback.print_exc()
            return f"[sys] ❌ 切换模型失败：{str(e)}"
    
    def _generate_plan(self, user_id):
        """
        生成任务规划
        
        Args:
            user_id: 用户ID
            
        Returns:
            规划文本
        """
        if not self.app_context:
            return "[sys] ❌ 规划功能不可用"
        
        try:
            # 导入必要的模块
            from datetime import datetime, timedelta
            import pytz
            
            # 获取北京时间
            beijing_tz = pytz.timezone('Asia/Shanghai')
            current_time = datetime.now(beijing_tz)
            
            # 获取今天和明天的任务
            today_todos = self.todo_service.get_today_todos(user_id)
            tomorrow_todos = self.todo_service.get_tomorrow_todos(user_id)
            
            # 如果没有任务，给出提示
            if not today_todos and not tomorrow_todos:
                return "[sys] 📝 您暂时没有今天和明天的待办任务，先休息一下吧！"
            
            # 构建任务详细信息
            def format_task_details(todo):
                """格式化任务详细信息"""
                details = []
                details.append(f"• 任务：{todo.content}")
                
                if todo.notes:
                    details.append(f"  备注：{todo.notes}")
                
                if todo.due_date:
                    due_str = todo.due_date.strftime('%Y-%m-%d %H:%M')
                    # 计算距离现在的时间
                    time_diff = todo.due_date - datetime.now()
                    hours = int(time_diff.total_seconds() / 3600)
                    if hours < 0:
                        details.append(f"  截止时间：{due_str} (已超时 {abs(hours)} 小时)")
                    elif hours < 24:
                        details.append(f"  截止时间：{due_str} (剩余 {hours} 小时)")
                    else:
                        days = int(hours / 24)
                        details.append(f"  截止时间：{due_str} (剩余 {days} 天)")
                
                created_str = todo.created_at.strftime('%Y-%m-%d %H:%M')
                details.append(f"  创建时间：{created_str}")
                
                return "\n".join(details)
            
            # 格式化今天的任务
            today_text = ""
            if today_todos:
                today_text = f"【今天的待办】(共{len(today_todos)}个)\n"
                today_text += "\n".join([format_task_details(todo) for todo in today_todos])
            else:
                today_text = "【今天的待办】\n无"
            
            # 格式化明天的任务
            tomorrow_text = ""
            if tomorrow_todos:
                tomorrow_text = f"【明天的待办】(共{len(tomorrow_todos)}个)\n"
                tomorrow_text += "\n".join([format_task_details(todo) for todo in tomorrow_todos])
            else:
                tomorrow_text = "【明天的待办】\n无"
            
            # 获取 llm_service 并生成规划
            llm_service = self.app_context.llm_service
            
            # 获取规划提示词
            prompt_manager = self.app_context.prompt_manager
            planning_prompt = prompt_manager.get_prompt(
                'task_planning_prompt',
                today_tasks=today_text,
                tomorrow_tasks=tomorrow_text,
                current_time=current_time.strftime('%Y年%m月%d日 %H:%M')
            )
            
            print(f"=" * 50)
            print(f"📋 生成任务规划 - 用户ID: {user_id}")
            print(f"今天任务数: {len(today_todos)}")
            print(f"明天任务数: {len(tomorrow_todos)}")
            print(f"提示词长度: {len(planning_prompt)} 字符")
            print(f"使用模型: {llm_service.model}")
            print(f"配置参数: temperature={llm_service.temperature}, max_tokens={llm_service.max_tokens}")
            print(f"=" * 50)
            
            # 调用 LLM 生成规划（不使用function calling，纯文本对话）
            # 使用 OpenAI SDK 的简单对话模式
            if llm_service.use_genai_sdk:
                # 使用 Google Genai SDK
                from google import genai
                from google.genai import types
                
                # 添加系统提示词（指导输出格式）
                system_instruction = "你是一个专业的任务规划助手，善于分析任务的轻重缓急，制定科学合理的执行计划。重要：请使用纯文本格式输出，不要使用Markdown格式（如**粗体**、*斜体*等），使用emoji和换行来组织内容。"
                
                contents = [
                    types.Content(
                        role="user",
                        parts=[types.Part(text=system_instruction + "\n\n" + planning_prompt)]
                    )
                ]
                
                # 使用当前模型的配置（从 llm_service 获取）
                generate_config = types.GenerateContentConfig(
                    temperature=llm_service.temperature,
                    max_output_tokens=llm_service.max_tokens
                )
                
                print(f"🤖 调用 Gemini API 生成任务规划...")
                response = llm_service.genai_client.models.generate_content(
                    model=llm_service.model,
                    contents=contents,
                    config=generate_config
                )
                
                print(f"📥 收到 API 响应")
                
                # 健壮地提取响应文本
                plan_text = ""
                
                # 方式1（推荐）: 直接使用 response.text 属性
                try:
                    if response and hasattr(response, 'text'):
                        plan_text = response.text
                        if plan_text:
                            print(f"   ✓ 使用 response.text 成功获取内容")
                except Exception as e:
                    print(f"   ✗ 访问 response.text 失败: {e}")
                
                # 方式2: 如果方式1失败，从 candidates 中提取
                if not plan_text:
                    print(f"   → 尝试从 candidates 中提取...")
                    if response and hasattr(response, 'candidates') and response.candidates:
                        print(f"   ✓ 响应包含 {len(response.candidates)} 个候选项")
                        candidate = response.candidates[0]
                        
                        # 检查是否有 finish_reason（可能被安全过滤器阻止）
                        if hasattr(candidate, 'finish_reason'):
                            print(f"   ✓ 完成原因: {candidate.finish_reason}")
                        
                        if hasattr(candidate, 'content') and candidate.content:
                            print(f"   ✓ 候选项包含内容")
                            # 检查 parts 是否存在且不为 None
                            if hasattr(candidate.content, 'parts') and candidate.content.parts:
                                print(f"   ✓ 内容包含 {len(candidate.content.parts)} 个部分")
                                for part in candidate.content.parts:
                                    if hasattr(part, 'text') and part.text:
                                        plan_text += part.text
                            else:
                                print(f"   ✗ 内容的 parts 为空或不存在")
                        else:
                            print(f"   ✗ 候选项内容为空")
                    else:
                        print(f"   ✗ 响应没有候选项")
                
                # 如果还是没有，返回默认消息
                if not plan_text:
                    plan_text = "抱歉，AI 无法生成任务规划。这可能是因为：\n1. API 响应异常\n2. 内容被安全过滤器拦截\n\n请稍后再试，或联系管理员检查日志。"
                    print(f"⚠️ 警告: 未能从响应中提取文本")
                else:
                    print(f"✅ 成功生成规划文本，长度: {len(plan_text)} 字符")
                
            else:
                # 使用 OpenAI SDK
                print(f"🤖 调用 OpenAI 兼容 API 生成任务规划...")
                response = llm_service.client.chat.completions.create(
                    model=llm_service.model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的任务规划助手，善于分析任务的轻重缓急，制定科学合理的执行计划。"},
                        {"role": "user", "content": planning_prompt}
                    ],
                    temperature=llm_service.temperature,
                    max_tokens=llm_service.max_tokens
                )
                
                plan_text = response.choices[0].message.content
                if not plan_text:
                    plan_text = "抱歉，无法生成任务规划。请稍后再试。"
                    print(f"⚠️ 警告: OpenAI 响应内容为空")
                else:
                    print(f"✅ 成功生成规划文本，长度: {len(plan_text)} 字符")
            
            # 添加系统标记
            result = f"[sys] 📋 任务规划建议\n\n{plan_text}"
            
            print(f"✅ 用户 {user_id} 生成任务规划成功")
            return result
            
        except Exception as e:
            print(f"❌ 生成任务规划失败: {e}")
            import traceback
            traceback.print_exc()
            return f"[sys] ❌ 生成规划失败：{str(e)}"
    
    def get_all_commands(self):
        """
        获取所有支持的系统命令
        
        Returns:
            命令列表
        """
        return list(self.commands.keys())

