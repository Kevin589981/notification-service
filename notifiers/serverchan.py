#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

from .base import BaseNotifier, NotificationResult


class ServerChanNotifier(BaseNotifier):
    """Server酱通知器，兼容新版和旧版 API"""
    
    def get_name(self) -> str:
        return "Server酱"
    
    def is_configured(self) -> bool:
        """检查 Server酱 是否已配置"""
        # 支持两种配置方式：PUSH_KEY（GlaDOS项目）和 SCKEY（jichang_checkin项目）
        return bool(
            self.config_manager.get_config("PUSH_KEY") or 
            self.config_manager.get_config("SCKEY")
        )
    
    def send(self, title: str, content: str) -> NotificationResult:
        """发送 Server酱 通知"""
        if not self.is_configured():
            self._log_not_configured()
            return self._create_error_result("PUSH_KEY 或 SCKEY 未设置", "配置错误")
        
        self._log_send_attempt(title)
        
        try:
            # 获取密钥，优先使用 PUSH_KEY，然后是 SCKEY
            push_key = self.config_manager.get_config("PUSH_KEY") or self.config_manager.get_config("SCKEY")
            
            # 根据密钥类型确定 API 版本和 URL
            if push_key.startswith("SCT"):
                # 新版 Server酱 Turbo
                url = f'https://sctapi.ftqq.com/{push_key}.send'
                api_version = "新版"
            else:
                # 旧版 Server酱
                url = f'https://sc.ftqq.com/{push_key}.send'
                api_version = "旧版"
            
            # 构建请求数据
            data = {
                "text": title, 
                "desp": content.replace("\n", "\n\n")  # 兼容 Markdown 格式
            }
            
            # 发送请求
            response = requests.post(url, data=data, timeout=15).json()
            
            # 检查响应结果
            if self._is_success_response(response):
                self._log_send_success()
                return self._create_success_result(f"Server酱({api_version}) 推送成功")
            else:
                error_msg = self._extract_error_message(response)
                self._log_send_failure(error_msg)
                return self._create_error_result(error_msg, f"Server酱({api_version}) 推送失败")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求失败: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "Server酱推送失败")
        except Exception as e:
            error_msg = f"发送异常: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "Server酱推送失败")
    
    def _is_success_response(self, response: dict) -> bool:
        """判断响应是否成功"""
        # 新版 API 返回 code: 0 表示成功
        if response.get("code") == 0:
            return True
        # 旧版 API 返回 errno: 0 表示成功
        if response.get("errno") == 0:
            return True
        return False
    
    def _extract_error_message(self, response: dict) -> str:
        """提取错误信息"""
        # 尝试从不同字段获取错误信息
        error_msg = (
            response.get("message") or 
            response.get("errmsg") or 
            response.get("error") or 
            "未知错误"
        )
        return str(error_msg)
    
    def validate_config(self) -> tuple:
        """
        验证配置的有效性
        
        Returns:
            tuple: (is_valid, error_message)
        """
        push_key = self.config_manager.get_config("PUSH_KEY")
        sckey = self.config_manager.get_config("SCKEY")
        
        if not (push_key or sckey):
            return False, "PUSH_KEY 和 SCKEY 都未设置"
        
        key = push_key or sckey
        
        # 验证密钥格式
        if key.startswith("SCT"):
            # 新版密钥格式验证
            if len(key) < 20:
                return False, "新版 Server酱密钥格式不正确"
        else:
            # 旧版密钥格式验证
            if len(key) < 10:
                return False, "旧版 Server酱密钥格式不正确"
        
        return True, "配置验证通过"