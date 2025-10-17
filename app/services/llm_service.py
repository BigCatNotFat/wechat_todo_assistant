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
        self.support_vision = llm_config.get('support_vision', False)
        
        # 初始化客户端
        if self.use_genai_sdk and GENAI_AVAILABLE:
            # 使用 Google Genai SDK
            self.genai_client = genai.Client(api_key=config['LLM_API_KEY'])
            self.client = None
            print(f"使用 Google Genai SDK，Google Search: {'启用' if self.use_google_search else '禁用'}")
        else:
            # 使用 OpenAI SDK（兼容多种API）
            self.client = OpenAI(
                api_key=config['LLM_API_KEY'],
                base_url=config['LLM_API_BASE']
            )
            self.genai_client = None
            self.use_google_search = False  # OpenAI SDK 不支持 Google Search
            print(f"使用 OpenAI 兼容 SDK")
        
        self.model = config['LLM_MODEL']
        self.temperature = config['LLM_TEMPERATURE']
        self.max_tokens = config['LLM_MAX_TOKENS']
    
    def _chat_with_genai_sdk(self, user_id, user_message, conversation_history=None):
        """
        使用 Google Genai SDK 进行对话（支持 Google Search 和图片理解）
        
        Args:
            user_id: 用户ID
            user_message: 用户消息
            conversation_history: 对话历史（可选），可能包含图片
            
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
            
            # 构建contents列表（支持多模态）
            contents = []
            
            # 添加系统提示词
            if system_prompt:
                contents.append(system_prompt + "\n\n")
            
            # 处理对话历史（包括图片）
            has_images = False
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get('role', '')
                    content = msg.get('content', '')
                    image_data = msg.get('image_data')
                    
                    # 添加文本
                    if role == 'user':
                        contents.append(f"用户: {content}\n")
                    elif role == 'assistant':
                        contents.append(f"助手: {content}\n")
                    
                    # 如果有图片且支持vision，添加图片
                    if image_data and self.support_vision:
                        has_images = True
                        try:
                            image_part = types.Part.from_bytes(
                                data=image_data['bytes'],
                                mime_type=image_data['mime_type']
                            )
                            contents.append(image_part)
                            contents.append("[用户发送了图片]\n")
                        except Exception as e:
                            print(f"添加历史图片失败: {e}")
            
            # 添加当前用户消息
            contents.append(f"用户: {user_message}")
            
            if has_images:
                print(f"🖼️ 检测到对话历史中包含 {has_images} 张图片，将发送给模型")
            
            # 配置工具
            tools = []
            if self.use_google_search:
                # 添加 Google Search 工具
                grounding_tool = types.Tool(google_search=types.GoogleSearch())
                tools.append(grounding_tool)
            
            # 配置生成参数
            config = types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
                tools=tools if tools else None
            )
            
            # 调用 Genai API
            print(f"调用 Gemini API，模型: {self.model}，Google Search: {self.use_google_search}，Vision: {self.support_vision}")
            response = self.genai_client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config
            )
            
            # 统计 token（如果可用）
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = response.usage_metadata
                if hasattr(usage, 'prompt_token_count'):
                    total_prompt_tokens = usage.prompt_token_count
                if hasattr(usage, 'candidates_token_count'):
                    total_completion_tokens = usage.candidates_token_count
                if hasattr(usage, 'total_token_count'):
                    total_tokens = usage.total_token_count
                print(f"第1轮调用 - 输入token: {total_prompt_tokens}, 输出token: {total_completion_tokens}")
            
            # 处理回答
            answer_text = response.text
            
            # 打印 Token 统计
            print(f"=" * 50)
            print(f"本次对话Token统计:")
            print(f"  总输入token: {total_prompt_tokens}")
            print(f"  总输出token: {total_completion_tokens}")
            print(f"  总计token: {total_tokens}")
            
            # 如果启用了 Google Search，打印搜索信息
            if self.use_google_search and hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    metadata = candidate.grounding_metadata
                    print(f"\n📊 Google Search 信息:")
                    
                    # 打印搜索查询
                    if hasattr(metadata, 'web_search_queries') and metadata.web_search_queries:
                        print(f"  搜索查询: {metadata.web_search_queries}")
                    
                    # 打印来源数量
                    if hasattr(metadata, 'grounding_chunks') and metadata.grounding_chunks:
                        print(f"  参考来源数量: {len(metadata.grounding_chunks)}")
                        # 打印前3个来源
                        for i, chunk in enumerate(metadata.grounding_chunks[:3]):
                            if hasattr(chunk, 'web') and chunk.web:
                                print(f"    [{i+1}] {chunk.web.title}: {chunk.web.uri}")
            
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
            llm_tools = LLMTools(self.todo_service, user_id)
            
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

