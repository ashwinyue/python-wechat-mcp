import asyncio
import json
from typing import Any, Dict

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# 创建服务器实例
server = Server("math-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用的工具"""
    return [
        Tool(
            name="add",
            description="计算两个数的和",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "第一个数字"
                    },
                    "b": {
                        "type": "number",
                        "description": "第二个数字"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="subtract",
            description="计算两个数的差",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "被减数"
                    },
                    "b": {
                        "type": "number",
                        "description": "减数"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="multiply",
            description="计算两个数的乘积",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "第一个数字"
                    },
                    "b": {
                        "type": "number",
                        "description": "第二个数字"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="divide",
            description="计算两个数的商",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "被除数"
                    },
                    "b": {
                        "type": "number",
                        "description": "除数"
                    }
                },
                "required": ["a", "b"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """处理工具调用"""
    try:
        a = float(arguments.get("a", 0))
        b = float(arguments.get("b", 0))
        
        if name == "add":
            result = a + b
            return [TextContent(
                type="text",
                text=f"{a} + {b} = {result}"
            )]
        elif name == "subtract":
            result = a - b
            return [TextContent(
                type="text",
                text=f"{a} - {b} = {result}"
            )]
        elif name == "multiply":
            result = a * b
            return [TextContent(
                type="text",
                text=f"{a} × {b} = {result}"
            )]
        elif name == "divide":
            if b == 0:
                return [TextContent(
                    type="text",
                    text="错误：除数不能为零"
                )]
            result = a / b
            return [TextContent(
                type="text",
                text=f"{a} ÷ {b} = {result}"
            )]
        else:
            raise ValueError(f"Unknown tool: {name}")
    except (ValueError, TypeError) as e:
        return [TextContent(
            type="text",
            text=f"计算错误：{str(e)}"
        )]

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