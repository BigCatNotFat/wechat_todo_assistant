# -*- coding: utf-8 -*-
"""
提示词管理器
负责加载和管理YAML格式的提示词模板
"""
import os
import yaml
from datetime import datetime


class PromptManager:
    """提示词管理器"""
    
    def __init__(self, prompts_file_path):
        """
        初始化提示词管理器
        
        Args:
            prompts_file_path: 提示词配置文件路径
        """
        self.prompts_file_path = prompts_file_path
        self.prompts = {}
        self.load_prompts()
    
    def load_prompts(self):
        """从YAML文件加载提示词"""
        try:
            if os.path.exists(self.prompts_file_path):
                with open(self.prompts_file_path, 'r', encoding='utf-8') as f:
                    self.prompts = yaml.safe_load(f) or {}
                print(f"成功加载 {len(self.prompts)} 个提示词模板")
            else:
                print(f"警告: 提示词文件不存在: {self.prompts_file_path}")
                self.prompts = {}
        except Exception as e:
            print(f"加载提示词文件失败: {e}")
            self.prompts = {}
    
    def get_prompt(self, key, **kwargs):
        """
        获取提示词模板并填充参数
        
        Args:
            key: 提示词的键名
            **kwargs: 要填充到模板中的参数
            
        Returns:
            填充后的提示词字符串
        """
        template = self.prompts.get(key, '')
        if not template:
            print(f"警告: 未找到提示词: {key}")
            return ''
        
        try:
            # 如果是系统提示词，自动添加系统时间
            if key == 'system_prompt':
                now = datetime.now()
                kwargs.setdefault('current_time', now.strftime('%Y年%m月%d日 %H:%M:%S'))
                kwargs.setdefault('current_date', now.strftime('%Y年%m月%d日'))
                kwargs.setdefault('current_weekday', ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'][now.weekday()])
            
            # 使用format方法填充模板
            return template.format(**kwargs)
        except KeyError as e:
            print(f"提示词模板缺少参数: {e}")
            return template
        except Exception as e:
            print(f"格式化提示词失败: {e}")
            return template
    
    def reload(self):
        """重新加载提示词文件"""
        self.load_prompts()

