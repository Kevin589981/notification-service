#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

from .base import BaseNotifier, NotificationResult


class QmsgNotifier(BaseNotifier):
    """Qmsg 酱通知器"""
    
    def get_name(self) -> str:
        return "Qmsg酱"
    
    def is_configured(self) -> bool:
        """检查 Qmsg 是否已配置"""
        return bool(
            self.config_manager.get_config("QMSG_KEY") and 
            self.config_manager.get_config("QMSG_TYPE")
        )
    
    def send(self, title: str, content: str) -> NotificationResult:
        """发送 Qmsg 通知"""
        if not self.is_configured():
            self._log_not_configured()
            return self._create_error_result("QMSG_KEY 或 QMSG_TYPE 未设置", "配置错误")
        
        self._log_send_attempt(title)
        
        try:
            # 构建请求 URL
            qmsg_key = self.config_manager.get_config("QMSG_KEY")
            qmsg_type = self.config_manager.get_config("QMSG_TYPE")
            url = f'https://qmsg.zendee.cn/{qmsg_type}/{qmsg_key}'
            
            # 构建请求数据
            message = f'{title}\n\n{content.replace("----", "-")}'
            payload = {"msg": message.encode("utf-8")}
            
            # 发送请求
            response = requests.post(url=url, params=payload, timeout=15).json()
            
            if response.get("code") == 0:
                self._log_send_success()
                return self._create_success_result("Qmsg酱推送成功")
            else:
                error_msg = response.get("reason", "未知错误")
                self._log_send_failure(error_msg)
                return self._create_error_result(error_msg, "Qmsg酱推送失败")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求失败: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "Qmsg酱推送失败")
        except Exception as e:
            error_msg = f"发送异常: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "Qmsg酱推送失败")