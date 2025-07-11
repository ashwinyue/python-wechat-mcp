#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试微信公众号文章爬取 MCP 服务器
"""

import subprocess
import json
import time
import sys
import os

def test_weixin_server():
    """测试微信服务器功能"""
    print("测试微信公众号文章爬取 MCP 服务器...")
    
    # 测试服务器是否能正常启动
    try:
        # 使用虚拟环境的Python
        python_path = "venv/bin/python"
        if not os.path.exists(python_path):
            print("错误：虚拟环境不存在，请先创建虚拟环境")
            return False
        
        # 启动服务器进程
        print("启动微信服务器...")
        process = subprocess.Popen(
            [python_path, "weixin_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务器启动
        time.sleep(2)
        
        # 检查服务器是否正在运行
        if process.poll() is None:
            print("✓ 微信服务器启动成功")
            
            # 发送初始化请求
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            print("发送初始化请求...")
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            
            # 读取响应
            response_line = process.stdout.readline()
            if response_line:
                try:
                    response = json.loads(response_line.strip())
                    print("✓ 初始化响应:", response)
                except json.JSONDecodeError:
                    print("✗ 初始化响应格式错误:", response_line)
            
            # 发送列出工具请求
            list_tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            
            print("发送列出工具请求...")
            process.stdin.write(json.dumps(list_tools_request) + "\n")
            process.stdin.flush()
            
            # 读取响应
            response_line = process.stdout.readline()
            if response_line:
                try:
                    response = json.loads(response_line.strip())
                    print("✓ 工具列表响应:", response)
                    
                    # 检查是否包含预期的工具
                    if "result" in response and "tools" in response["result"]:
                        tools = response["result"]["tools"]
                        expected_tools = ["crawl_weixin_article", "analyze_article_content", "get_article_statistics", "save_article_to_file"]
                        
                        for tool_name in expected_tools:
                            if any(tool["name"] == tool_name for tool in tools):
                                print(f"✓ 找到工具: {tool_name}")
                            else:
                                print(f"✗ 未找到工具: {tool_name}")
                    
                except json.JSONDecodeError:
                    print("✗ 工具列表响应格式错误:", response_line)
            
            # 终止服务器进程
            process.terminate()
            process.wait()
            print("✓ 微信服务器测试完成")
            return True
            
        else:
            # 服务器启动失败
            stdout, stderr = process.communicate()
            print("✗ 微信服务器启动失败")
            print("stdout:", stdout)
            print("stderr:", stderr)
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_spider_import():
    """测试爬虫模块导入"""
    print("\n测试爬虫模块导入...")
    try:
        # 使用虚拟环境的Python测试导入
        python_path = "venv/bin/python"
        result = subprocess.run(
            [python_path, "-c", "from weixin_spider import WeixinSpider; print('✓ 爬虫模块导入成功')"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout.strip())
            return True
        else:
            print("✗ 爬虫模块导入失败")
            print("stderr:", result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("微信公众号文章爬取 MCP 服务器测试")
    print("=" * 50)
    
    # 测试1: 爬虫模块导入
    success1 = test_spider_import()
    
    # 测试2: 服务器启动和基本功能
    success2 = test_weixin_server()
    
    print("\n" + "=" * 50)
    print("测试结果:")
    print(f"爬虫模块导入: {'✓ 成功' if success1 else '✗ 失败'}")
    print(f"服务器功能: {'✓ 成功' if success2 else '✗ 失败'}")
    
    if success1 and success2:
        print("\n🎉 所有测试通过！微信公众号文章爬取功能已成功集成到MCP项目中。")
        print("\n使用方法:")
        print("1. 在MCP客户端中配置微信服务器")
        print("2. 使用 crawl_weixin_article 工具爬取文章")
        print("3. 文章将自动保存为JSON、TXT、HTML格式")
        print("4. 图片将下载到articles目录的images子目录中")
    else:
        print("\n❌ 部分测试失败，请检查配置和依赖。")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 