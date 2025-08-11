![License](https://img.shields.io/badge/License-MIT-blue.svg)

# 通知服务模块

独立的通知服务模块，用于处理来自签到模块的通知请求，支持多种通知方式。

## 功能特性

- 支持多种通知方式：Bark、钉钉、飞书、企业微信、Telegram、Server酱、SMTP邮件等
- 基于 GitHub Actions 的事件处理
- **支持文件附件发送（仅SMTP邮件）**
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

### 基本通知

通过 GitHub Actions 的 repository_dispatch 事件触发通知服务：

```bash
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/YOUR_USERNAME/YOUR_REPO/dispatches \
  -d '{
    "event_type": "send-notification",
    "client_payload": {
      "title": "通知标题",
      "content": "通知内容",
      "source": "your_app"
    }
  }'
```

### 带附件的通知（仅SMTP邮件支持）

```bash
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/YOUR_USERNAME/YOUR_REPO/dispatches \
  -d '{
    "event_type": "send-notification",
    "client_payload": {
      "title": "带附件的通知",
      "content": "请查看附件中的报告",
      "source": "monitoring",
      "attachments": [
        {
          "filename": "report.pdf",
          "content": "base64编码的文件内容",
          "encoding": "base64",
          "content_type": "application/pdf"
        }
      ]
    }
  }'
```

### 附件功能说明

- **支持范围**: 仅SMTP邮件通知器支持附件，其他通知器会忽略附件
- **文件大小**: 单个附件最大25MB
- **编码方式**: 
  - 二进制文件使用base64编码
  - 文本文件可直接传递内容
- **支持格式**: PDF、图片、Office文档、文本文件等

详细使用示例请参考：
- `attachment_example.md` - 附件功能详细说明
- `send_notification_with_attachment.py` - Python发送示例
- `test_attachment_functionality.py` - 功能测试脚本

## 配置说明

所有配置通过环境变量设置，支持的通知方式配置请参考各个通知器的说明。

### SMTP邮件配置（支持附件）

```bash
SMTP_SERVER=smtp.gmail.com:587
SMTP_SSL=true
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_NAME=通知服务
```
