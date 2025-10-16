# -*- coding: utf-8 -*-
"""
任务规划服务
处理每日任务规划和总结
"""
from datetime import datetime


class PlanningService:
    """任务规划服务"""
    
    def __init__(self, todo_service, llm_service, wechat_service):
        """
        初始化规划服务
        
        Args:
            todo_service: 待办事项服务
            llm_service: 大模型服务
            wechat_service: 微信服务
        """
        self.todo_service = todo_service
        self.llm_service = llm_service
        self.wechat_service = wechat_service
    
    def generate_daily_plan_for_user(self, user_id):
        """
        为单个用户生成每日规划
        
        Args:
            user_id: 用户ID
            
        Returns:
            规划文本
        """
        try:
            plan = self.llm_service.generate_daily_plan(user_id)
            return plan
        except Exception as e:
            print(f"生成用户{user_id}的每日规划失败: {e}")
            return None
    
    def send_daily_plan_to_user(self, openid):
        """
        发送每日规划给用户
        
        Args:
            openid: 用户OpenID
            
        Returns:
            是否发送成功
        """
        try:
            # 获取用户
            from app.models.user import User
            user = User.query.filter_by(openid=openid).first()
            if not user:
                print(f"用户不存在: {openid}")
                return False
            
            # 生成规划
            plan = self.generate_daily_plan_for_user(user.id)
            if not plan:
                return False
            
            # 添加问候语
            greeting = f"早上好！☀️\n\n今天是 {datetime.now().strftime('%Y年%m月%d日 %A')}\n\n"
            message = greeting + plan
            
            # 发送消息
            success = self.wechat_service.send_customer_message(openid, message)
            return success
            
        except Exception as e:
            print(f"发送每日规划给{openid}失败: {e}")
            return False
    
    def send_daily_plan_to_all_users(self):
        """
        发送每日规划给所有用户
        """
        try:
            from app.models.user import User
            users = User.query.all()
            
            success_count = 0
            fail_count = 0
            
            for user in users:
                if self.send_daily_plan_to_user(user.openid):
                    success_count += 1
                else:
                    fail_count += 1
            
            print(f"每日规划推送完成: 成功{success_count}个, 失败{fail_count}个")
            
        except Exception as e:
            print(f"批量发送每日规划失败: {e}")

