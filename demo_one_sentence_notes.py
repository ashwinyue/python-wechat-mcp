#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一句话读书笔记功能演示
快速展示如何使用微信服务器的一句话总结功能
"""

import json
import asyncio
import sys

# 添加当前目录到Python路径
sys.path.append('.')

from weixin_server import generate_one_sentence_summary, create_and_save_reading_notes

def print_header():
    """打印标题"""
    print("🚀 一句话读书笔记功能演示")
    print("=" * 50)
    print("快速提取文章核心要点，一句话掌握文章精髓")
    print()

def print_separator():
    """打印分隔线"""
    print("-" * 50)

async def demo_one_sentence_notes():
    """演示一句话读书笔记功能"""
    
    print_header()
    
    # 创建示例文章数据
    sample_article = {
        "title": "聊一聊我是如何学习 MCP 的",
        "author": "江湖十年",
        "publish_time": "2025年07月11日 09:02",
        "content": """大家好，我是江湖十年。我最近连发了两篇关于 MCP 的文章，是因为近期在做的项目中会用到 MCP。

2025 年已经过去一半了，年初爆火的 MCP 协议也已经降温了，但它却成为了事实上的标准。我认为 MCP 是所有开发者必学的技能，就像 HTTP 一样的存在。

有人说 2025 是 Agent 元年，我认为这其中 MCP 协议功不可没。它真正做到了统一模型和外部数据之间的交互。

那么在 AI 时代，我们该如何学习一项新的技术呢？根据我的个人体验来看，使用诸如 DeepSeek、ChatGPT 等大模型，来辅助学习编程技术是非常方便且高效的。

所以，我为了学习 MCP，花了很多时间来看官方文档。当然，官方文档肯定是最权威，最新鲜的一手技术资料。

我更推荐初学者通过专栏或者图书的形式来学习 MCP 协议知识。专栏的好处是能够跟作者保持互动，图书的好处是错误更少并且更加专业。""",
        "word_count": 350
    }
    
    print(f"📖 示例文章: {sample_article['title']}")
    print(f"👤 作者: {sample_article['author']}")
    print(f"📊 字数: {sample_article['word_count']}字")
    print()
    
    # 1. 演示一句话总结功能
    print("🎯 功能1：生成一句话总结")
    print_separator()
    
    try:
        result = await generate_one_sentence_summary(sample_article)
        result_data = json.loads(result)
        
        if result_data.get("status") == "success":
            print(f"💡 一句话总结:")
            print(f"   {result_data.get('one_sentence_summary')}")
            print()
            print(f"🔑 核心关键词: {', '.join(result_data.get('core_keywords', []))}")
            print(f"⏰ 生成时间: {result_data.get('generated_time')}")
        else:
            print(f"❌ 生成失败: {result_data.get('message')}")
    except Exception as e:
        print(f"❌ 演示失败: {e}")
    
    print()
    print_separator()
    
    # 2. 演示保存到文件功能
    print("📝 功能2：生成并保存一句话笔记")
    print_separator()
    
    try:
        save_result = await create_and_save_reading_notes(
            article_data=sample_article,
            note_style="one_sentence",
            save_to_file=True,
            custom_filename="演示_一句话总结"
        )
        
        save_data = json.loads(save_result)
        
        if save_data.get("status") == "success":
            print("✅ 笔记保存成功!")
            print(f"📁 文件路径: {save_data.get('file_path')}")
            print(f"📊 文件大小: {save_data.get('file_size')} 字节")
            print(f"📝 笔记字数: {save_data.get('notes_word_count')}字")
        else:
            print(f"❌ 保存失败: {save_data.get('message')}")
    except Exception as e:
        print(f"❌ 保存失败: {e}")
    
    print()
    print_separator()
    
    # 3. 使用说明
    print("💡 使用说明")
    print_separator()
    print("""
🎯 一句话读书笔记的优势：
• 快速浏览：在时间有限时，快速了解文章核心内容
• 知识管理：为大量文章建立简洁的索引和目录
• 内容筛选：快速判断文章是否值得深入阅读
• 分享交流：用一句话向他人介绍文章要点

🔧 在MCP客户端中使用：
1. 启动客户端：make run-all
2. 爬取文章：请帮我爬取这篇微信文章：[URL]
3. 生成总结：请为这篇文章生成一句话总结
4. 保存笔记：请将一句话总结保存到文件

📚 支持的笔记风格：
• one_sentence - 一句话总结（最简洁）
• summary - 摘要式
• key_points - 要点式  
• detailed - 详细式
• mind_map - 思维导图式
    """)
    
    print("=" * 50)
    print("✅ 演示完成！一句话读书笔记功能已集成到微信服务器中")
    print("🚀 运行 'make run-all' 开始使用完整功能")

if __name__ == "__main__":
    asyncio.run(demo_one_sentence_notes()) 