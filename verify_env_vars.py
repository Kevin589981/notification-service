#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 GitHub Actions workflow 中的环境变量与 config_manager.py 中的环境变量是否一一对应
"""

import re
import yaml
from pathlib import Path


def extract_env_vars_from_yml():
    """从 yml 文件中提取环境变量"""
    yml_path = Path('.github/workflows/notification-service.yml')
    
    if not yml_path.exists():
        print(f"错误: {yml_path} 文件不存在")
        return set()
    
    with open(yml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正则表达式提取环境变量
    env_vars = set()
    
    # 匹配 ENV_VAR: ${{ secrets.ENV_VAR }} 格式
    pattern = r'(\w+):\s*\$\{\{\s*secrets\.(\w+)\s*\}\}'
    matches = re.findall(pattern, content)
    
    for env_var, secret_var in matches:
        # 跳过 GitHub Actions 内置变量
        if env_var not in ['GITHUB_EVENT_NAME', 'GITHUB_EVENT_PATH']:
            env_vars.add(env_var)
    
    return env_vars


def extract_env_vars_from_config_manager():
    """从 config_manager.py 中提取环境变量"""
    config_path = Path('config_manager.py')
    
    if not config_path.exists():
        print(f"错误: {config_path} 文件不存在")
        return set()
    
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正则表达式提取环境变量
    env_vars = set()
    
    # 匹配 os.environ.get('ENV_VAR', ...) 格式
    pattern = r"os\.environ\.get\(['\"](\w+)['\"]"
    matches = re.findall(pattern, content)
    
    for env_var in matches:
        env_vars.add(env_var)
    
    # 也匹配直接在 _config_cache 中定义的环境变量
    pattern2 = r"['\"](\w+)['\"]:\s*os\.environ\.get\(['\"](\w+)['\"]"
    matches2 = re.findall(pattern2, content)
    
    for _, env_var in matches2:
        env_vars.add(env_var)
    
    return env_vars


def main():
    """主函数"""
    print("=== 环境变量对应关系验证 ===\n")
    
    # 提取环境变量
    yml_vars = extract_env_vars_from_yml()
    config_vars = extract_env_vars_from_config_manager()
    
    print(f"GitHub Actions workflow 中的环境变量数量: {len(yml_vars)}")
    print(f"config_manager.py 中的环境变量数量: {len(config_vars)}")
    print()
    
    # 检查 yml 中有但 config_manager 中没有的变量
    yml_only = yml_vars - config_vars
    if yml_only:
        print("⚠️  在 yml 文件中存在但在 config_manager.py 中不存在的环境变量:")
        for var in sorted(yml_only):
            print(f"  - {var}")
        print()
    
    # 检查 config_manager 中有但 yml 中没有的变量
    config_only = config_vars - yml_vars
    if config_only:
        print("⚠️  在 config_manager.py 中存在但在 yml 文件中不存在的环境变量:")
        for var in sorted(config_only):
            print(f"  - {var}")
        print()
    
    # 检查完全匹配的变量
    common_vars = yml_vars & config_vars
    if common_vars:
        print("✅ 在两个文件中都存在的环境变量:")
        for var in sorted(common_vars):
            print(f"  - {var}")
        print()
    
    # 总结
    if yml_only or config_only:
        print("❌ 环境变量不完全匹配！")
        print("建议:")
        if yml_only:
            print("  1. 在 config_manager.py 中添加缺失的环境变量")
        if config_only:
            print("  2. 在 yml 文件中添加缺失的环境变量，或从 config_manager.py 中移除不需要的变量")
        return False
    else:
        print("✅ 所有环境变量都完全匹配！")
        return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)