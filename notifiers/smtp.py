#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

from .base import BaseNotifier, NotificationResult


class SMTPNotifier(BaseNotifier):
    """SMTP 邮件通知器"""
    
    def get_name(self) -> str:
        return "SMTP邮件"
    
    def is_configured(self) -> bool:
        """检查 SMTP 是否已配置"""
        required_configs = [
            "SMTP_SERVER", "SMTP_SSL", "SMTP_EMAIL", 
            "SMTP_PASSWORD", "SMTP_NAME"
        ]
        return all(self.config_manager.get_config(config) for config in required_configs)
    
    def send(self, title: str, content: str) -> NotificationResult:
        """发送 SMTP 邮件通知"""
        if not self.is_configured():
            self._log_not_configured()
            return self._create_error_result("SMTP 配置不完整", "配置错误")
        
        self._log_send_attempt(title)
        
        try:
            # 获取配置
            smtp_server = self.config_manager.get_config("SMTP_SERVER")
            smtp_ssl = self.config_manager.get_config("SMTP_SSL")
            smtp_email = self.config_manager.get_config("SMTP_EMAIL")
            smtp_password = self.config_manager.get_config("SMTP_PASSWORD")
            smtp_name = self.config_manager.get_config("SMTP_NAME")
            
            # 构建邮件
            message = MIMEText(content, 'plain', 'utf-8')
            message['From'] = formataddr((Header(smtp_name, 'utf-8').encode(), smtp_email))
            message['To'] = formataddr((Header(smtp_name, 'utf-8').encode(), smtp_email))
            message['Subject'] = Header(title, 'utf-8')
            
            # 发送邮件
            if smtp_ssl.lower() == 'true':
                smtp_client = smtplib.SMTP_SSL(smtp_server)
            else:
                smtp_client = smtplib.SMTP(smtp_server)
            
            smtp_client.login(smtp_email, smtp_password)
            smtp_client.sendmail(smtp_email, smtp_email, message.as_bytes())
            smtp_client.close()
            
            self._log_send_success()
            return self._create_success_result("SMTP 邮件推送成功")
            
        except smtplib.SMTPException as e:
            error_msg = f"SMTP 错误: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "SMTP 邮件推送失败")
        except Exception as e:
            error_msg = f"发送异常: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "SMTP 邮件推送失败")