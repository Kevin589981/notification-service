# GitHub Actions 通知服务设置指南

## 概述

本文档描述如何设置和使用通知服务的 GitHub Actions workflow，实现跨仓库的自动化通知功能。

## Workflow 配置

### 文件位置
`.github/workflows/notification-service.yml`

### 触发方式
- **事件类型**: `repository_dispatch`
- **动作类型**: `send-notification`

### 环境变量配置

在 GitHub 仓库的 Settings > Secrets and variables > Actions 中配置以下密钥：

#### 必需的密钥
- `REPO_ACCESS_TOKEN`: 用于跨仓库触发的 GitHub Personal Access Token

#### 通知服务密钥（根据需要配置）

**Bark 通知配置**
- `BARK_PUSH`: Bark 推送 URL
- `BARK_ARCHIVE`: Bark 归档设置（可选）
- `BARK_GROUP`: Bark 分组设置（可选）
- `BARK_SOUND`: Bark 声音设置（可选）
- `BARK_ICON`: Bark 图标设置（可选）

**钉钉通知配置**
- `DD_BOT_TOKEN`: 钉钉机器人 Token
- `DD_BOT_SECRET`: 钉钉机器人密钥

**飞书通知配置**
- `FSKEY`: 飞书机器人密钥

**企业微信通知配置**
- `QYWX_AM`: 企业微信应用配置（格式：corpid,corpsecret,touser,agentid[,media_id]）
- `QYWX_KEY`: 企业微信机器人密钥

**Telegram 通知配置**
- `TG_BOT_TOKEN`: Telegram 机器人 Token
- `TG_USER_ID`: Telegram 用户 ID
- `TG_API_HOST`: Telegram API 主机（可选）
- `TG_PROXY_AUTH`: Telegram 代理认证（可选）
- `TG_PROXY_HOST`: Telegram 代理主机（可选）
- `TG_PROXY_PORT`: Telegram 代理端口（可选）

**Server酱通知配置**
- `PUSH_KEY`: Server酱新版密钥
- `SCKEY`: Server酱旧版密钥（兼容）

**PushDeer 通知配置**
- `DEER_KEY`: PushDeer 密钥
- `DEER_URL`: PushDeer 服务器 URL（可选）

**Push+ 通知配置**
- `PUSH_PLUS_TOKEN`: Push+ 通知 Token
- `PUSH_PLUS_USER`: Push+ 用户标识（可选）

**Qmsg 通知配置**
- `QMSG_KEY`: Qmsg 通知密钥
- `QMSG_TYPE`: Qmsg 消息类型

**Gotify 通知配置**
- `GOTIFY_URL`: Gotify 服务器 URL
- `GOTIFY_TOKEN`: Gotify 应用 Token
- `GOTIFY_PRIORITY`: Gotify 消息优先级（可选，默认为0）

**iGot 通知配置**
- `IGOT_PUSH_KEY`: iGot 推送密钥

**SMTP 邮件通知配置**
- `SMTP_SERVER`: SMTP 服务器地址
- `SMTP_SSL`: 是否启用 SSL（true/false）
- `SMTP_EMAIL`: SMTP 邮箱地址
- `SMTP_PASSWORD`: SMTP 邮箱密码
- `SMTP_NAME`: 发件人名称

**其他配置**
- `HITOKOTO`: 是否启用一言（true/false）
- `CONSOLE`: 是否启用控制台输出（true/false）
- `SKIP_PUSH_TITLE`: 跳过推送的标题列表（换行分隔）

## 跨仓库触发

### 从签到模块触发通知

在签到模块的 workflow 中添加以下步骤：

```yaml
- name: Trigger Notification Service
  if: always()  # 无论签到成功或失败都发送通知
  uses: peter-evans/repository-dispatch@v2
  with:
    token: ${{ secrets.REPO_ACCESS_TOKEN }}
    repository: your-username/notification-service
    event-type: send-notification
    client-payload: |
      {
        "title": "签到通知",
        "content": "${{ steps.checkin.outputs.result }}",
        "source": "glados",
        "timestamp": "${{ steps.checkin.outputs.timestamp }}"
      }
```

### 事件数据格式

#### client_payload 结构
```json
{
  "title": "通知标题",
  "content": "通知内容",
  "source": "事件来源 (glados|airport|unknown)",
  "timestamp": "ISO 格式时间戳"
}
```

#### 字段说明
- `title` (必需): 通知标题
- `content` (必需): 通知内容
- `source` (可选): 事件来源，用于区分不同的签到模块
- `timestamp` (可选): 事件发生时间

## 使用示例

### GlaDOS 签到通知
```yaml
client-payload: |
  {
    "title": "GlaDOS 签到通知",
    "content": "账号 user@example.com 签到成功！剩余天数：365天",
    "source": "glados",
    "timestamp": "2025-08-01T06:00:00Z"
  }
```

### 机场签到通知
```yaml
client-payload: |
  {
    "title": "机场签到通知", 
    "content": "账号 user@example.com 签到成功！获得流量：100MB",
    "source": "airport",
    "timestamp": "2025-08-01T06:00:00Z"
  }
```

## 监控和调试

### 查看 Workflow 运行日志
1. 进入 GitHub 仓库
2. 点击 "Actions" 标签
3. 选择 "Notification Service" workflow
4. 查看具体运行实例的日志

### 日志内容包括
- 事件接收和验证信息
- 配置的通知器列表
- 每个通知器的发送结果
- 错误信息和调试详情

### 常见问题排查

#### 1. Workflow 未触发
- 检查 `REPO_ACCESS_TOKEN` 是否正确配置
- 确认 token 具有 `repo` 权限
- 验证目标仓库名称是否正确

#### 2. 通知发送失败
- 检查对应通知服务的密钥配置
- 查看 workflow 日志中的错误信息
- 验证通知服务的 API 是否正常

#### 3. 事件数据格式错误
- 确保 `client_payload` 包含必需字段
- 检查 JSON 格式是否正确
- 验证字段值是否为空

## 安全注意事项

1. **密钥管理**
   - 所有敏感信息必须通过 GitHub Secrets 配置
   - 不要在代码中硬编码任何密钥
   - 定期轮换访问令牌

2. **权限控制**
   - `REPO_ACCESS_TOKEN` 应使用最小权限原则
   - 仅授予必要的仓库访问权限

3. **日志安全**
   - 系统会自动遮蔽日志中的敏感信息
   - 避免在通知内容中包含敏感数据

## 测试

### 本地测试
```bash
# 设置环境变量
export GITHUB_EVENT_NAME=repository_dispatch
export GITHUB_EVENT_PATH=sample_event.json

# 运行通知服务
python main.py
```

### 创建测试事件文件
```bash
python test_cross_repo_communication.py create-sample
```

这将创建一个 `sample_event.json` 文件，可用于本地测试。