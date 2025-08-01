#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import hashlib
import hmac
import json
import time
import urllib.parse
import requests

from .base import BaseNotifier, NotificationResult


class DingTalkNotifier(BaseNotifier):
    """钉钉机器人通知器"""
    
    def get_name(self) -> str:
        return "钉钉机器人"
    
    def is_configured(self) -> bool:
        """检查钉钉机器人是否已配置"""
        return bool(
            self.config_manager.get_config("DD_BOT_SECRET") and 
            self.config_manager.get_config("DD_BOT_TOKEN")
        )
    
    def send(self, title: str, content: str) -> NotificationResult:
        """发送钉钉机器人通知"""
        if not self.is_configured():
            self._log_not_configured()
            return self._create_error_result("DD_BOT_SECRET 或 DD_BOT_TOKEN 未设置", "配置错误")
        
        self._log_send_attempt(title)
        
        try:
            # 生成签名
            timestamp, sign = self._generate_sign()
            
            # 构建请求 URL
            token = self.config_manager.get_config("DD_BOT_TOKEN")
            url = f'https://oapi.dingtalk.com/robot/send?access_token={token}&timestamp={timestamp}&sign={sign}'
            
            # 构建请求数据
            headers = {"Content-Type": "application/json;charset=utf-8"}
            data = {
                "msgtype": "text", 
                "text": {"content": f"{title}\n\n{content}"}
            }
            
            # 发送请求
            response = requests.post(
                url=url, 
                data=json.dumps(data), 
                headers=headers, 
                timeout=15
            ).json()
            
            if not response.get("errcode"):
                self._log_send_success()
                return self._create_success_result("钉钉机器人推送成功")
            else:
                error_msg = response.get("errmsg", "未知错误")
                self._log_send_failure(error_msg)
                return self._create_error_result(error_msg, "钉钉机器人推送失败")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求失败: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "钉钉机器人推送失败")
        except Exception as e:
            error_msg = f"发送异常: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "钉钉机器人推送失败")
    
    def _generate_sign(self) -> tuple:
        """生成钉钉机器人签名"""
        timestamp = str(round(time.time() * 1000))
        secret = self.config_manager.get_config("DD_BOT_SECRET")
        
        secret_enc = secret.encode("utf-8")
        string_to_sign = f"{timestamp}\n{secret}"
        string_to_sign_enc = string_to_sign.encode("utf-8")
        
        hmac_code = hmac.new(
            secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
        ).digest()
        
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        
        return timestamp, sign