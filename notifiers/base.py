#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Any, Dict
import logging

logger = logging.getLogger(__name__)


@dataclass
class NotificationResult:
    """通知发送结果数据模型"""
    success: bool
    channel: str
    message: str
    error: Optional[str] = None


class BaseNotifier(ABC):
    """通知器基础抽象类，定义所有通知器的通用接口"""
    
    def __init__(self, config_manager):
        """
        初始化通知器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def is_configured(self) -> bool:
        """
        检查通知器是否已正确配置
        
        Returns:
            bool: 如果配置完整返回 True，否则返回 False
        """
        pass
    
    @abstractmethod
    def send(self, title: str, content: str) -> NotificationResult:
        """
        发送通知消息
        
        Args:
            title: 通知标题
            content: 通知内容
            
        Returns:
            NotificationResult: 发送结果
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        获取通知器名称
        
        Returns:
            str: 通知器名称
        """
        pass
    
    def _create_success_result(self, message: str = "发送成功") -> NotificationResult:
        """创建成功结果"""
        return NotificationResult(
            success=True,
            channel=self.get_name(),
            message=message
        )
    
    def _create_error_result(self, error: str, message: str = "发送失败") -> NotificationResult:
        """创建错误结果"""
        return NotificationResult(
            success=False,
            channel=self.get_name(),
            message=message,
            error=error
        )
    
    def _log_send_attempt(self, title: str) -> None:
        """记录发送尝试日志"""
        self.logger.info(f"{self.get_name()} 服务启动，准备发送通知: {title}")
    
    def _log_send_success(self) -> None:
        """记录发送成功日志"""
        self.logger.info(f"{self.get_name()} 推送成功！")
    
    def _log_send_failure(self, error: str) -> None:
        """记录发送失败日志"""
        self.logger.error(f"{self.get_name()} 推送失败！错误信息: {error}")
    
    def _log_not_configured(self) -> None:
        """记录未配置日志"""
        self.logger.warning(f"{self.get_name()} 服务未配置，跳过推送")