#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
负责安全地获取和管理存储在环境变量中的各种通知服务密钥
"""

import os
import re
import json
from typing import Any, Dict, Optional


class ConfigManager:
    """配置管理器，用于安全地获取和管理配置信息"""
    
    def __init__(self):
        """初始化配置管理器"""
        self._config_cache = {}
        self._notification_config = {}
        self._load_notification_config()
        self._load_config()
    
    def _load_notification_config(self) -> None:
        """加载通知配置文件"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'notification_config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                self._notification_config = json.load(f)
        except Exception as e:
            print(f"加载通知配置文件失败: {e}")
            self._notification_config = {}
    
    def _load_config(self) -> None:
        """从环境变量加载配置"""
        # 通知服务相关配置
        self._config_cache = {
            # Bark 推送配置
            'BARK_PUSH': os.environ.get('BARK_PUSH') or None,
            'BARK_ARCHIVE': os.environ.get('BARK_ARCHIVE') or None,
            'BARK_GROUP': os.environ.get('BARK_GROUP') or None,
            'BARK_SOUND': os.environ.get('BARK_SOUND') or None,
            'BARK_ICON': os.environ.get('BARK_ICON') or None,
            
            # 钉钉机器人配置
            'DD_BOT_SECRET': os.environ.get('DD_BOT_SECRET') or None,
            'DD_BOT_TOKEN': os.environ.get('DD_BOT_TOKEN') or None,
            
            # 飞书机器人配置
            'FSKEY': os.environ.get('FSKEY') or None,
            
            # 企业微信配置
            'QYWX_AM': os.environ.get('QYWX_AM') or None,
            'QYWX_KEY': os.environ.get('QYWX_KEY') or None,
            
            # Telegram 配置
            'TG_BOT_TOKEN': os.environ.get('TG_BOT_TOKEN') or None,
            'TG_USER_ID': os.environ.get('TG_USER_ID') or None,
            'TG_API_HOST': os.environ.get('TG_API_HOST') or None,
            'TG_PROXY_AUTH': os.environ.get('TG_PROXY_AUTH') or None,
            'TG_PROXY_HOST': os.environ.get('TG_PROXY_HOST') or None,
            'TG_PROXY_PORT': os.environ.get('TG_PROXY_PORT') or None,
            
            # Server酱配置
            'PUSH_KEY': os.environ.get('PUSH_KEY') or None,
            'SCKEY': os.environ.get('SCKEY') or None,  # 兼容旧版配置
            
            # PushDeer 配置
            'DEER_KEY': os.environ.get('DEER_KEY') or None,
            'DEER_URL': os.environ.get('DEER_URL') or None,
            
            # Push+ 配置
            'PUSH_PLUS_TOKEN': os.environ.get('PUSH_PLUS_TOKEN') or None,
            'PUSH_PLUS_USER': os.environ.get('PUSH_PLUS_USER') or None,
            
            # qmsg 配置
            'QMSG_KEY': os.environ.get('QMSG_KEY') or None,
            'QMSG_TYPE': os.environ.get('QMSG_TYPE') or None,
            
            # Gotify 配置
            'GOTIFY_URL': os.environ.get('GOTIFY_URL') or None,
            'GOTIFY_TOKEN': os.environ.get('GOTIFY_TOKEN') or None,
            'GOTIFY_PRIORITY': int(os.environ.get('GOTIFY_PRIORITY') or '0'),
            
            # iGot 配置
            'IGOT_PUSH_KEY': os.environ.get('IGOT_PUSH_KEY') or None,
            
            # SMTP 邮件配置
            'SMTP_SERVER': os.environ.get('SMTP_SERVER') or None,
            'SMTP_SSL': os.environ.get('SMTP_SSL') or None,
            'SMTP_EMAIL': os.environ.get('SMTP_EMAIL') or None,
            'SMTP_PASSWORD': os.environ.get('SMTP_PASSWORD') or None,
            'SMTP_NAME': os.environ.get('SMTP_NAME') or None,
            
            # 其他配置
            'HITOKOTO': os.environ.get('HITOKOTO', 'false').lower() == 'true',
            'CONSOLE': os.environ.get('CONSOLE', 'true').lower() == 'true',
            'SKIP_PUSH_TITLE': os.environ.get('SKIP_PUSH_TITLE') or None,
        }
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        安全获取配置值
        
        Args:
            key: 配置键名
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        try:
            return self._config_cache.get(key, default)
        except Exception as e:
            print(f"获取配置 {key} 时发生错误: {e}")
            return default
    
    def is_configured(self, service: str) -> bool:
        """
        检查服务是否已配置
        
        Args:
            service: 服务名称
            
        Returns:
            是否已配置
        """
        service_configs = {
            'bark': ['BARK_PUSH'],
            'console': [],  # 控制台输出不需要配置
            'dingtalk': ['DD_BOT_SECRET', 'DD_BOT_TOKEN'],
            'feishu': ['FSKEY'],
            'wecom_app': ['QYWX_AM'],
            'wecom_bot': ['QYWX_KEY'],
            'telegram': ['TG_BOT_TOKEN', 'TG_USER_ID'],
            'serverchan': ['PUSH_KEY'],
            'serverchan_legacy': ['SCKEY'],
            'pushdeer': ['DEER_KEY'],
            'pushplus': ['PUSH_PLUS_TOKEN'],
            'qmsg': ['QMSG_KEY', 'QMSG_TYPE'],
            'gotify': ['GOTIFY_URL', 'GOTIFY_TOKEN'],
            'igot': ['IGOT_PUSH_KEY'],
            'smtp': ['SMTP_SERVER', 'SMTP_SSL', 'SMTP_EMAIL', 'SMTP_PASSWORD', 'SMTP_NAME'],
        }
        
        required_keys = service_configs.get(service, [])
        if service not in service_configs:
            return False
        
        # 如果没有必需的配置项，则认为已配置（如console）
        if not required_keys:
            return True
            
        return all(self.get_config(key) for key in required_keys)
    
    def get_notifier_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有通知器配置
        
        Returns:
            通知器配置字典
        """
        configs = {}
        
        # Bark 配置
        if self.is_configured('bark'):
            configs['bark'] = {
                'push_url': self.get_config('BARK_PUSH'),
                'archive': self.get_config('BARK_ARCHIVE'),
                'group': self.get_config('BARK_GROUP'),
                'sound': self.get_config('BARK_SOUND'),
                'icon': self.get_config('BARK_ICON'),
            }
        
        # 钉钉配置
        if self.is_configured('dingding'):
            configs['dingding'] = {
                'secret': self.get_config('DD_BOT_SECRET'),
                'token': self.get_config('DD_BOT_TOKEN'),
            }
        
        # 飞书配置
        if self.is_configured('feishu'):
            configs['feishu'] = {
                'key': self.get_config('FSKEY'),
            }
        
        # 企业微信应用配置
        if self.is_configured('wecom_app'):
            configs['wecom_app'] = {
                'config': self.get_config('QYWX_AM'),
            }
        
        # 企业微信机器人配置
        if self.is_configured('wecom_bot'):
            configs['wecom_bot'] = {
                'key': self.get_config('QYWX_KEY'),
            }
        
        # Telegram 配置
        if self.is_configured('telegram'):
            configs['telegram'] = {
                'bot_token': self.get_config('TG_BOT_TOKEN'),
                'user_id': self.get_config('TG_USER_ID'),
                'api_host': self.get_config('TG_API_HOST'),
                'proxy_auth': self.get_config('TG_PROXY_AUTH'),
                'proxy_host': self.get_config('TG_PROXY_HOST'),
                'proxy_port': self.get_config('TG_PROXY_PORT'),
            }
        
        # Server酱配置（新版）
        if self.is_configured('serverchan'):
            configs['serverchan'] = {
                'key': self.get_config('PUSH_KEY'),
            }
        
        # Server酱配置（旧版兼容）
        if self.is_configured('serverchan_legacy'):
            configs['serverchan_legacy'] = {
                'key': self.get_config('SCKEY'),
            }
        
        # PushDeer 配置
        if self.is_configured('pushdeer'):
            configs['pushdeer'] = {
                'key': self.get_config('DEER_KEY'),
                'url': self.get_config('DEER_URL'),
            }
        
        # Push+ 配置
        if self.is_configured('pushplus'):
            configs['pushplus'] = {
                'token': self.get_config('PUSH_PLUS_TOKEN'),
                'user': self.get_config('PUSH_PLUS_USER'),
            }
        
        # qmsg 配置
        if self.is_configured('qmsg'):
            configs['qmsg'] = {
                'key': self.get_config('QMSG_KEY'),
                'type': self.get_config('QMSG_TYPE'),
            }
        
        # Gotify 配置
        if self.is_configured('gotify'):
            configs['gotify'] = {
                'url': self.get_config('GOTIFY_URL'),
                'token': self.get_config('GOTIFY_TOKEN'),
                'priority': self.get_config('GOTIFY_PRIORITY'),
            }
        
        # iGot 配置
        if self.is_configured('igot'):
            configs['igot'] = {
                'key': self.get_config('IGOT_PUSH_KEY'),
            }
        
        # SMTP 配置
        if self.is_configured('smtp'):
            configs['smtp'] = {
                'server': self.get_config('SMTP_SERVER'),
                'ssl': self.get_config('SMTP_SSL'),
                'email': self.get_config('SMTP_EMAIL'),
                'password': self.get_config('SMTP_PASSWORD'),
                'name': self.get_config('SMTP_NAME'),
            }
        
        return configs
    
    def mask_sensitive_value(self, value: str) -> str:
        """
        遮蔽敏感信息用于日志
        
        Args:
            value: 原始值
            
        Returns:
            遮蔽后的值
        """
        if not value or len(value) <= 6:
            return '*' * len(value) if value else ''
        
        # 保留前3位和后3位，中间用*替代
        return value[:3] + '*' * (len(value) - 6) + value[-3:]
    
    def validate_config(self) -> Dict[str, str]:
        """
        验证配置并返回错误信息
        
        Returns:
            配置错误信息字典
        """
        errors = {}
        
        # 检查 Server酱 配置格式
        push_key = self.get_config('PUSH_KEY')
        sckey = self.get_config('SCKEY')
        
        if push_key and not (push_key.startswith('SCT') or re.match(r'^[a-zA-Z0-9]+$', push_key)):
            errors['PUSH_KEY'] = 'PUSH_KEY 格式不正确'
        
        if sckey and not re.match(r'^[a-zA-Z0-9]+$', sckey):
            errors['SCKEY'] = 'SCKEY 格式不正确'
        
        # 检查企业微信应用配置格式
        qywx_am = self.get_config('QYWX_AM')
        if qywx_am:
            parts = qywx_am.split(',')
            if len(parts) < 4 or len(parts) > 5:
                errors['QYWX_AM'] = 'QYWX_AM 配置格式错误，应为：corpid,corpsecret,touser,agentid[,media_id]'
        
        # 检查 SMTP SSL 配置
        smtp_ssl = self.get_config('SMTP_SSL')
        if smtp_ssl and smtp_ssl.lower() not in ['true', 'false']:
            errors['SMTP_SSL'] = 'SMTP_SSL 应设置为 true 或 false'
        
        return errors
    
    def is_channel_enabled(self, channel: str) -> bool:
        """
        检查通知渠道是否启用
        
        Args:
            channel: 通知渠道名称
            
        Returns:
            是否启用
        """
        # 从环境变量获取启用状态，格式如：ENABLE_BARK=true
        env_key = f"ENABLE_{channel.upper()}"
        env_value = os.environ.get(env_key, '').lower()
        
        if env_value in ['true', '1', 'yes', 'on']:
            return True
        elif env_value in ['false', '0', 'no', 'off']:
            return False
        
        # 如果环境变量未设置，使用配置文件中的默认值
        channels = self._notification_config.get('notification_channels', {})
        channel_config = channels.get(channel, {})
        return channel_config.get('enabled', False)
    
    def get_enabled_channels(self) -> list:
        """
        获取所有启用的通知渠道
        
        Returns:
            启用的通知渠道列表
        """
        enabled_channels = []
        channels = self._notification_config.get('notification_channels', {})
        
        for channel_name in channels.keys():
            if self.is_channel_enabled(channel_name) and self.is_configured(channel_name):
                enabled_channels.append(channel_name)
        
        return enabled_channels
    
    def get_channel_info(self, channel: str) -> Dict[str, Any]:
        """
        获取通知渠道信息
        
        Args:
            channel: 通知渠道名称
            
        Returns:
            通知渠道信息
        """
        channels = self._notification_config.get('notification_channels', {})
        return channels.get(channel, {})
    
    def get_all_channels_status(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有通知渠道的状态
        
        Returns:
            所有通知渠道的状态信息
        """
        status = {}
        channels = self._notification_config.get('notification_channels', {})
        
        for channel_name, channel_config in channels.items():
            status[channel_name] = {
                'enabled': self.is_channel_enabled(channel_name),
                'configured': self.is_configured(channel_name),
                'description': channel_config.get('description', ''),
                'required_env': channel_config.get('required_env', []),
                'optional_env': channel_config.get('optional_env', [])
            }
        
        return status