#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重试处理模块
实现网络错误的重试机制，支持指数退避策略
"""

import time
import logging
import random
from typing import Callable, Any, Optional, List, Type
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RetryableError(Exception):
    """可重试的错误基类"""
    pass


class NetworkError(RetryableError):
    """网络相关错误"""
    pass


class TemporaryError(RetryableError):
    """临时性错误"""
    pass


class RetryStrategy(Enum):
    """重试策略枚举"""
    FIXED = "fixed"           # 固定间隔
    LINEAR = "linear"         # 线性增长
    EXPONENTIAL = "exponential"  # 指数退避


@dataclass
class RetryConfig:
    """重试配置"""
    max_attempts: int = 3                    # 最大重试次数
    base_delay: float = 1.0                  # 基础延迟时间（秒）
    max_delay: float = 60.0                  # 最大延迟时间（秒）
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL  # 重试策略
    backoff_multiplier: float = 2.0          # 退避倍数
    jitter: bool = True                      # 是否添加随机抖动
    retryable_exceptions: List[Type[Exception]] = None  # 可重试的异常类型
    
    def __post_init__(self):
        if self.retryable_exceptions is None:
            self.retryable_exceptions = [
                RetryableError,
                NetworkError,
                TemporaryError,
                ConnectionError,
                TimeoutError,
            ]


class RetryHandler:
    """重试处理器"""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        """
        初始化重试处理器
        
        Args:
            config: 重试配置，如果为 None 则使用默认配置
        """
        self.config = config or RetryConfig()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        执行函数并在失败时重试
        
        Args:
            func: 要执行的函数
            *args: 函数的位置参数
            **kwargs: 函数的关键字参数
            
        Returns:
            函数的执行结果
            
        Raises:
            Exception: 如果所有重试都失败，抛出最后一次的异常
        """
        last_exception = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                func_name = getattr(func, '__name__', str(func))
                self.logger.debug(f"执行函数 {func_name}，第 {attempt} 次尝试")
                result = func(*args, **kwargs)
                
                if attempt > 1:
                    func_name = getattr(func, '__name__', str(func))
                    self.logger.info(f"函数 {func_name} 在第 {attempt} 次尝试后成功执行")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                func_name = getattr(func, '__name__', str(func))
                
                # 检查是否为可重试的异常
                if not self._is_retryable_exception(e):
                    self.logger.error(f"函数 {func_name} 发生不可重试的异常: {str(e)}")
                    raise e
                
                # 如果是最后一次尝试，不再重试
                if attempt == self.config.max_attempts:
                    self.logger.error(f"函数 {func_name} 在 {attempt} 次尝试后仍然失败: {str(e)}")
                    break
                
                # 计算延迟时间并等待
                delay = self._calculate_delay(attempt)
                self.logger.warning(f"函数 {func_name} 第 {attempt} 次尝试失败: {str(e)}，{delay:.2f} 秒后重试")
                time.sleep(delay)
        
        # 所有重试都失败，抛出最后一次的异常
        raise last_exception
    
    def _is_retryable_exception(self, exception: Exception) -> bool:
        """
        检查异常是否可重试
        
        Args:
            exception: 要检查的异常
            
        Returns:
            bool: 如果异常可重试返回 True，否则返回 False
        """
        return any(isinstance(exception, exc_type) for exc_type in self.config.retryable_exceptions)
    
    def _calculate_delay(self, attempt: int) -> float:
        """
        计算延迟时间
        
        Args:
            attempt: 当前尝试次数（从1开始）
            
        Returns:
            float: 延迟时间（秒）
        """
        if self.config.strategy == RetryStrategy.FIXED:
            delay = self.config.base_delay
        elif self.config.strategy == RetryStrategy.LINEAR:
            delay = self.config.base_delay * attempt
        elif self.config.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.config.base_delay * (self.config.backoff_multiplier ** (attempt - 1))
        else:
            delay = self.config.base_delay
        
        # 限制最大延迟时间
        delay = min(delay, self.config.max_delay)
        
        # 添加随机抖动以避免雷群效应
        if self.config.jitter:
            jitter_range = delay * 0.1  # 10% 的抖动
            delay += random.uniform(-jitter_range, jitter_range)
            delay = max(0, delay)  # 确保延迟时间不为负数
        
        return delay


def retry_on_failure(config: Optional[RetryConfig] = None):
    """
    装饰器：为函数添加重试机制
    
    Args:
        config: 重试配置
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            retry_handler = RetryHandler(config)
            return retry_handler.execute_with_retry(func, *args, **kwargs)
        return wrapper
    return decorator


# 预定义的重试配置
NETWORK_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    base_delay=1.0,
    max_delay=30.0,
    strategy=RetryStrategy.EXPONENTIAL,
    backoff_multiplier=2.0,
    jitter=True,
    retryable_exceptions=[NetworkError, ConnectionError, TimeoutError]
)

NOTIFICATION_RETRY_CONFIG = RetryConfig(
    max_attempts=2,
    base_delay=0.5,
    max_delay=10.0,
    strategy=RetryStrategy.EXPONENTIAL,
    backoff_multiplier=2.0,
    jitter=True,
    retryable_exceptions=[RetryableError, NetworkError, TemporaryError]
)