#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通知配置检查工具
用于检查和显示当前的通知渠道配置状态
"""

import os
import sys
from config_manager import ConfigManager


def main():
    """主函数"""
    print("=== 通知服务配置状态检查 ===\n")
    
    # 初始化配置管理器
    config_manager = ConfigManager()
    
    # 获取所有渠道状态
    channels_status = config_manager.get_all_channels_status()
    
    print("📋 通知渠道状态:")
    print("-" * 80)
    print(f"{'渠道名称':<15} {'启用状态':<8} {'配置状态':<8} {'描述'}")
    print("-" * 80)
    
    enabled_count = 0
    configured_count = 0
    active_count = 0
    
    for channel_name, status in channels_status.items():
        enabled = "✅" if status['enabled'] else "❌"
        configured = "✅" if status['configured'] else "❌"
        description = status['description']
        
        print(f"{channel_name:<15} {enabled:<8} {configured:<8} {description}")
        
        if status['enabled']:
            enabled_count += 1
        if status['configured']:
            configured_count += 1
        if status['enabled'] and status['configured']:
            active_count += 1
    
    print("-" * 80)
    print(f"总计: {len(channels_status)} 个渠道")
    print(f"启用: {enabled_count} 个")
    print(f"已配置: {configured_count} 个")
    print(f"活跃: {active_count} 个")
    
    # 显示活跃渠道详情
    if active_count > 0:
        print(f"\n🚀 活跃的通知渠道 ({active_count} 个):")
        for channel_name, status in channels_status.items():
            if status['enabled'] and status['configured']:
                print(f"  • {channel_name}: {status['description']}")
    
    # 显示未配置但启用的渠道
    enabled_but_not_configured = [
        channel_name for channel_name, status in channels_status.items()
        if status['enabled'] and not status['configured']
    ]
    
    if enabled_but_not_configured:
        print(f"\n⚠️  启用但未配置的渠道 ({len(enabled_but_not_configured)} 个):")
        for channel_name in enabled_but_not_configured:
            status = channels_status[channel_name]
            print(f"  • {channel_name}: {status['description']}")
            print(f"    需要配置的环境变量: {', '.join(status['required_env'])}")
            if status['optional_env']:
                print(f"    可选的环境变量: {', '.join(status['optional_env'])}")
    
    # 显示配置建议
    if active_count == 0:
        print("\n💡 建议:")
        print("  没有活跃的通知渠道。请:")
        print("  1. 在环境变量中设置 ENABLE_<渠道名>=true 来启用渠道")
        print("  2. 配置相应的认证信息")
        print("  3. 参考 .env.example 文件进行配置")
    
    print(f"\n📖 配置说明:")
    print("  • 启用状态: 通过 ENABLE_<渠道名> 环境变量控制")
    print("  • 配置状态: 检查必需的环境变量是否已设置")
    print("  • 活跃渠道: 既启用又配置完成的渠道")
    
    return active_count > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)