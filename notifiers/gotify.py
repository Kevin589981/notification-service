#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

from .base import BaseNotifier, NotificationResult


class GotifyNotifier(BaseNotifier):
    """Gotify 通知器"""
    
    def get_name(self) -> str:
        return "Gotify"
    
    def is_configured(self) -> bool:
        """检查 Gotify 是否已配置"""
        return bool(
            self.config_manager.get_config("GOTIFY_URL") and 
            self.config_manager.get_config("GOTIFY_TOKEN")
        )
    
    def send(self, title: str, content: str) -> NotificationResult:
        """发送 Gotify 通知"""
        if not self.is_configured():
            self._log_not_configured()
            return self._create_error_result("GOTIFY_URL 或 GOTIFY_TOKEN 未设置", "配置错误")
        
        self._log_send_attempt(title)
        
        try:
            # 构建请求 URL
            gotify_url = self.config_manager.get_config("GOTIFY_URL")
            gotify_token = self.config_manager.get_config("GOTIFY_TOKEN")
            url = f'{gotify_url}/message?token={gotify_token}'
            
            # 构建请求数据
            priority = self.config_manager.get_config("GOTIFY_PRIORITY", 0)
            data = {
                "title": title, 
                "message": content,
                "priority": priority
            }
            
            # 发送请求
            response = requests.post(url, data=data, timeout=15).json()
            
            if response.get("id"):
                self._log_send_success()
                return self._create_success_result("Gotify 推送成功")
            else:
                error_msg = "未收到有效响应"
                self._log_send_failure(error_msg)
                return self._create_error_result(error_msg, "Gotify 推送失败")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求失败: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "Gotify 推送失败")
        except Exception as e:
            error_msg = f"发送异常: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "Gotify 推送失败")