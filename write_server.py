import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# 创建服务器实例
server = Server("write-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用的工具"""
    return [
        Tool(
            name="write_file",
            description="将指定内容写入本地文件",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "需要写入文档的具体内容"
                    },
                    "filename": {
                        "type": "string", 
                        "description": "文件名（可选），如果不提供则使用时间戳命名"
                    }
                },
                "required": ["content"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """处理工具调用"""
    if name == "write_file":
        content = arguments.get("content", "")
        filename = arguments.get("filename")
        
        if not filename:
            # 使用时间戳生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"output_{timestamp}.txt"
        
        try:
            # 确保文件路径安全
            if not filename.endswith('.txt'):
                filename += '.txt'
            
            # 写入文件
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return [TextContent(
                type="text",
                text=f"已成功将内容写入文件: {filename}"
            )]
        except Exception as e:
            return [TextContent(
                type="text", 
                text=f"写入文件时出错: {str(e)}"
            )]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """主函数"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
