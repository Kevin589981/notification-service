#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础通知器接口
定义所有通知器的通用接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class NotificationResult:
    """通知结果数据模型"""
    success: bool
    channel: str
    message: str
    error: Optional[str] = None


class BaseNotifier(ABC):
    """基础通知器抽象类"""
    
    def __init__(self, config: dict):
        """
        初始化通知器
        
        Args:
            config: 通知器配置
        """
        self.config = config
    
    @abstractmethod
    def is_configured(self) -> bool:
        """
        检查是否已配置
        
        Returns:
            是否已配置
        """
        pass
    
    @abstractmethod
    def send(self, title: str, content: str) -> NotificationResult:
        """
        发送通知
        
        Args:
            title: 通知标题
            content: 通知内容
            
        Returns:
            通知结果
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        获取通知器名称
        
        Returns:
            通知器名称
        """
        pass
    
    def validate_config(self) -> list:
        """
        验证配置
        
        Returns:
            配置错误列表
        """
        return []