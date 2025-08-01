#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import requests

from .base import BaseNotifier, NotificationResult


class WeComAppNotifier(BaseNotifier):
    """企业微信应用通知器"""
    
    def get_name(self) -> str:
        return "企业微信应用"
    
    def is_configured(self) -> bool:
        """检查企业微信应用是否已配置"""
        return bool(self.config_manager.get_config("QYWX_AM"))
    
    def send(self, title: str, content: str) -> NotificationResult:
        """发送企业微信应用通知"""
        if not self.is_configured():
            self._log_not_configured()
            return self._create_error_result("QYWX_AM 未设置", "配置错误")
        
        self._log_send_attempt(title)
        
        try:
            # 解析配置参数
            qywx_am = self.config_manager.get_config("QYWX_AM")
            qywx_am_parts = re.split(",", qywx_am)
            
            if len(qywx_am_parts) < 4 or len(qywx_am_parts) > 5:
                error_msg = "QYWX_AM 配置格式错误"
                self._log_send_failure(error_msg)
                return self._create_error_result(error_msg, "配置错误")
            
            corpid = qywx_am_parts[0]
            corpsecret = qywx_am_parts[1]
            touser = qywx_am_parts[2]
            agentid = qywx_am_parts[3]
            media_id = qywx_am_parts[4] if len(qywx_am_parts) == 5 else ""
            
            # 创建企业微信客户端
            wecom_client = WeComClient(corpid, corpsecret, agentid)
            
            # 发送消息
            if not media_id:
                message = f"{title}\n\n{content}"
                response = wecom_client.send_text(message, touser)
            else:
                response = wecom_client.send_mpnews(title, content, media_id, touser)
            
            if response == "ok":
                self._log_send_success()
                return self._create_success_result("企业微信应用推送成功")
            else:
                self._log_send_failure(response)
                return self._create_error_result(response, "企业微信应用推送失败")
                
        except Exception as e:
            error_msg = f"发送异常: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "企业微信应用推送失败")


class WeComBotNotifier(BaseNotifier):
    """企业微信机器人通知器"""
    
    def get_name(self) -> str:
        return "企业微信机器人"
    
    def is_configured(self) -> bool:
        """检查企业微信机器人是否已配置"""
        return bool(self.config_manager.get_config("QYWX_KEY"))
    
    def send(self, title: str, content: str) -> NotificationResult:
        """发送企业微信机器人通知"""
        if not self.is_configured():
            self._log_not_configured()
            return self._create_error_result("QYWX_KEY 未设置", "配置错误")
        
        self._log_send_attempt(title)
        
        try:
            # 构建请求 URL
            qywx_key = self.config_manager.get_config("QYWX_KEY")
            url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={qywx_key}"
            
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
            
            if response.get("errcode") == 0:
                self._log_send_success()
                return self._create_success_result("企业微信机器人推送成功")
            else:
                error_msg = response.get("errmsg", "未知错误")
                self._log_send_failure(error_msg)
                return self._create_error_result(error_msg, "企业微信机器人推送失败")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求失败: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "企业微信机器人推送失败")
        except Exception as e:
            error_msg = f"发送异常: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "企业微信机器人推送失败")


class WeComClient:
    """企业微信客户端"""
    
    def __init__(self, corpid: str, corpsecret: str, agentid: str):
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.agentid = agentid
    
    def get_access_token(self) -> str:
        """获取访问令牌"""
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        params = {
            "corpid": self.corpid,
            "corpsecret": self.corpsecret,
        }
        response = requests.post(url, params=params, timeout=15)
        data = response.json()
        return data["access_token"]
    
    def send_text(self, message: str, touser: str = "@all") -> str:
        """发送文本消息"""
        send_url = (
            "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="
            + self.get_access_token()
        )
        send_data = {
            "touser": touser,
            "msgtype": "text",
            "agentid": self.agentid,
            "text": {"content": message},
            "safe": "0",
        }
        send_bytes = json.dumps(send_data).encode("utf-8")
        response = requests.post(send_url, data=send_bytes, timeout=15)
        response_data = response.json()
        return response_data["errmsg"]
    
    def send_mpnews(self, title: str, message: str, media_id: str, touser: str = "@all") -> str:
        """发送图文消息"""
        send_url = (
            "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="
            + self.get_access_token()
        )
        send_data = {
            "touser": touser,
            "msgtype": "mpnews",
            "agentid": self.agentid,
            "mpnews": {
                "articles": [
                    {
                        "title": title,
                        "thumb_media_id": media_id,
                        "author": "Author",
                        "content_source_url": "",
                        "content": message.replace("\n", "<br/>"),
                        "digest": message,
                    }
                ]
            },
        }
        send_bytes = json.dumps(send_data).encode("utf-8")
        response = requests.post(send_url, data=send_bytes, timeout=15)
        response_data = response.json()
        return response_data["errmsg"]