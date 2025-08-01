# 通知服务配置说明

## 概述

通知服务支持多种通知渠道，你可以通过环境变量灵活控制哪些渠道启用。

## 配置方式

### 1. 启用/禁用通知渠道

通过设置环境变量 `ENABLE_<渠道名>=true/false` 来控制渠道启用状态：

```bash
# 启用SMTP邮件通知
ENABLE_SMTP=true

# 启用Bark推送
ENABLE_BARK=true

# 禁用钉钉通知
ENABLE_DINGTALK=false
```

### 2. 配置认证信息

每个通知渠道都需要相应的认证信息，参考 `.env.example` 文件。

## 支持的通知渠道

| 渠道名称 | 环境变量 | 必需配置 | 可选配置 | 描述 |
|---------|---------|---------|---------|------|
| bark | `ENABLE_BARK` | `BARK_PUSH` | `BARK_ARCHIVE`, `BARK_GROUP`, `BARK_SOUND`, `BARK_ICON` | Bark iOS推送通知 |
| console | `ENABLE_CONSOLE` | 无 | `CONSOLE` | 控制台输出 |
| dingtalk | `ENABLE_DINGTALK` | `DD_BOT_SECRET`, `DD_BOT_TOKEN` | 无 | 钉钉机器人通知 |
| feishu | `ENABLE_FEISHU` | `FSKEY` | 无 | 飞书机器人通知 |
| wecom_app | `ENABLE_WECOM_APP` | `QYWX_AM` | 无 | 企业微信应用通知 |
| wecom_bot | `ENABLE_WECOM_BOT` | `QYWX_KEY` | 无 | 企业微信机器人通知 |
| telegram | `ENABLE_TELEGRAM` | `TG_BOT_TOKEN`, `TG_USER_ID` | `TG_API_HOST`, `TG_PROXY_*` | Telegram机器人通知 |
| serverchan | `ENABLE_SERVERCHAN` | `PUSH_KEY` | 无 | Server酱通知 |
| serverchan_legacy | `ENABLE_SERVERCHAN_LEGACY` | `SCKEY` | 无 | Server酱通知(旧版) |
| pushdeer | `ENABLE_PUSHDEER` | `DEER_KEY` | `DEER_URL` | PushDeer通知 |
| pushplus | `ENABLE_PUSHPLUS` | `PUSH_PLUS_TOKEN` | `PUSH_PLUS_USER` | Push+通知 |
| qmsg | `ENABLE_QMSG` | `QMSG_KEY`, `QMSG_TYPE` | 无 | Qmsg酱通知 |
| gotify | `ENABLE_GOTIFY` | `GOTIFY_URL`, `GOTIFY_TOKEN` | `GOTIFY_PRIORITY` | Gotify通知 |
| igot | `ENABLE_IGOT` | `IGOT_PUSH_KEY` | 无 | iGot通知 |
| smtp | `ENABLE_SMTP` | `SMTP_SERVER`, `SMTP_SSL`, `SMTP_EMAIL`, `SMTP_PASSWORD`, `SMTP_NAME` | 无 | SMTP邮件通知 |

## 默认配置

如果不设置 `ENABLE_<渠道名>` 环境变量，系统会使用 `notification_config.json` 中的默认值：

- `console`: 默认启用
- `smtp`: 默认启用  
- 其他渠道: 默认禁用

## 配置检查

使用配置检查工具查看当前状态：

```bash
python check_config.py
```

这会显示：
- 所有渠道的启用状态
- 配置状态
- 活跃渠道列表
- 配置建议

## 示例配置

### 只使用邮件通知
```bash
ENABLE_SMTP=true
ENABLE_CONSOLE=false

SMTP_SERVER=smtp.gmail.com
SMTP_SSL=true
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_NAME=通知服务
```

### 使用多种通知方式
```bash
ENABLE_SMTP=true
ENABLE_BARK=true
ENABLE_TELEGRAM=true

# SMTP配置
SMTP_SERVER=smtp.gmail.com
SMTP_SSL=true
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_NAME=通知服务

# Bark配置
BARK_PUSH=https://api.day.app/your-key/

# Telegram配置
TG_BOT_TOKEN=your-bot-token
TG_USER_ID=your-user-id
```

## 注意事项

1. **启用状态**: 渠道必须同时启用且配置完成才会生效
2. **环境变量优先级**: 环境变量设置优先于配置文件默认值
3. **配置验证**: 系统会自动验证必需的配置项是否存在
4. **错误处理**: 单个渠道失败不会影响其他渠道的通知发送

## 故障排除

1. **渠道未生效**: 检查是否同时启用且配置完成
2. **配置错误**: 使用 `python check_config.py` 检查配置状态
3. **认证失败**: 验证认证信息是否正确
4. **网络问题**: 检查网络连接和代理设置