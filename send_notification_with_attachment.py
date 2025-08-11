#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送带附件的通知请求示例脚本
"""

import requests
import base64
import json
import os
import sys
from datetime import datetime

def encode_file_to_base64(file_path):
    """将文件编码为base64字符串"""
    try:
        with open(file_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"编码文件失败: {e}")
        return None

def get_content_type(file_path):
    """根据文件扩展名猜测MIME类型"""
    import mimetypes
    content_type, _ = mimetypes.guess_type(file_path)
    return content_type or 'application/octet-stream'

def send_notification_with_attachments(github_token, repo_full_name, title, content, attachment_files=None):
    """
    发送带附件的GitHub repository_dispatch通知
    
    Args:
        github_token: GitHub个人访问令牌
        repo_full_name: 仓库全名 (如: username/repo-name)
        title: 通知标题
        content: 通知内容
        attachment_files: 附件文件路径列表
    
    Returns:
        bool: 是否发送成功
    """
    
    # 构建基本payload
    payload = {
        "event_type": "send-notification",
        "client_payload": {
            "title": title,
            "content": content,
            "source": "api_request",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    # 处理附件
    if attachment_files:
        attachments = []
        
        for file_path in attachment_files:
            if not os.path.exists(file_path):
                print(f"警告: 附件文件不存在: {file_path}")
                continue
            
            # 检查文件大小 (限制25MB)
            file_size = os.path.getsize(file_path)
            if file_size > 25 * 1024 * 1024:
                print(f"警告: 附件文件过大，跳过: {file_path} ({file_size} bytes)")
                continue
            
            # 编码文件
            filename = os.path.basename(file_path)
            
            # 判断是否为文本文件
            content_type = get_content_type(file_path)
            is_text = content_type.startswith('text/')
            
            if is_text:
                # 文本文件直接读取
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    attachments.append({
                        "filename": filename,
                        "content": file_content,
                        "encoding": "text",
                        "content_type": content_type
                    })
                    print(f"添加文本附件: {filename} ({content_type})")
                    
                except UnicodeDecodeError:
                    # 如果无法以UTF-8读取，则作为二进制处理
                    is_text = False
            
            if not is_text:
                # 二进制文件base64编码
                encoded_content = encode_file_to_base64(file_path)
                if encoded_content:
                    attachments.append({
                        "filename": filename,
                        "content": encoded_content,
                        "encoding": "base64",
                        "content_type": content_type
                    })
                    print(f"添加二进制附件: {filename} ({content_type})")
        
        if attachments:
            payload["client_payload"]["attachments"] = attachments
            print(f"总共准备了 {len(attachments)} 个附件")
    
    # 发送请求
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {github_token}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.github.com/repos/{repo_full_name}/dispatches"
    
    try:
        print(f"发送通知请求到: {url}")
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 204:
            print("✓ 通知请求发送成功")
            return True
        else:
            print(f"✗ 通知请求发送失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 发送请求时发生错误: {e}")
        return False

def main():
    """主函数"""
    
    # 配置参数 - 请根据实际情况修改
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
    REPO_FULL_NAME = os.environ.get('GITHUB_REPO', 'username/repo-name')
    
    if not GITHUB_TOKEN:
        print("错误: 请设置GITHUB_TOKEN环境变量")
        print("export GITHUB_TOKEN=your_github_token")
        sys.exit(1)
    
    if not REPO_FULL_NAME or REPO_FULL_NAME == 'username/repo-name':
        print("错误: 请设置GITHUB_REPO环境变量")
        print("export GITHUB_REPO=your_username/your_repo_name")
        sys.exit(1)
    
    # 示例1: 发送不带附件的通知
    print("=== 示例1: 发送普通通知 ===")
    success = send_notification_with_attachments(
        github_token=GITHUB_TOKEN,
        repo_full_name=REPO_FULL_NAME,
        title="测试通知",
        content="这是一个测试通知，不包含附件。"
    )
    
    if success:
        print("普通通知发送成功\n")
    else:
        print("普通通知发送失败\n")
    
    # 示例2: 发送带附件的通知
    print("=== 示例2: 发送带附件的通知 ===")
    
    # 创建一些测试文件
    test_files = []
    
    # 创建文本文件
    text_file = "test_attachment.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write("这是一个测试附件文件\n")
        f.write("包含中文内容\n")
        f.write(f"创建时间: {datetime.now()}\n")
    test_files.append(text_file)
    
    # 创建JSON文件
    json_file = "test_data.json"
    test_data = {
        "message": "这是测试数据",
        "timestamp": datetime.now().isoformat(),
        "items": ["item1", "item2", "item3"]
    }
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    test_files.append(json_file)
    
    # 发送带附件的通知
    success = send_notification_with_attachments(
        github_token=GITHUB_TOKEN,
        repo_full_name=REPO_FULL_NAME,
        title="带附件的测试通知",
        content="这是一个包含附件的测试通知。请检查邮件中的附件。",
        attachment_files=test_files
    )
    
    if success:
        print("带附件的通知发送成功")
    else:
        print("带附件的通知发送失败")
    
    # 清理测试文件
    for file_path in test_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"清理测试文件: {file_path}")

if __name__ == "__main__":
    main()