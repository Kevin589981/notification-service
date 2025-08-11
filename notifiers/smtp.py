#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
import os
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.header import Header
from email.utils import formataddr
from email import encoders
from typing import List

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
        """发送 SMTP 邮件通知（不带附件）"""
        return self.send_with_attachments(title, content, [])
    
    def send_with_attachments(self, title: str, content: str, attachments: List = None) -> NotificationResult:
        """发送 SMTP 邮件通知（支持附件）"""
        if not self.is_configured():
            self._log_not_configured()
            return self._create_error_result("SMTP 配置不完整", "配置错误")
        
        self._log_send_attempt(title)
        if attachments:
            self.logger.info(f"准备发送 {len(attachments)} 个附件")
        
        try:
            # 获取配置
            smtp_server = self.config_manager.get_config("SMTP_SERVER")
            smtp_ssl = self.config_manager.get_config("SMTP_SSL")
            smtp_email = self.config_manager.get_config("SMTP_EMAIL")
            smtp_password = self.config_manager.get_config("SMTP_PASSWORD")
            smtp_name = self.config_manager.get_config("SMTP_NAME")
            
            # 构建邮件
            if attachments:
                # 有附件时使用多部分邮件
                message = MIMEMultipart()
                
                # 添加文本内容
                text_part = MIMEText(content, 'plain', 'utf-8')
                message.attach(text_part)
                
                # 添加附件
                for attachment in attachments:
                    if self._add_attachment(message, attachment):
                        self.logger.info(f"附件 {attachment.filename} 添加成功")
                    else:
                        self.logger.warning(f"附件 {attachment.filename} 添加失败")
            else:
                # 无附件时使用简单文本邮件
                message = MIMEText(content, 'plain', 'utf-8')
            
            # 设置邮件头
            message['From'] = formataddr((Header(smtp_name, 'utf-8').encode(), smtp_email))
            message['To'] = formataddr((Header(smtp_name, 'utf-8').encode(), smtp_email))
            message['Subject'] = Header(title, 'utf-8')
            
            # 发送邮件
            if smtp_ssl.lower() == 'true':
                smtp_client = smtplib.SMTP_SSL(smtp_server)
            else:
                smtp_client = smtplib.SMTP(smtp_server)
            
            smtp_client.login(smtp_email, smtp_password)
            smtp_client.sendmail(smtp_email, smtp_email, message.as_string())
            smtp_client.close()
            
            success_msg = "SMTP 邮件推送成功"
            if attachments:
                success_msg += f"（包含 {len(attachments)} 个附件）"
            
            self._log_send_success()
            return self._create_success_result(success_msg)
            
        except smtplib.SMTPException as e:
            error_msg = f"SMTP 错误: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "SMTP 邮件推送失败")
        except Exception as e:
            error_msg = f"发送异常: {str(e)}"
            self._log_send_failure(error_msg)
            return self._create_error_result(error_msg, "SMTP 邮件推送失败")
    
    def _add_attachment(self, message: MIMEMultipart, attachment) -> bool:
        """
        添加附件到邮件
        
        Args:
            message: 邮件对象
            attachment: 附件信息对象
            
        Returns:
            bool: 是否成功添加附件
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(attachment.filepath):
                self.logger.error(f"附件文件不存在: {attachment.filepath}")
                return False
            
            # 获取文件大小
            file_size = os.path.getsize(attachment.filepath)
            max_size = 25 * 1024 * 1024  # 25MB 限制
            
            if file_size > max_size:
                self.logger.error(f"附件 {attachment.filename} 过大: {file_size} bytes (最大 {max_size} bytes)")
                return False
            
            # 读取文件内容
            with open(attachment.filepath, 'rb') as f:
                file_data = f.read()
            
            # 猜测MIME类型
            content_type = attachment.content_type
            if content_type == 'application/octet-stream':
                content_type, _ = mimetypes.guess_type(attachment.filepath)
                if content_type is None:
                    content_type = 'application/octet-stream'
            
            # 创建附件对象
            main_type, sub_type = content_type.split('/', 1)
            
            if main_type == 'text':
                # 文本文件
                attachment_part = MIMEText(file_data.decode('utf-8'), sub_type, 'utf-8')
            else:
                # 二进制文件
                attachment_part = MIMEBase(main_type, sub_type)
                attachment_part.set_payload(file_data)
                encoders.encode_base64(attachment_part)
            
            # 设置附件头
            attachment_part.add_header(
                'Content-Disposition',
                f'attachment; filename="{attachment.filename}"'
            )
            
            # 添加到邮件
            message.attach(attachment_part)
            
            self.logger.debug(f"附件 {attachment.filename} 添加成功 ({content_type}, {file_size} bytes)")
            return True
            
        except Exception as e:
            self.logger.error(f"添加附件 {attachment.filename} 失败: {str(e)}")
            return False