#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests

from .base import BaseNotifier, NotificationResult


class PushPlusNotifier(BaseNotifier):
    """Push+ 微信推送通知器"""
    
    def get_name(self) -> str:
        return "Push+"
    
    def is_configured(self) -> bool:
        """检查 Push+ 是否已配置"""
        return bool(self.config_manager.get_config("PUSH_PLUS_TOKEN"))
    
    def send(self, title: str, content: str) -> NotificationResult:
        """发送 Push+ 通知"""
        if not self.is_configured():
            self._log_not_configured()
            return self._create_error_result("PUSH_PLUS_TOKEN 未设置", "配置错误")
        
        self._log_send_attempt(title)
        
        try:
            # 构建请求数据
            token = self.config_manager.get_config("PUSH_PLUS_TOKEN")
            topic = self.config_manager.get_config("PUSH_PLUS_USER", "")
            
            data = {
                "token": token,
                "title": title,
                "content": content,
                "topic": topic,
            }
            
            headers = {"Content-Type": "application/json"}
            body = json.dumps(data).encode(encoding="utf-8")
            
            # 尝试新版 API
            url = "http://www.pushplus.plus/send"
            response = requests.post(url=url, data=body, headers=headers, timeout=15).json()
            
            if response.get("code") == 200:
                self._log_send_success()
                return self._create_success_result("Push+ 推送成功")
            else:
                # 尝试旧版 API
                return self._try_old_api(body, headers, title, content)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求失败: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "Push+ 推送失败")
        except Exception as e:
            error_msg = f"发送异常: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "Push+ 推送失败")
    
    def _try_old_api(self, body: bytes, headers: dict, title: str, content: str) -> NotificationResult:
        """尝试旧版 API"""
        try:
            url_old = "http://pushplus.hxtrip.com/send"
            headers["Accept"] = "application/json"
            response = requests.post(url=url_old, data=body, headers=headers, timeout=15).json()
            
            if response.get("code") == 200:
                self._log_send_success()
                return self._create_success_result("Push+(hxtrip) 推送成功")
            else:
                error_msg = response.get("msg", "未知错误")
                self._log_send_failure(error_msg)
                return self._create_error_result(error_msg, "Push+ 推送失败")
                
        except Exception as e:
            error_msg = f"旧版 API 也失败: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "Push+ 推送失败")