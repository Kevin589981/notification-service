#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

from .base import BaseNotifier, NotificationResult


class PushDeerNotifier(BaseNotifier):
    """PushDeer 通知器"""
    
    def get_name(self) -> str:
        return "PushDeer"
    
    def is_configured(self) -> bool:
        """检查 PushDeer 是否已配置"""
        return bool(self.config_manager.get_config("DEER_KEY"))
    
    def send(self, title: str, content: str) -> NotificationResult:
        """发送 PushDeer 通知"""
        if not self.is_configured():
            self._log_not_configured()
            return self._create_error_result("DEER_KEY 未设置", "配置错误")
        
        self._log_send_attempt(title)
        
        try:
            # 构建请求数据
            deer_key = self.config_manager.get_config("DEER_KEY")
            data = {
                "text": title, 
                "desp": content, 
                "type": "markdown",
                "pushkey": deer_key
            }
            
            # 构建请求 URL
            url = self.config_manager.get_config("DEER_URL", "https://api2.pushdeer.com/message/push")
            
            # 发送请求
            response = requests.post(url, data=data, timeout=15).json()
            
            if len(response.get("content", {}).get("result", [])) > 0:
                self._log_send_success()
                return self._create_success_result("PushDeer 推送成功")
            else:
                error_msg = str(response)
                self._log_send_failure(error_msg)
                return self._create_error_result(error_msg, "PushDeer 推送失败")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求失败: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "PushDeer 推送失败")
        except Exception as e:
            error_msg = f"发送异常: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "PushDeer 推送失败")