#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP服务器演示脚本
用于演示所有MCP服务器的启动和基本功能
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

def test_server_import(server_name, server_file):
    """测试服务器模块导入"""
    try:
        # 导入测试
        result = subprocess.run([
            sys.executable, '-c', 
            f'import {server_name}; print("✓ {server_name} 模块导入成功")'
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print(f"✓ {server_name} 模块测试通过")
            return True
        else:
            print(f"✗ {server_name} 模块测试失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ {server_name} 测试异常: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 MCP服务器演示")
    print("=" * 60)
    
    # 服务器列表
    servers = [
        ("weixin_server", "weixin_server.py", "微信公众号爬取服务器"),
        ("weather_server", "weather_server.py", "天气查询服务器"),
        ("math_server", "math_server.py", "数学计算服务器"),
        ("write_server", "write_server.py", "文件写入服务器"),
        ("greeter_server", "greeter_server.py", "问候服务器"),
    ]
    
    print("\n📋 服务器模块测试")
    print("-" * 40)
    
    success_count = 0
    for server_name, server_file, description in servers:
        print(f"测试 {description}...")
        if test_server_import(server_name, server_file):
            success_count += 1
        time.sleep(0.5)
    
    print(f"\n📊 测试结果: {success_count}/{len(servers)} 个服务器通过测试")
    
    if success_count == len(servers):
        print("\n🎉 所有服务器模块测试通过！")
        print("\n💡 使用说明:")
        print("1. 运行 'make run-all' 启动所有服务器和客户端")
        print("2. 运行 'make status-servers' 查看服务器状态")
        print("3. 运行 'make logs' 查看服务器日志")
        print("4. 运行 'make stop-all' 停止所有服务器")
        print("\n🔧 单独启动服务器:")
        for _, server_file, description in servers:
            print(f"   python {server_file}  # {description}")
        
        print("\n📚 MCP协议说明:")
        print("   MCP服务器通过标准输入/输出进行JSON-RPC通信")
        print("   在生产环境中，服务器由MCP客户端管理")
        print("   本演示脚本仅用于验证服务器模块的正确性")
        
    else:
        print("\n❌ 部分服务器测试失败，请检查依赖和配置")
        print("   运行 'make setup' 重新安装依赖")
        print("   运行 'make config' 检查配置")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main() 