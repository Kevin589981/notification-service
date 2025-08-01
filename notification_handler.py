#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import threading

from retry_handler import RetryHandler, RetryConfig, RetryStrategy, NetworkError, TemporaryError

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_manager import ConfigManager
from notifiers.base import NotificationResult

logger = logging.getLogger(__name__)


@dataclass
class GitHubEventPayload:
    """GitHub 事件负载数据模型"""
    title: str
    content: str
    source: str
    timestamp: str


@dataclass
class NotificationSummary:
    """通知发送汇总结果"""
    total_channels: int
    successful_channels: List[str]
    failed_channels: List[str]
    errors: List[str]


class NotificationHandler:
    """通知处理器，管理多个通知器并处理通知发送逻辑"""
    
    def __init__(self, config_manager: ConfigManager):
        """
        初始化通知处理器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.notifiers = []
        self._lock = threading.Lock()
        
        # 初始化所有通知器
        self._initialize_notifiers()
    
    def _initialize_notifiers(self):
        """初始化所有可用的通知器"""
        from notifiers.bark import BarkNotifier
        from notifiers.console import ConsoleNotifier
        from notifiers.dingtalk import DingTalkNotifier
        from notifiers.wecom import WeComAppNotifier, WeComBotNotifier
        from notifiers.telegram import TelegramNotifier
        from notifiers.smtp import SMTPNotifier
        from notifiers.pushplus import PushPlusNotifier
        from notifiers.qmsg import QmsgNotifier
        from notifiers.gotify import GotifyNotifier
        from notifiers.igot import IGotNotifier
        from notifiers.pushdeer import PushDeerNotifier
        from notifiers.serverchan import ServerChanNotifier
        
        # 初始化所有通知器
        self.notifiers = [
            BarkNotifier(self.config_manager),
            ConsoleNotifier(self.config_manager),
            DingTalkNotifier(self.config_manager),
            WeComAppNotifier(self.config_manager),
            WeComBotNotifier(self.config_manager),
            TelegramNotifier(self.config_manager),
            SMTPNotifier(self.config_manager),
            PushPlusNotifier(self.config_manager),
            QmsgNotifier(self.config_manager),
            GotifyNotifier(self.config_manager),
            IGotNotifier(self.config_manager),
            PushDeerNotifier(self.config_manager),
            ServerChanNotifier(self.config_manager),
        ]
    
    def process_github_event(self, event_data: dict) -> None:
        """
        处理来自 GitHub Actions 的事件数据
        
        Args:
            event_data: GitHub repository_dispatch 事件数据
        """
        try:
            # 解析事件数据
            client_payload = event_data.get('client_payload', {})
            payload = GitHubEventPayload(
                title=client_payload.get('title', '通知'),
                content=client_payload.get('content', ''),
                source=client_payload.get('source', 'unknown'),
                timestamp=client_payload.get('timestamp', '')
            )
            
            self.logger.info(f"接收到来自 {payload.source} 的通知请求: {payload.title}")
            
            # 验证请求数据
            if not payload.content:
                self.logger.warning("通知内容为空，跳过发送")
                return
            
            # 发送通知
            self.send_notification(payload.title, payload.content, payload.source)
            
        except Exception as e:
            self.logger.error(f"处理 GitHub 事件时发生错误: {str(e)}")
    
    def send_notification(self, title: str, content: str, source: str = "unknown") -> NotificationSummary:
        """
        发送通知到所有配置的渠道
        
        Args:
            title: 通知标题
            content: 通知内容
            source: 通知来源
            
        Returns:
            NotificationSummary: 发送结果汇总
        """
        if not content:
            self.logger.warning(f"{title} 推送内容为空！")
            return NotificationSummary(0, [], [], ["推送内容为空"])
        
        # 检查是否需要跳过推送
        if self._should_skip_push(title):
            self.logger.info(f"{title} 在跳过推送列表中，跳过推送！")
            return NotificationSummary(0, [], [], ["标题在跳过列表中"])
        
        # 获取活跃的通知器
        active_notifiers = self.get_active_notifiers()
        if not active_notifiers:
            self.logger.warning("没有配置任何通知器")
            return NotificationSummary(0, [], [], ["没有配置任何通知器"])
        
        # 添加一言（如果启用）
        final_content = self._add_hitokoto_if_enabled(content)
        
        # 并发发送通知
        return self._send_concurrent_notifications(title, final_content, active_notifiers)
    
    def get_active_notifiers(self) -> List:
        """
        获取已配置的通知器列表
        
        Returns:
            List: 已配置的通知器列表
        """
        return [notifier for notifier in self.notifiers if notifier.is_configured()]
    
    def _should_skip_push(self, title: str) -> bool:
        """检查是否应该跳过推送"""
        skip_titles = self.config_manager.get_config("SKIP_PUSH_TITLE", "")
        if skip_titles:
            skip_list = skip_titles.split("\n")
            return title in skip_list
        return False
    
    def _add_hitokoto_if_enabled(self, content: str) -> str:
        """如果启用一言，则添加到内容末尾"""
        if self.config_manager.get_config("HITOKOTO", False):
            try:
                import requests
                url = "https://v1.hitokoto.cn/"
                res = requests.get(url, timeout=5).json()
                hitokoto = res["hitokoto"] + "    ----" + res["from"]
                return content + "\n\n" + hitokoto
            except Exception as e:
                self.logger.warning(f"获取一言失败: {str(e)}")
        return content
    
    def _send_concurrent_notifications(self, title: str, content: str, notifiers: List) -> NotificationSummary:
        """
        并发发送通知到多个渠道，支持超时控制和资源管理
        
        Args:
            title: 通知标题
            content: 通知内容
            notifiers: 通知器列表
            
        Returns:
            NotificationSummary: 发送结果汇总
        """
        successful_channels = []
        failed_channels = []
        errors = []
        
        if not notifiers:
            self.logger.warning("没有可用的通知器")
            return NotificationSummary(0, [], [], ["没有可用的通知器"])
        
        # 获取配置的超时时间和最大工作线程数
        timeout = int(self.config_manager.get_config("NOTIFICATION_TIMEOUT", 30))
        max_workers = min(len(notifiers), int(self.config_manager.get_config("MAX_CONCURRENT_NOTIFICATIONS", 10)))
        
        self.logger.info(f"开始并发发送通知到 {len(notifiers)} 个渠道，使用 {max_workers} 个工作线程，超时时间 {timeout} 秒")
        
        # 使用线程池并发发送，确保资源管理
        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="NotificationSender") as executor:
            # 提交所有发送任务
            future_to_notifier = {}
            for notifier in notifiers:
                try:
                    future = executor.submit(self._send_single_notification, notifier, title, content)
                    future_to_notifier[future] = notifier
                except Exception as e:
                    # 提交任务失败
                    channel_name = notifier.get_name()
                    failed_channels.append(channel_name)
                    error_msg = f"提交发送任务失败: {str(e)}"
                    errors.append(f"{channel_name}: {error_msg}")
                    self.logger.error(f"{channel_name} 提交任务失败: {error_msg}")
            
            # 收集结果，使用超时控制
            completed_count = 0
            for future in as_completed(future_to_notifier, timeout=timeout + 10):  # 额外10秒缓冲
                notifier = future_to_notifier[future]
                channel_name = notifier.get_name()
                completed_count += 1
                
                try:
                    result = future.result(timeout=1)  # 快速获取已完成的结果
                    if result.success:
                        successful_channels.append(result.channel)
                        self.logger.info(f"[{completed_count}/{len(future_to_notifier)}] {result.channel} 推送成功: {result.message}")
                    else:
                        failed_channels.append(result.channel)
                        error_msg = result.error or "未知错误"
                        errors.append(f"{result.channel}: {error_msg}")
                        self.logger.error(f"[{completed_count}/{len(future_to_notifier)}] {result.channel} 推送失败: {error_msg}")
                        
                except Exception as e:
                    # 处理超时或其他异常
                    failed_channels.append(channel_name)
                    error_msg = f"获取发送结果异常: {str(e)}"
                    errors.append(f"{channel_name}: {error_msg}")
                    self.logger.error(f"[{completed_count}/{len(future_to_notifier)}] {channel_name} 获取结果异常: {error_msg}")
            
            # 检查是否有未完成的任务
            remaining_futures = [f for f in future_to_notifier.keys() if not f.done()]
            if remaining_futures:
                self.logger.warning(f"有 {len(remaining_futures)} 个通知任务未在超时时间内完成")
                for future in remaining_futures:
                    notifier = future_to_notifier[future]
                    channel_name = notifier.get_name()
                    if channel_name not in failed_channels:
                        failed_channels.append(channel_name)
                        errors.append(f"{channel_name}: 发送超时")
                    future.cancel()  # 尝试取消未完成的任务
        
        # 记录汇总结果
        total = len(notifiers)
        success_count = len(successful_channels)
        failure_count = len(failed_channels)
        
        self.logger.info(f"通知发送完成: 总计 {total} 个渠道，成功 {success_count} 个，失败 {failure_count} 个")
        
        # 记录详细的成功和失败信息
        if successful_channels:
            self.logger.info(f"成功的渠道: {', '.join(successful_channels)}")
        if failed_channels:
            self.logger.warning(f"失败的渠道: {', '.join(failed_channels)}")
        
        return NotificationSummary(
            total_channels=total,
            successful_channels=successful_channels,
            failed_channels=failed_channels,
            errors=errors
        )
    
    def _send_single_notification(self, notifier, title: str, content: str) -> NotificationResult:
        """
        发送单个通知，包含错误处理、重试机制和日志记录
        
        Args:
            notifier: 通知器实例
            title: 通知标题
            content: 通知内容
            
        Returns:
            NotificationResult: 发送结果
        """
        channel_name = notifier.get_name()
        
        # 配置重试机制
        retry_config = RetryConfig(
            max_attempts=int(self.config_manager.get_config("NOTIFICATION_RETRY_ATTEMPTS", 2)),
            base_delay=float(self.config_manager.get_config("NOTIFICATION_RETRY_DELAY", 1.0)),
            max_delay=float(self.config_manager.get_config("NOTIFICATION_MAX_RETRY_DELAY", 10.0)),
            strategy=RetryStrategy.EXPONENTIAL,
            backoff_multiplier=2.0,
            jitter=True,
            retryable_exceptions=[NetworkError, TemporaryError, ConnectionError, TimeoutError]
        )
        
        retry_handler = RetryHandler(retry_config)
        
        try:
            # 记录发送开始
            self.logger.debug(f"开始发送通知到 {channel_name}")
            
            # 使用重试机制执行发送
            result = retry_handler.execute_with_retry(self._execute_notification_send, notifier, title, content)
            
            # 验证结果
            if not isinstance(result, NotificationResult):
                self.logger.error(f"{channel_name} 返回了无效的结果类型: {type(result)}")
                return NotificationResult(
                    success=False,
                    channel=channel_name,
                    message="发送失败",
                    error="通知器返回了无效的结果类型"
                )
            
            return result
            
        except Exception as e:
            # 捕获所有异常，确保单个通知器失败不影响其他通知器
            error_msg = self._format_error_message(e)
            self.logger.error(f"{channel_name} 发送失败（已重试）: {error_msg}")
            
            return NotificationResult(
                success=False,
                channel=channel_name,
                message="发送失败",
                error=error_msg
            )
    
    def _execute_notification_send(self, notifier, title: str, content: str) -> NotificationResult:
        """
        执行通知发送的核心逻辑，可能会抛出可重试的异常
        
        Args:
            notifier: 通知器实例
            title: 通知标题
            content: 通知内容
            
        Returns:
            NotificationResult: 发送结果
            
        Raises:
            NetworkError: 网络相关错误
            TemporaryError: 临时性错误
        """
        try:
            result = notifier.send(title, content)
            
            # 如果通知器返回失败结果，检查是否为可重试的错误
            if not result.success and self._is_retryable_error(result.error):
                if "网络" in str(result.error) or "连接" in str(result.error) or "timeout" in str(result.error).lower():
                    raise NetworkError(f"网络错误: {result.error}")
                elif "临时" in str(result.error) or "temporary" in str(result.error).lower():
                    raise TemporaryError(f"临时错误: {result.error}")
            
            return result
            
        except (ConnectionError, TimeoutError) as e:
            # 将网络相关异常转换为可重试的异常
            raise NetworkError(f"网络连接异常: {str(e)}")
        except Exception as e:
            # 检查异常消息是否表明这是一个可重试的错误
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ["timeout", "connection", "network", "temporary", "503", "502", "504"]):
                raise NetworkError(f"网络相关异常: {str(e)}")
            else:
                # 不可重试的异常，直接抛出
                raise e
    
    def _is_retryable_error(self, error_msg: Optional[str]) -> bool:
        """
        检查错误消息是否表明这是一个可重试的错误
        
        Args:
            error_msg: 错误消息
            
        Returns:
            bool: 如果是可重试的错误返回 True
        """
        if not error_msg:
            return False
        
        error_msg_lower = error_msg.lower()
        retryable_keywords = [
            "timeout", "连接超时", "网络", "network", "connection", 
            "temporary", "临时", "503", "502", "504", "429",
            "服务不可用", "service unavailable", "too many requests"
        ]
        
        return any(keyword in error_msg_lower for keyword in retryable_keywords)
    
    def _format_error_message(self, exception: Exception) -> str:
        """
        格式化错误消息，提供更友好的错误描述
        
        Args:
            exception: 异常对象
            
        Returns:
            str: 格式化后的错误消息
        """
        error_type = type(exception).__name__
        error_msg = str(exception)
        
        # 根据异常类型提供更友好的描述
        if isinstance(exception, NetworkError):
            return f"网络错误: {error_msg}"
        elif isinstance(exception, TemporaryError):
            return f"临时错误: {error_msg}"
        elif isinstance(exception, ConnectionError):
            return f"连接错误: {error_msg}"
        elif isinstance(exception, TimeoutError):
            return f"超时错误: {error_msg}"
        else:
            return f"{error_type}: {error_msg}"