#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.parse
import requests
from typing import Dict, Any

from .base import BaseNotifier, NotificationResult


class BarkNotifier(BaseNotifier):
    """Bark 通知器"""
    
    def get_name(self) -> str:
        return "Bark"
    
    def is_configured(self) -> bool:
        """检查 Bark 是否已配置"""
        return bool(self.config_manager.get_config("BARK_PUSH"))
    
    def send(self, title: str, content: str) -> NotificationResult:
        """发送 Bark 通知"""
        if not self.is_configured():
            self._log_not_configured()
            return self._create_error_result("BARK_PUSH 未设置", "配置错误")
        
        self._log_send_attempt(title)
        
        try:
            # 构建 URL
            bark_push = self.config_manager.get_config("BARK_PUSH")
            if bark_push.startswith("http"):
                url = f'{bark_push}/{urllib.parse.quote_plus(title)}/{urllib.parse.quote_plus(content)}'
            else:
                url = f'https://api.day.app/{bark_push}/{urllib.parse.quote_plus(title)}/{urllib.parse.quote_plus(content)}'
            
            # 添加可选参数
            params = self._build_params()
            if params:
                url = url + "?" + params.rstrip("&")
            
            # 发送请求
            response = requests.get(url, timeout=15).json()
            
            if response.get("code") == 200:
                self._log_send_success()
                return self._create_success_result("Bark 推送成功")
            else:
                error_msg = response.get("message", "未知错误")
                self._log_send_failure(error_msg)
                return self._create_error_result(error_msg, "Bark 推送失败")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求失败: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "Bark 推送失败")
        except Exception as e:
            error_msg = f"发送异常: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "Bark 推送失败")
    
    def _build_params(self) -> str:
        """构建可选参数"""
        bark_params = {
            "BARK_ARCHIVE": "isArchive",
            "BARK_GROUP": "group", 
            "BARK_SOUND": "sound",
            "BARK_ICON": "icon",
        }
        
        params = ""
        for config_key, param_key in bark_params.items():
            value = self.config_manager.get_config(config_key)
            if value:
                params += f"{param_key}={value}&"
        
        return params