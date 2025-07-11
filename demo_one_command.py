#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一句话完成全流程功能演示
展示如何用一句话完成：爬取文章 → 分析内容 → 生成读书笔记
"""

print("🚀 一句话完成全流程功能演示")
print("=" * 60)
print("功能：爬取文章 → 分析内容 → 生成读书笔记")
print()

print("💡 新增的一站式工具：crawl_and_create_reading_notes")
print("-" * 60)
print("""
🎯 功能特点：
• 一个命令完成整个流程：爬取 → 分析 → 生成笔记 → 保存文件
• 支持多种笔记风格：summary、key_points、one_sentence、detailed、mind_map
• 自动保存文章和笔记到对应目录
• 返回详细的处理结果和文件信息

🔧 在MCP客户端中的使用方式：
只需要说一句话：
"请帮我爬取这篇微信文章并生成摘要式读书笔记：[URL]"

AI会自动调用 crawl_and_create_reading_notes 工具完成：
1. 爬取微信文章内容
2. 分析文章数据（关键词、摘要等）
3. 生成指定风格的读书笔记
4. 保存所有文件（文章+笔记）

📚 支持的笔记风格：
• summary - 摘要式（默认，适合快速了解文章要点）
• key_points - 要点式（条理清晰，便于复习）
• one_sentence - 一句话总结（最简洁，适合快速浏览）
• detailed - 详细式（深入分析，适合学习研究）
• mind_map - 思维导图式（结构化，便于记忆）

📁 文件输出结构：
articles/
└── 文章标题_时间戳/
    ├── 文章标题.json    # 完整文章数据
    ├── 文章标题.txt     # 纯文本内容
    ├── 文章标题.html    # HTML格式（图片路径已修复）
    └── images/          # 图片文件夹

reading_notes/
└── 文章标题_笔记风格.md  # Markdown格式的读书笔记

🌟 使用示例：
在MCP客户端中，您可以这样说：

1. "请爬取这篇文章并生成摘要：https://mp.weixin.qq.com/s/example"
2. "帮我分析这篇技术文章并做要点笔记：[URL]"
3. "请为这篇文章生成一句话总结：[URL]"
4. "爬取并制作详细学习笔记：[URL]"

AI会智能识别您的需求，自动选择合适的笔记风格！
""")

print("=" * 60)
print("✅ 功能介绍完成！")
print()
print("🚀 开始使用：")
print("1. 运行 'make run-all' 启动MCP客户端")
print("2. 在对话中说：请帮我爬取这篇微信文章并生成读书笔记：[URL]")
print("3. AI会自动完成整个流程并保存所有文件")
print()
print("💡 提示：您也可以指定笔记风格，如'生成要点式笔记'、'做一句话总结'等") 