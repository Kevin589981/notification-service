#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .base import BaseNotifier, NotificationResult


class ConsoleNotifier(BaseNotifier):
    """控制台输出通知器"""
    
    def get_name(self) -> str:
        return "控制台"
    
    def is_configured(self) -> bool:
        """检查控制台输出是否已配置"""
        return self.config_manager.get_config("CONSOLE", True)
    
    def send(self, title: str, content: str) -> NotificationResult:
        """输出到控制台"""
        if not self.is_configured():
            return self._create_error_result("控制台输出已禁用", "配置错误")
        
        try:
            # 直接输出到控制台
            print(f"{title}\n\n{content}")
            
            return self._create_success_result("控制台输出成功")
            
        except Exception as e:
            error_msg = f"控制台输出异常: {str(e)}"
            return self._create_error_result(error_msg, "控制台输出失败")