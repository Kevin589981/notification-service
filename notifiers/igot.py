#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

from .base import BaseNotifier, NotificationResult


class IGotNotifier(BaseNotifier):
    """iGot 聚合推送通知器"""
    
    def get_name(self) -> str:
        return "iGot"
    
    def is_configured(self) -> bool:
        """检查 iGot 是否已配置"""
        return bool(self.config_manager.get_config("IGOT_PUSH_KEY"))
    
    def send(self, title: str, content: str) -> NotificationResult:
        """发送 iGot 通知"""
        if not self.is_configured():
            self._log_not_configured()
            return self._create_error_result("IGOT_PUSH_KEY 未设置", "配置错误")
        
        self._log_send_attempt(title)
        
        try:
            # 构建请求 URL
            push_key = self.config_manager.get_config("IGOT_PUSH_KEY")
            url = f'https://push.hellyw.com/{push_key}'
            
            # 构建请求数据
            data = {"title": title, "content": content}
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            
            # 发送请求
            response = requests.post(url, data=data, headers=headers, timeout=15).json()
            
            if response.get("ret") == 0:
                self._log_send_success()
                return self._create_success_result("iGot 推送成功")
            else:
                error_msg = response.get("errMsg", "未知错误")
                self._log_send_failure(error_msg)
                return self._create_error_result(error_msg, "iGot 推送失败")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求失败: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "iGot 推送失败")
        except Exception as e:
            error_msg = f"发送异常: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "iGot 推送失败")