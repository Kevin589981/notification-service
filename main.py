#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notification Service Main Entry Point
处理来自 GitHub Actions 的通知请求
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, List

from config_manager import ConfigManager
from notification_handler import NotificationHandler


def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def process_attachments(client_payload: Dict[str, Any]) -> List:
    """
    处理附件数据，返回附件信息列表
    
    Args:
        client_payload: GitHub client_payload 数据
        
    Returns:
        List: 附件信息列表
    """
    logger = logging.getLogger(__name__)
    attachments = []
    
    # 获取附件目录
    attachments_dir = os.environ.get('ATTACHMENTS_DIR', './temp_attachments')
    
    # 检查是否有附件数据
    attachment_data = client_payload.get('attachments', [])
    if not attachment_data:
        return attachments
    
    logger.info(f"发现 {len(attachment_data)} 个附件")
    
    # 检查附件目录是否存在
    if not os.path.exists(attachments_dir):
        logger.warning(f"附件目录不存在: {attachments_dir}")
        return attachments
    
    # 导入附件信息类
    from notification_handler import AttachmentInfo
    
    # 处理每个附件
    for attachment in attachment_data:
        filename = attachment.get('filename', 'attachment')
        filepath = os.path.join(attachments_dir, filename)
        content_type = attachment.get('content_type', 'application/octet-stream')
        
        # 检查文件是否存在
        if os.path.exists(filepath):
            attachments.append(AttachmentInfo(
                filename=filename,
                filepath=filepath,
                content_type=content_type
            ))
            logger.info(f"附件已准备: {filename} ({content_type})")
        else:
            logger.warning(f"附件文件不存在: {filepath}")
    
    return attachments


def validate_event_data(event_data: Dict[str, Any]) -> bool:
    """
    验证事件数据的完整性和有效性
    
    Args:
        event_data: GitHub repository_dispatch 事件数据
        
    Returns:
        bool: 验证是否通过
    """
    logger = logging.getLogger(__name__)
    
    # 检查基本结构
    if not isinstance(event_data, dict):
        logger.error("事件数据不是有效的字典格式")
        return False
    
    # 检查 client_payload
    client_payload = event_data.get('client_payload', {})
    if not isinstance(client_payload, dict):
        logger.error("client_payload 不是有效的字典格式")
        return False
    
    # 检查必需字段
    required_fields = ['title', 'content']
    for field in required_fields:
        if field not in client_payload:
            logger.error(f"缺少必需字段: {field}")
            return False
        if not client_payload[field]:
            logger.warning(f"字段 {field} 为空")
    
    # 检查可选字段的有效性
    source = client_payload.get('source', 'unknown')
    if source not in ['glados', 'airport', 'unknown']:
        logger.warning(f"未知的事件来源: {source}")
    
    return True


def log_event_details(event_data: Dict[str, Any]):
    """
    记录事件详细信息用于调试和监控
    
    Args:
        event_data: GitHub repository_dispatch 事件数据
    """
    logger = logging.getLogger(__name__)
    
    try:
        # 记录基本事件信息
        action = event_data.get('action', 'unknown')
        sender = event_data.get('sender', {}).get('login', 'unknown')
        repository = event_data.get('repository', {}).get('full_name', 'unknown')
        
        logger.info(f"接收到跨仓库通信事件:")
        logger.info(f"  - 动作类型: {action}")
        logger.info(f"  - 发送者: {sender}")
        logger.info(f"  - 源仓库: {repository}")
        logger.info(f"  - 接收时间: {datetime.now().isoformat()}")
        
        # 记录客户端负载信息
        client_payload = event_data.get('client_payload', {})
        if client_payload:
            logger.info(f"  - 通知标题: {client_payload.get('title', 'N/A')}")
            logger.info(f"  - 内容长度: {len(client_payload.get('content', ''))}")
            logger.info(f"  - 事件来源: {client_payload.get('source', 'unknown')}")
            logger.info(f"  - 时间戳: {client_payload.get('timestamp', 'N/A')}")
        
    except Exception as e:
        logger.error(f"记录事件详情时发生错误: {e}")


def main():
    """主入口函数，处理 GitHub Actions 事件"""
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=== 通知服务启动 ===")
        
        # 从环境变量获取事件数据
        event_name = os.environ.get('GITHUB_EVENT_NAME', '')
        event_path = os.environ.get('GITHUB_EVENT_PATH', '')
        
        logger.info(f"GitHub 事件名称: {event_name}")
        logger.info(f"事件数据路径: {event_path}")
        
        # 验证事件类型
        if event_name != 'repository_dispatch':
            logger.error(f"不支持的事件类型: {event_name}")
            logger.info("支持的事件类型: repository_dispatch")
            sys.exit(1)
            
        # 验证事件数据文件
        if not event_path:
            logger.error("未设置 GITHUB_EVENT_PATH 环境变量")
            sys.exit(1)
            
        if not os.path.exists(event_path):
            logger.error(f"事件数据文件不存在: {event_path}")
            sys.exit(1)
            
        # 读取和解析事件数据
        logger.info("读取事件数据...")
        try:
            with open(event_path, 'r', encoding='utf-8') as f:
                event_data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"事件数据 JSON 解析失败: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"读取事件数据文件失败: {e}")
            sys.exit(1)
        
        # 记录事件详情
        log_event_details(event_data)
        
        # 验证事件数据
        if not validate_event_data(event_data):
            logger.error("事件数据验证失败")
            sys.exit(1)
        
        logger.info("事件数据验证通过")
        
        # 初始化配置管理器和通知处理器
        logger.info("初始化通知服务组件...")
        config_manager = ConfigManager()
        notification_handler = NotificationHandler(config_manager)
        
        # 检查可用的通知器
        active_notifiers = notification_handler.get_active_notifiers()
        logger.info(f"发现 {len(active_notifiers)} 个已配置的通知器:")
        for notifier in active_notifiers:
            logger.info(f"  - {notifier.get_name()}")
        
        if not active_notifiers:
            logger.warning("没有配置任何通知器，通知将不会发送")
        
        # 处理通知请求
        logger.info("开始处理通知请求...")
        notification_handler.process_github_event(event_data)
        
        logger.info("=== 通知服务完成 ===")
        
    except KeyboardInterrupt:
        logger.info("接收到中断信号，正在退出...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"处理通知请求时发生未预期的错误: {e}")
        logger.exception("详细错误信息:")
        sys.exit(1)


if __name__ == "__main__":
    main()