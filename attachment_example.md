# 文件附件功能使用说明

## 功能概述

现在通知服务支持在GitHub Actions触发时接收和发送文件附件。此功能仅在SMTP邮件通知器中有效。

## 使用方法

### 1. 发送带附件的通知请求

通过repository_dispatch事件发送通知时，可以在client_payload中包含attachments字段：

```json
{
  "event_type": "send-notification",
  "client_payload": {
    "title": "带附件的通知",
    "content": "这是一个包含附件的通知消息",
    "source": "test",
    "timestamp": "2025-01-11T10:00:00Z",
    "attachments": [
      {
        "filename": "report.pdf",
        "content": "base64编码的文件内容",
        "encoding": "base64",
        "content_type": "application/pdf"
      },
      {
        "filename": "data.txt",
        "content": "这是一个文本文件的内容",
        "encoding": "text",
        "content_type": "text/plain"
      }
    ]
  }
}
```

### 2. 附件字段说明

- `filename`: 附件文件名
- `content`: 文件内容（base64编码或纯文本）
- `encoding`: 编码方式（"base64" 或 "text"）
- `content_type`: MIME类型（可选，默认为 "application/octet-stream"）

### 3. 支持的附件类型

- 文本文件（.txt, .md, .log等）
- PDF文档
- 图片文件（.jpg, .png, .gif等）
- Office文档（.doc, .xls, .ppt等）
- 压缩文件（.zip, .rar等）
- 其他二进制文件

### 4. 限制说明

- 单个附件最大25MB
- 只有SMTP邮件通知器支持附件
- 其他通知器会忽略附件，只发送文本内容
- 附件会在处理完成后自动清理

## 示例脚本

### 发送带附件的通知

```bash
#!/bin/bash

# 准备附件内容（base64编码）
ATTACHMENT_CONTENT=$(base64 -w 0 /path/to/your/file.pdf)

# 发送通知请求
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/YOUR_USERNAME/YOUR_REPO/dispatches \
  -d '{
    "event_type": "send-notification",
    "client_payload": {
      "title": "系统报告",
      "content": "请查看附件中的系统报告",
      "source": "monitoring",
      "attachments": [
        {
          "filename": "system_report.pdf",
          "content": "'$ATTACHMENT_CONTENT'",
          "encoding": "base64",
          "content_type": "application/pdf"
        }
      ]
    }
  }'
```

### Python示例

```python
import requests
import base64
import json

def send_notification_with_attachment(token, repo, file_path):
    # 读取文件并编码
    with open(file_path, 'rb') as f:
        file_content = base64.b64encode(f.read()).decode('utf-8')
    
    # 构建请求数据
    payload = {
        "event_type": "send-notification",
        "client_payload": {
            "title": "带附件的通知",
            "content": "请查看附件",
            "source": "python_script",
            "attachments": [
                {
                    "filename": "attachment.pdf",
                    "content": file_content,
                    "encoding": "base64",
                    "content_type": "application/pdf"
                }
            ]
        }
    }
    
    # 发送请求
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }
    
    response = requests.post(
        f"https://api.github.com/repos/{repo}/dispatches",
        headers=headers,
        json=payload
    )
    
    return response.status_code == 204

# 使用示例
# send_notification_with_attachment("your_token", "username/repo", "report.pdf")
```

## 注意事项

1. 确保SMTP邮件服务器支持发送附件
2. 大文件可能导致邮件发送失败，建议控制附件大小
3. 某些邮件服务商可能会过滤特定类型的附件
4. 附件内容需要正确的base64编码
5. 文本文件可以直接传递内容，无需base64编码