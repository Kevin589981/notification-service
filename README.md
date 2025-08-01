# 通知服务模块

独立的通知服务模块，用于处理来自签到模块的通知请求，支持多种通知方式。

## 功能特性

- 支持多种通知方式：Bark、钉钉、飞书、企业微信、Telegram、Server酱等
- 基于 GitHub Actions 的事件处理
- 安全的密钥管理
- 并发通知发送
- 错误处理和重试机制

## 项目结构

```
notification-service/
├── main.py                 # 主入口文件
├── config_manager.py       # 配置管理模块
├── notification_handler.py # 通知处理器
├── notifiers/              # 通知器实现
│   ├── __init__.py
│   └── base_notifier.py    # 基础通知器接口
├── tests/                  # 测试文件
├── requirements.txt        # 依赖包
└── README.md              # 说明文档
```

## 使用方法

通过 GitHub Actions 的 repository_dispatch 事件触发通知服务。

## 配置说明

所有配置通过环境变量设置，支持的通知方式配置请参考各个通知器的说明。