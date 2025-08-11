#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试附件功能的脚本
"""

import json
import os
import tempfile
import base64
from datetime import datetime

def create_test_event_with_attachments():
    """创建包含附件的测试事件数据"""
    
    # 创建测试附件内容
    test_text_content = "这是一个测试文本文件\n包含多行内容\n用于测试附件功能"
    test_binary_content = b"This is binary content for testing"
    
    # 创建测试事件数据
    event_data = {
        "action": "send-notification",
        "client_payload": {
            "title": "附件功能测试",
            "content": "这是一个测试通知，包含两个附件：一个文本文件和一个二进制文件。",
            "source": "test",
            "timestamp": datetime.now().isoformat(),
            "attachments": [
                {
                    "filename": "test_document.txt",
                    "content": test_text_content,
                    "encoding": "text",
                    "content_type": "text/plain"
                },
                {
                    "filename": "test_binary.dat",
                    "content": base64.b64encode(test_binary_content).decode('utf-8'),
                    "encoding": "base64",
                    "content_type": "application/octet-stream"
                }
            ]
        },
        "repository": {
            "full_name": "test/repo"
        },
        "sender": {
            "login": "test_user"
        }
    }
    
    return event_data

def create_test_attachments_directory(event_data):
    """根据事件数据创建测试附件目录和文件"""
    
    # 创建临时目录
    temp_dir = "./temp_attachments"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 处理附件
    attachments = event_data.get("client_payload", {}).get("attachments", [])
    
    for attachment in attachments:
        filename = attachment.get("filename", "attachment")
        content = attachment.get("content", "")
        encoding = attachment.get("encoding", "base64")
        
        filepath = os.path.join(temp_dir, filename)
        
        if encoding == "base64":
            # 解码base64内容
            try:
                file_content = base64.b64decode(content)
                with open(filepath, 'wb') as f:
                    f.write(file_content)
                print(f"创建二进制附件: {filepath}")
            except Exception as e:
                print(f"创建附件 {filename} 失败: {e}")
        else:
            # 文本内容
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"创建文本附件: {filepath}")
    
    return temp_dir

def test_notification_with_attachments():
    """测试带附件的通知功能"""
    
    print("=== 开始测试附件功能 ===")
    
    try:
        # 创建测试事件数据
        event_data = create_test_event_with_attachments()
        print("✓ 测试事件数据创建成功")
        
        # 创建测试附件文件
        temp_dir = create_test_attachments_directory(event_data)
        print("✓ 测试附件文件创建成功")
        
        # 设置环境变量
        os.environ['ATTACHMENTS_DIR'] = temp_dir
        os.environ['GITHUB_EVENT_NAME'] = 'repository_dispatch'
        
        # 创建临时事件文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(event_data, f, ensure_ascii=False, indent=2)
            event_file = f.name
        
        os.environ['GITHUB_EVENT_PATH'] = event_file
        
        print("✓ 环境变量设置完成")
        print(f"  - ATTACHMENTS_DIR: {temp_dir}")
        print(f"  - GITHUB_EVENT_PATH: {event_file}")
        
        # 导入并测试通知处理器
        from config_manager import ConfigManager
        from notification_handler import NotificationHandler
        
        config_manager = ConfigManager()
        notification_handler = NotificationHandler(config_manager)
        
        print("✓ 通知处理器初始化成功")
        
        # 处理事件
        print("开始处理带附件的通知事件...")
        notification_handler.process_github_event(event_data)
        
        print("✓ 通知事件处理完成")
        
        # 清理临时文件
        os.unlink(event_file)
        
        # 清理附件目录
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        print("✓ 临时文件清理完成")
        print("=== 附件功能测试完成 ===")
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def test_smtp_attachment_functionality():
    """专门测试SMTP附件功能"""
    
    print("=== 测试SMTP附件功能 ===")
    
    try:
        from config_manager import ConfigManager
        from notifiers.smtp import SMTPNotifier
        from notification_handler import AttachmentInfo
        
        config_manager = ConfigManager()
        smtp_notifier = SMTPNotifier(config_manager)
        
        # 检查SMTP是否配置
        if not smtp_notifier.is_configured():
            print("⚠ SMTP未配置，跳过SMTP附件测试")
            return
        
        print("✓ SMTP通知器已配置")
        
        # 创建测试附件
        temp_dir = "./temp_test_attachments"
        os.makedirs(temp_dir, exist_ok=True)
        
        # 创建文本附件
        text_file = os.path.join(temp_dir, "test.txt")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write("这是一个测试附件文件\n用于验证SMTP附件功能")
        
        # 创建附件信息
        attachments = [
            AttachmentInfo(
                filename="test.txt",
                filepath=text_file,
                content_type="text/plain"
            )
        ]
        
        print("✓ 测试附件创建成功")
        
        # 测试发送
        result = smtp_notifier.send_with_attachments(
            "SMTP附件测试",
            "这是一个SMTP附件功能测试邮件，请检查是否收到附件。",
            attachments
        )
        
        if result.success:
            print("✓ SMTP附件发送成功")
        else:
            print(f"✗ SMTP附件发送失败: {result.error}")
        
        # 清理测试文件
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        print("✓ 测试文件清理完成")
        print("=== SMTP附件功能测试完成 ===")
        
    except Exception as e:
        print(f"✗ SMTP附件测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 运行基本附件功能测试
    test_notification_with_attachments()
    
    print("\n" + "="*50 + "\n")
    
    # 运行SMTP附件功能测试
    test_smtp_attachment_functionality()