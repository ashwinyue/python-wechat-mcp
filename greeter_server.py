import asyncio
import json
from typing import Any, Dict

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# 创建服务器实例
server = Server("greeter-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用的工具"""
    return [
        Tool(
            name="say_hello",
            description="向指定的人问好",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "要问好的人的名字"
                    }
                },
                "required": ["name"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """处理工具调用"""
    if name == "say_hello":
        person_name = arguments.get("name", "朋友")
        
        greeting_message = f"你好 {person_name}！欢迎来到 Python MCP 世界！"
        
        return [TextContent(
            type="text",
            text=greeting_message
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