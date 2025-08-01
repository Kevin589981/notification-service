#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

from .base import BaseNotifier, NotificationResult


class TelegramNotifier(BaseNotifier):
    """Telegram 机器人通知器"""
    
    def get_name(self) -> str:
        return "Telegram"
    
    def is_configured(self) -> bool:
        """检查 Telegram 机器人是否已配置"""
        return bool(
            self.config_manager.get_config("TG_BOT_TOKEN") and 
            self.config_manager.get_config("TG_USER_ID")
        )
    
    def send(self, title: str, content: str) -> NotificationResult:
        """发送 Telegram 通知"""
        if not self.is_configured():
            self._log_not_configured()
            return self._create_error_result("TG_BOT_TOKEN 或 TG_USER_ID 未设置", "配置错误")
        
        self._log_send_attempt(title)
        
        try:
            # 构建请求 URL
            bot_token = self.config_manager.get_config("TG_BOT_TOKEN")
            api_host = self.config_manager.get_config("TG_API_HOST")
            
            if api_host:
                url = f"https://{api_host}/bot{bot_token}/sendMessage"
            else:
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            # 构建请求数据
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            payload = {
                "chat_id": str(self.config_manager.get_config("TG_USER_ID")),
                "text": f"{title}\n\n{content}",
                "disable_web_page_preview": "true",
            }
            
            # 配置代理
            proxies = self._get_proxies()
            
            # 发送请求
            response = requests.post(
                url=url, 
                headers=headers, 
                params=payload, 
                proxies=proxies,
                timeout=15
            ).json()
            
            if response.get("ok"):
                self._log_send_success()
                return self._create_success_result("Telegram 推送成功")
            else:
                error_msg = response.get("description", "未知错误")
                self._log_send_failure(error_msg)
                return self._create_error_result(error_msg, "Telegram 推送失败")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求失败: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "Telegram 推送失败")
        except Exception as e:
            error_msg = f"发送异常: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "Telegram 推送失败")
    
    def _get_proxies(self) -> dict:
        """获取代理配置"""
        proxy_host = self.config_manager.get_config("TG_PROXY_HOST")
        proxy_port = self.config_manager.get_config("TG_PROXY_PORT")
        proxy_auth = self.config_manager.get_config("TG_PROXY_AUTH")
        
        if not (proxy_host and proxy_port):
            return None
        
        # 处理代理认证
        if proxy_auth and "@" not in proxy_host:
            proxy_host = f"{proxy_auth}@{proxy_host}"
        
        proxy_url = f"http://{proxy_host}:{proxy_port}"
        return {"http": proxy_url, "https": proxy_url}