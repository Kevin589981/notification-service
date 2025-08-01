# 环境变量对应关系修复总结

## 问题描述

在 GitHub Actions workflow 文件 (`.github/workflows/notification-service.yml`) 中设置的环境变量与 `config_manager.py` 中使用的环境变量没有一一对应，导致通知服务可能无法正确获取配置。

## 修复内容

### 修复前的问题

**yml 文件中的环境变量（部分不匹配）：**
- `BARK_URL`, `BARK_KEY` ❌
- `SENDKEY` ❌ 
- `SMTP_PORT`, `SMTP_USER`, `SMTP_TO` ❌
- `QMSG_QQ` ❌
- 缺少多个可选配置变量 ❌

**config_manager.py 中的环境变量：**
- `BARK_PUSH`, `BARK_ARCHIVE`, `BARK_GROUP`, `BARK_SOUND`, `BARK_ICON` ✅
- `PUSH_KEY` ✅
- `SMTP_SERVER`, `SMTP_SSL`, `SMTP_EMAIL`, `SMTP_PASSWORD`, `SMTP_NAME` ✅
- `QMSG_TYPE` ✅
- 包含所有通知器的完整配置变量 ✅

### 修复后的对应关系

现在 yml 文件中的环境变量与 config_manager.py 完全匹配：

#### Bark 通知配置
- `BARK_PUSH`: Bark 推送 URL
- `BARK_ARCHIVE`: Bark 归档设置
- `BARK_GROUP`: Bark 分组设置
- `BARK_SOUND`: Bark 声音设置
- `BARK_ICON`: Bark 图标设置

#### 钉钉通知配置
- `DD_BOT_TOKEN`: 钉钉机器人 Token
- `DD_BOT_SECRET`: 钉钉机器人密钥

#### 飞书通知配置
- `FSKEY`: 飞书机器人密钥

#### 企业微信通知配置
- `QYWX_AM`: 企业微信应用配置
- `QYWX_KEY`: 企业微信机器人密钥

#### Telegram 通知配置
- `TG_BOT_TOKEN`: Telegram 机器人 Token
- `TG_USER_ID`: Telegram 用户 ID
- `TG_API_HOST`: Telegram API 主机
- `TG_PROXY_AUTH`: Telegram 代理认证
- `TG_PROXY_HOST`: Telegram 代理主机
- `TG_PROXY_PORT`: Telegram 代理端口

#### Server酱通知配置
- `PUSH_KEY`: Server酱新版密钥
- `SCKEY`: Server酱旧版密钥

#### PushDeer 通知配置
- `DEER_KEY`: PushDeer 密钥
- `DEER_URL`: PushDeer 服务器 URL

#### Push+ 通知配置
- `PUSH_PLUS_TOKEN`: Push+ 通知 Token
- `PUSH_PLUS_USER`: Push+ 用户标识

#### Qmsg 通知配置
- `QMSG_KEY`: Qmsg 通知密钥
- `QMSG_TYPE`: Qmsg 消息类型

#### Gotify 通知配置
- `GOTIFY_URL`: Gotify 服务器 URL
- `GOTIFY_TOKEN`: Gotify 应用 Token
- `GOTIFY_PRIORITY`: Gotify 消息优先级

#### iGot 通知配置
- `IGOT_PUSH_KEY`: iGot 推送密钥

#### SMTP 邮件通知配置
- `SMTP_SERVER`: SMTP 服务器地址
- `SMTP_SSL`: 是否启用 SSL
- `SMTP_EMAIL`: SMTP 邮箱地址
- `SMTP_PASSWORD`: SMTP 邮箱密码
- `SMTP_NAME`: 发件人名称

#### 其他配置
- `HITOKOTO`: 是否启用一言
- `CONSOLE`: 是否启用控制台输出
- `SKIP_PUSH_TITLE`: 跳过推送的标题列表

## 修复的文件

1. **`.github/workflows/notification-service.yml`**
   - 更新了所有环境变量名称以匹配 config_manager.py
   - 添加了缺失的可选配置变量
   - 移除了不存在的环境变量

2. **`GITHUB_ACTIONS_SETUP.md`**
   - 更新了文档中的环境变量说明
   - 添加了详细的配置分类和说明
   - 提供了正确的密钥配置指南

## 验证工具

创建了 `verify_env_vars.py` 脚本来自动验证环境变量对应关系：

```bash
python verify_env_vars.py
```

该脚本会：
- 从 yml 文件中提取环境变量
- 从 config_manager.py 中提取环境变量
- 比较两者的差异
- 提供修复建议

## 验证结果

✅ **所有 36 个环境变量完全匹配**
✅ **所有单元测试通过**
✅ **跨仓库通信功能正常工作**

## 影响

修复后的配置确保了：
1. GitHub Actions workflow 能够正确传递所有必要的环境变量
2. 通知服务能够访问所有配置的通知器
3. 用户可以根据需要配置任意组合的通知服务
4. 配置文档与实际实现保持一致

## 使用建议

1. 用户只需要配置他们实际使用的通知服务对应的环境变量
2. 未配置的通知服务会被自动跳过
3. 建议定期运行 `verify_env_vars.py` 来确保配置一致性
4. 在添加新的通知器时，确保同时更新 yml 文件和 config_manager.py