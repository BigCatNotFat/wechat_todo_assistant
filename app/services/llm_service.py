# -*- coding: utf-8 -*-
"""
大模型服务
处理与大语言模型的交互，包括Function Calling
"""
import json
from openai import OpenAI
from app.utils.llm_tools import TOOLS_SCHEMA, LLMTools

# Google Genai SDK (用于Gemini Google Search)
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("警告: google-genai SDK 未安装，Gemini Google Search 功能将不可用")


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
        
        # 获取当前模型配置
        current_llm = config['CURRENT_LLM']
        llm_config = config['LLM_MODELS'][current_llm]
        
        # 判断是否使用 Google Genai SDK
        self.use_genai_sdk = llm_config.get('use_genai_sdk', False)
        self.use_google_search = llm_config.get('use_google_search', False)
        
        # 初始化主模型客户端
        if self.use_genai_sdk and GENAI_AVAILABLE:
            # 使用 Google Genai SDK
            self.genai_client = genai.Client(api_key=config['LLM_API_KEY'])
            self.client = None
            print(f"✅ 使用 Google Genai SDK - 主模型: {config['LLM_MODEL']}")
        else:
            # 使用 OpenAI SDK（兼容多种API）
            self.client = OpenAI(
                api_key=config['LLM_API_KEY'],
                base_url=config['LLM_API_BASE']
            )
            self.genai_client = None
            print(f"✅ 使用 OpenAI 兼容 SDK - 主模型: {config['LLM_MODEL']}")
        
        self.model = config['LLM_MODEL']
        self.temperature = config['LLM_TEMPERATURE']
        self.max_tokens = config['LLM_MAX_TOKENS']
        
        # 初始化独立的搜索客户端（如果主模型启用了搜索功能）
        self.search_client = None
        self.search_model = None
        self.search_temperature = None
        
        if self.use_google_search and GENAI_AVAILABLE:
            # 从配置中获取搜索模型参数
            search_config = config.get('SEARCH_MODEL_CONFIG', {})
            search_api_key = search_config.get('api_key')
            
            if search_api_key:
                # 初始化搜索专用客户端（所有参数从配置读取）
                self.search_client = genai.Client(api_key=search_api_key)
                self.search_model = search_config.get('model', 'gemini-2.0-flash-exp')
                self.search_temperature = search_config.get('temperature', 0.7)  # 如果配置中没有，默认0.7
                print(f"🔍 已启用网络搜索功能 - 搜索模型: {self.search_model}, 温度: {self.search_temperature}")
            else:
                print(f"⚠️ 警告: 主模型已开启搜索功能，但未配置 SEARCH_MODEL_CONFIG")
                self.use_google_search = False
        elif self.use_google_search and not GENAI_AVAILABLE:
            print(f"⚠️ 警告: 主模型已开启搜索功能，但 google-genai SDK 未安装")
            self.use_google_search = False
    
    def _convert_openai_tools_to_genai(self, openai_tools):
        """
        将 OpenAI 格式的工具定义转换为 Google Genai SDK 格式
        
        Args:
            openai_tools: OpenAI 格式的工具列表
            
        Returns:
            Google Genai SDK 格式的函数声明列表
        """
        if not GENAI_AVAILABLE:
            return []
        
        function_declarations = []
        
        for tool in openai_tools:
            if tool.get('type') == 'function':
                func = tool['function']
                
                # 转换为 Genai 格式
                function_declaration = {
                    'name': func['name'],
                    'description': func['description'],
                    'parameters': func['parameters']
                }
                
                function_declarations.append(function_declaration)
        
        return function_declarations
    
    def _chat_with_genai_sdk(self, user_id, user_message, conversation_history=None):
        """
        使用 Google Genai SDK 进行对话（支持 Google Search 和 Function Calling）
        
        Args:
            user_id: 用户ID
            user_message: 用户消息
            conversation_history: 对话历史（可选）
            
        Returns:
            大模型的回复文本
        """
        try:
            # Token统计
            total_prompt_tokens = 0
            total_completion_tokens = 0
            total_tokens = 0
            
            # 构建系统提示词
            system_prompt = self.prompt_manager.get_prompt('system_prompt')
            
            # 构建 contents 列表（使用 types.Content 格式）
            contents = []
            
            # 添加系统提示词
            if system_prompt:
                contents.append(types.Content(
                    role="user",
                    parts=[types.Part(text=system_prompt)]
                ))
            
            # 添加对话历史
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get('role', '')
                    content = msg.get('content', '')
                    
                    # 转换角色名称
                    genai_role = "model" if role == "assistant" else "user"
                    
                    if content:
                        contents.append(types.Content(
                            role=genai_role,
                            parts=[types.Part(text=content)]
                        ))
            
            # 添加当前用户消息
            contents.append(types.Content(
                role="user",
                parts=[types.Part(text=user_message)]
            ))
            
            # 配置工具
            tools = []
            
            # 注意：Google Search 和 Function Calling 不能同时使用（API 限制）
            # 解决方案：将 Google Search 改为一个 Function Calling 函数
            
            # 添加 Function Calling 工具（包含待办管理和搜索）
            function_declarations = self._convert_openai_tools_to_genai(TOOLS_SCHEMA)
            if function_declarations:
                function_tool = types.Tool(function_declarations=function_declarations)
                tools.append(function_tool)
                print(f"✅ 已添加 {len(function_declarations)} 个函数调用工具（包含搜索功能）")
            
            # 配置生成参数
            config = types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
                tools=tools if tools else None
            )
            
            # 创建工具实例（用于执行函数调用）
            llm_tools = LLMTools(
                self.todo_service, 
                user_id,
                search_client=self.search_client,  # 传递独立的搜索客户端
                search_model=self.search_model,  # 传递搜索模型名称
                search_temperature=self.search_temperature  # 传递搜索温度参数
            )
            
            # 支持多轮函数调用（最多5轮）
            max_iterations = 5
            iteration_count = 0
            
            print(f"调用 Gemini API，模型: {self.model}，Function Calling: {len(function_declarations) > 0}")
            
            for iteration in range(max_iterations):
                iteration_count += 1
                
                # 调用 Genai API
                response = self.genai_client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=config
                )
                
                # 统计 token
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    usage = response.usage_metadata
                    if hasattr(usage, 'prompt_token_count'):
                        total_prompt_tokens += usage.prompt_token_count
                    if hasattr(usage, 'candidates_token_count'):
                        total_completion_tokens += usage.candidates_token_count
                    if hasattr(usage, 'total_token_count'):
                        total_tokens += usage.total_token_count
                    print(f"第{iteration + 1}轮调用 - 输入token: {usage.prompt_token_count}, 输出token: {usage.candidates_token_count}")
                
                # 检查是否有函数调用
                if response.candidates and response.candidates[0].content.parts:
                    has_function_call = False
                    
                    # 将模型响应添加到对话历史
                    contents.append(response.candidates[0].content)
                    
                    # 处理每个 part
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            has_function_call = True
                            function_call = part.function_call
                            
                            print(f"🔧 检测到函数调用: {function_call.name}({dict(function_call.args)})")
                            
                            # 执行函数
                            function_result = llm_tools.execute_tool_call(
                                function_call.name,
                                dict(function_call.args)
                            )
                            
                            print(f"✅ 函数执行结果: {function_result}")
                            
                            # 创建函数响应 part
                            function_response_part = types.Part.from_function_response(
                                name=function_call.name,
                                response={"result": function_result}
                            )
                            
                            # 添加函数结果到对话历史
                            contents.append(types.Content(
                                role="user",
                                parts=[function_response_part]
                            ))
                    
                    # 如果没有函数调用，说明模型已经生成了最终回答
                    if not has_function_call:
                        answer_text = response.text
                        break
                    
                    # 继续下一轮（让模型基于函数结果生成回答）
                else:
                    # 没有有效响应
                    answer_text = response.text if hasattr(response, 'text') else "抱歉，我没有理解您的问题。"
                    break
            else:
                # 达到最大迭代次数
                print(f"⚠️ 警告：达到最大函数调用迭代次数({max_iterations})，强制返回")
                answer_text = response.text if hasattr(response, 'text') else "抱歉，处理时间过长。"
            
            # 打印 Token 统计
            print(f"=" * 50)
            print(f"本次对话Token统计:")
            print(f"  总输入token: {total_prompt_tokens}")
            print(f"  总输出token: {total_completion_tokens}")
            print(f"  总计token: {total_tokens}")
            print(f"  函数调用轮次: {iteration_count}")
            print(f"=" * 50)
            
            return answer_text
            
        except Exception as e:
            print(f"Gemini API 调用失败: {e}")
            import traceback
            traceback.print_exc()
            return f"抱歉，我遇到了一些问题：{str(e)}"
    
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
        # 如果使用 Google Genai SDK，调用专门的方法
        if self.use_genai_sdk:
            return self._chat_with_genai_sdk(user_id, user_message, conversation_history)
        
        # 以下是原有的 OpenAI SDK 实现
        try:
            # Token统计
            total_prompt_tokens = 0
            total_completion_tokens = 0
            total_tokens = 0
            
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
            
            # 统计第一次调用的token
            if hasattr(response, 'usage') and response.usage:
                total_prompt_tokens += response.usage.prompt_tokens
                total_completion_tokens += response.usage.completion_tokens
                total_tokens += response.usage.total_tokens
                print(f"第1轮调用 - 输入token: {response.usage.prompt_tokens}, 输出token: {response.usage.completion_tokens}")
            
            # 创建工具实例（用于执行函数调用）
            llm_tools = LLMTools(
                self.todo_service, 
                user_id,
                search_client=self.search_client,  # 传递独立的搜索客户端
                search_model=self.search_model,  # 传递搜索模型名称
                search_temperature=self.search_temperature  # 传递搜索温度参数
            )
            
            # 支持多轮工具调用（最多5轮，防止无限循环）
            max_iterations = 5
            for iteration in range(max_iterations):
                # 处理响应
                assistant_message = response.choices[0].message
                
                # 如果大模型需要调用函数
                if assistant_message.tool_calls:
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
                    
                    # 再次调用大模型，让它基于函数结果生成回复或继续调用工具
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        tools=TOOLS_SCHEMA,
                        tool_choice="auto",
                        temperature=self.temperature,
                        max_tokens=self.max_tokens
                    )
                    
                    # 统计后续调用的token
                    if hasattr(response, 'usage') and response.usage:
                        total_prompt_tokens += response.usage.prompt_tokens
                        total_completion_tokens += response.usage.completion_tokens
                        total_tokens += response.usage.total_tokens
                        print(f"第{iteration + 2}轮调用 - 输入token: {response.usage.prompt_tokens}, 输出token: {response.usage.completion_tokens}")
                    
                    # 继续循环，检查是否还有新的工具调用
                else:
                    # 没有工具调用了，返回最终回复
                    print(f"=" * 50)
                    print(f"本次对话Token统计:")
                    print(f"  总输入token: {total_prompt_tokens}")
                    print(f"  总输出token: {total_completion_tokens}")
                    print(f"  总计token: {total_tokens}")
                    print(f"=" * 50)
                    return assistant_message.content
            
            # 达到最大迭代次数，返回最后的回复
            print(f"警告：达到最大工具调用迭代次数({max_iterations})，强制返回")
            print(f"=" * 50)
            print(f"本次对话Token统计:")
            print(f"  总输入token: {total_prompt_tokens}")
            print(f"  总输出token: {total_completion_tokens}")
            print(f"  总计token: {total_tokens}")
            print(f"=" * 50)
            return response.choices[0].message.content
            
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
            
            # 统计token使用
            if hasattr(response, 'usage') and response.usage:
                print(f"=" * 50)
                print(f"每日规划Token统计:")
                print(f"  输入token: {response.usage.prompt_tokens}")
                print(f"  输出token: {response.usage.completion_tokens}")
                print(f"  总计token: {response.usage.total_tokens}")
                print(f"=" * 50)
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"生成每日规划失败: {e}")
            return "抱歉，无法生成今日规划。"

