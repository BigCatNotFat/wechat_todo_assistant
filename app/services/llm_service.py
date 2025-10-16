# -*- coding: utf-8 -*-
"""
大模型服务
处理与大语言模型的交互，包括Function Calling
"""
import json
from openai import OpenAI
from app.utils.llm_tools import TOOLS_SCHEMA, LLMTools


class LLMService:
    """大模型服务"""
    
    def __init__(self, config, prompt_manager, todo_service):
        """
        初始化大模型服务
        
        Args:
            config: 配置对象
            prompt_manager: 提示词管理器
            todo_service: 待办事项服务
        """
        self.config = config
        self.prompt_manager = prompt_manager
        self.todo_service = todo_service
        
        # 初始化OpenAI客户端（兼容多种API）
        self.client = OpenAI(
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_API_BASE
        )
        
        self.model = config.LLM_MODEL
        self.temperature = config.LLM_TEMPERATURE
        self.max_tokens = config.LLM_MAX_TOKENS
    
    def chat_with_function_calling(self, user_id, user_message, conversation_history=None):
        """
        与大模型对话，支持Function Calling
        
        Args:
            user_id: 用户ID
            user_message: 用户消息
            conversation_history: 对话历史（可选）
            
        Returns:
            大模型的回复文本
        """
        try:
            # 构建消息列表
            messages = []
            
            # 添加系统提示词
            system_prompt = self.prompt_manager.get_prompt('system_prompt')
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # 添加对话历史（如果有）
            if conversation_history:
                messages.extend(conversation_history)
            
            # 添加用户消息
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # 调用大模型
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # 处理响应
            assistant_message = response.choices[0].message
            
            # 如果大模型需要调用函数
            if assistant_message.tool_calls:
                # 创建工具实例
                llm_tools = LLMTools(self.todo_service, user_id)
                
                # 添加助手消息到历史
                messages.append(assistant_message)
                
                # 执行所有函数调用
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"执行函数调用: {function_name}({function_args})")
                    
                    # 执行函数
                    function_result = llm_tools.execute_tool_call(function_name, function_args)
                    
                    # 添加函数结果到消息列表
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(function_result, ensure_ascii=False)
                    })
                
                # 再次调用大模型，让它基于函数结果生成回复
                second_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                
                return second_response.choices[0].message.content
            
            # 如果不需要调用函数，直接返回回复
            return assistant_message.content
            
        except Exception as e:
            print(f"大模型调用失败: {e}")
            return f"抱歉，我遇到了一些问题：{str(e)}"
    
    def generate_daily_plan(self, user_id):
        """
        生成每日任务规划
        
        Args:
            user_id: 用户ID
            
        Returns:
            规划文本
        """
        try:
            # 获取昨天完成的任务
            yesterday_todos = self.todo_service.get_yesterday_completed_todos(user_id)
            yesterday_summary = "\n".join([
                f"- {todo.content}" for todo in yesterday_todos
            ]) if yesterday_todos else "无"
            
            # 获取今天的待办任务
            today_todos = self.todo_service.get_today_todos(user_id)
            today_tasks = "\n".join([
                f"- [{todo.priority}] {todo.content}" for todo in today_todos
            ]) if today_todos else "无"
            
            # 获取规划提示词
            prompt = self.prompt_manager.get_prompt(
                'daily_planning_prompt',
                yesterday_summary=yesterday_summary,
                today_tasks=today_tasks
            )
            
            # 调用大模型生成规划
            messages = [
                {"role": "system", "content": self.prompt_manager.get_prompt('system_prompt')},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"生成每日规划失败: {e}")
            return "抱歉，无法生成今日规划。"

