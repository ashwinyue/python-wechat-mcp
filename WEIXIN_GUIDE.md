# 微信公众号文章爬取服务器使用指南

## 🚀 快速开始

### 1. 启动服务器

有两种方式启动微信服务器：

**方式一：一键启动所有服务器（推荐）**
```bash
make run-all
```

**方式二：单独启动微信服务器**
```bash
make run-weixin
```

### 2. 验证服务器状态

```bash
# 运行演示验证所有模块
make demo

# 查看服务器状态
make status-servers
```

## 🔧 功能介绍

微信服务器提供4个主要工具：

### 1. `crawl_weixin_article` - 爬取微信文章

**功能**：爬取微信公众号文章内容并自动保存到文件

**参数**：
- `url` (必需): 微信公众号文章URL，必须以 `https://mp.weixin.qq.com/` 开头
- `download_images` (可选): 是否下载图片，默认为 `true`
- `custom_filename` (可选): 自定义文件名，不提供则使用文章标题

**返回值**：JSON格式的爬取结果

**使用示例**：
```python
# 基本用法
result = await client.call_tool("crawl_weixin_article", {
    "url": "https://mp.weixin.qq.com/s/your-article-url"
})

# 不下载图片
result = await client.call_tool("crawl_weixin_article", {
    "url": "https://mp.weixin.qq.com/s/your-article-url",
    "download_images": False
})

# 自定义文件名
result = await client.call_tool("crawl_weixin_article", {
    "url": "https://mp.weixin.qq.com/s/your-article-url",
    "custom_filename": "my_article"
})
```

### 2. `analyze_article_content` - 分析文章内容

**功能**：分析已爬取的文章内容，提供摘要和统计信息

**参数**：
- `article_data` (必需): 文章数据对象
- `analysis_type` (可选): 分析类型
  - `"summary"`: 摘要信息
  - `"keywords"`: 关键词提取
  - `"images"`: 图片信息分析
  - `"full"`: 完整分析（默认）

**使用示例**：
```python
# 完整分析
result = await client.call_tool("analyze_article_content", {
    "article_data": article_data,
    "analysis_type": "full"
})

# 只分析关键词
result = await client.call_tool("analyze_article_content", {
    "article_data": article_data,
    "analysis_type": "keywords"
})
```

### 3. `get_article_statistics` - 获取文章统计

**功能**：获取文章的详细统计信息

**参数**：
- `article_data` (必需): 文章数据对象

**返回信息**：
- 基本信息：标题、作者、发布时间等
- 内容统计：字符数、词数、段落数、阅读时间
- 图片统计：总数、下载成功数、失败数

### 4. `save_article_to_file` - 保存文章到文件

**功能**：将文章数据保存为多种格式的文件

**参数**：
- `article_data` (必需): 文章数据对象
- `custom_filename` (可选): 自定义文件名

**保存格式**：
- JSON: 完整的文章数据
- TXT: 纯文本内容
- HTML: 带格式的HTML文件

### 5. `generate_one_sentence_summary` - 生成一句话总结

**功能**：快速生成文章的一句话读书笔记，适合快速浏览和知识管理

**参数**：
- `article_data` (必需): 文章数据对象

**返回信息**：
- 一句话总结
- 核心关键词（前3个）
- 生成时间

**使用示例**：
```python
result = await client.call_tool("generate_one_sentence_summary", {
    "article_data": article_data
})
```

### 6. `generate_reading_notes` - 生成读书笔记

**功能**：根据文章内容生成不同风格的读书笔记

**参数**：
- `article_data` (必需): 文章数据对象
- `note_style` (可选): 笔记风格
  - `"summary"`: 摘要式（默认）
  - `"detailed"`: 详细式
  - `"mind_map"`: 思维导图式
  - `"key_points"`: 要点式
  - `"one_sentence"`: 一句话总结

**使用示例**：
```python
# 生成一句话总结
result = await client.call_tool("generate_reading_notes", {
    "article_data": article_data,
    "note_style": "one_sentence"
})

# 生成详细笔记
result = await client.call_tool("generate_reading_notes", {
    "article_data": article_data,
    "note_style": "detailed"
})
```

### 7. `create_and_save_reading_notes` - 生成并保存读书笔记

**功能**：生成读书笔记并保存到文件，支持所有笔记风格

**参数**：
- `article_data` (必需): 文章数据对象
- `note_style` (可选): 笔记风格（同上）
- `save_to_file` (可选): 是否保存到文件，默认为True
- `custom_filename` (可选): 自定义文件名

**保存位置**：笔记保存在 `reading_notes/` 目录下，格式为Markdown

**使用示例**：
```python
# 生成并保存一句话总结
result = await client.call_tool("create_and_save_reading_notes", {
    "article_data": article_data,
    "note_style": "one_sentence",
    "custom_filename": "MCP学习心得_一句话总结"
})
```

### 8. `crawl_and_create_reading_notes` - 一句话完成全流程 ⭐

**功能**：一句话完成爬取文章、分析内容、生成读书笔记的完整流程

**参数**：
- `url` (必需): 微信文章URL
- `note_style` (可选): 笔记风格（默认为summary）
- `download_images` (可选): 是否下载图片，默认为True
- `custom_filename` (可选): 自定义文件名

**自动完成的步骤**：
1. 爬取微信文章内容
2. 分析文章数据（关键词、摘要等）
3. 生成指定风格的读书笔记
4. 保存所有文件（文章+笔记）

**返回信息**：
- 文章信息（标题、作者、字数、图片数等）
- 分析摘要（关键词数、摘要状态等）
- 笔记信息（风格、字数、保存路径等）
- 创建的文件列表

**使用示例**：
```python
# 一句话完成：爬取文章并生成摘要式读书笔记
result = await client.call_tool("crawl_and_create_reading_notes", {
    "url": "https://mp.weixin.qq.com/s/example-article",
    "note_style": "summary"
})

# 一句话完成：爬取文章并生成一句话总结
result = await client.call_tool("crawl_and_create_reading_notes", {
    "url": "https://mp.weixin.qq.com/s/example-article", 
    "note_style": "one_sentence",
    "custom_filename": "重要文章"
})
```

## 📁 文件输出结构

爬取的文章会保存在 `articles/` 目录下：

```
articles/
└── 文章标题_20240101_120000/
    ├── 文章标题.json    # 完整文章数据
    ├── 文章标题.txt     # 纯文本内容
    ├── 文章标题.html    # HTML格式
    └── images/          # 图片文件夹
        ├── img_1.jpg
        ├── img_2.png
        └── ...
```

## 🎯 实际使用示例

### 示例1：爬取文章并分析

```python
# 1. 爬取文章
url = "https://mp.weixin.qq.com/s/example-article"
crawl_result = await client.call_tool("crawl_weixin_article", {
    "url": url,
    "download_images": True
})

# 2. 解析结果
import json
result_data = json.loads(crawl_result)
if result_data["status"] == "success":
    print(f"文章标题: {result_data['article']['title']}")
    print(f"作者: {result_data['article']['author']}")
    print(f"字数: {result_data['article']['word_count']}")
    print(f"图片数: {result_data['article']['images_count']}")
```

### 示例2：批量处理文章

```python
urls = [
    "https://mp.weixin.qq.com/s/article1",
    "https://mp.weixin.qq.com/s/article2",
    "https://mp.weixin.qq.com/s/article3"
]

for i, url in enumerate(urls):
    result = await client.call_tool("crawl_weixin_article", {
        "url": url,
        "custom_filename": f"article_{i+1}"
    })
    print(f"处理第{i+1}篇文章: {result}")
```

### 示例3：只获取文本不下载图片

```python
result = await client.call_tool("crawl_weixin_article", {
    "url": "https://mp.weixin.qq.com/s/your-article",
    "download_images": False
})
```

### 示例4：生成一句话读书笔记

```python
# 1. 爬取文章
crawl_result = await client.call_tool("crawl_weixin_article", {
    "url": "https://mp.weixin.qq.com/s/example-article"
})

# 2. 提取文章数据
import json
result_data = json.loads(crawl_result)
article_data = result_data["article"]

# 3. 生成一句话总结
summary_result = await client.call_tool("generate_one_sentence_summary", {
    "article_data": article_data
})

summary_data = json.loads(summary_result)
print(f"一句话总结: {summary_data['one_sentence_summary']}")
print(f"核心关键词: {', '.join(summary_data['core_keywords'])}")
```

### 示例5：一句话完成全流程 ⭐

```python
# 最简单的用法：一句话完成爬取+分析+生成笔记
result = await client.call_tool("crawl_and_create_reading_notes", {
    "url": "https://mp.weixin.qq.com/s/example-article"
})

# 指定笔记风格
result = await client.call_tool("crawl_and_create_reading_notes", {
    "url": "https://mp.weixin.qq.com/s/example-article",
    "note_style": "key_points",  # 要点式笔记
    "custom_filename": "重要技术文章"
})

# 生成一句话总结
result = await client.call_tool("crawl_and_create_reading_notes", {
    "url": "https://mp.weixin.qq.com/s/example-article",
    "note_style": "one_sentence"
})
```

### 示例6：批量生成读书笔记

```python
urls = [
    "https://mp.weixin.qq.com/s/article1",
    "https://mp.weixin.qq.com/s/article2", 
    "https://mp.weixin.qq.com/s/article3"
]

# 使用一站式功能批量处理
for i, url in enumerate(urls):
    result = await client.call_tool("crawl_and_create_reading_notes", {
        "url": url,
        "note_style": "summary",
        "custom_filename": f"文章{i+1}"
    })
    
    result_data = json.loads(result)
    if result_data["status"] == "success":
        print(f"✅ 文章{i+1}处理完成")
        print(f"标题: {result_data['article_info']['title']}")
        print(f"笔记: {result_data['notes_info']['file_path']}")
```

## 🔍 在MCP客户端中使用

当您运行 `make run-all` 启动MCP客户端后，可以直接在对话中使用：

```
用户：请帮我爬取这篇微信文章：https://mp.weixin.qq.com/s/example

AI：我来帮您爬取这篇微信文章。

[AI会自动调用 crawl_weixin_article 工具]

用户：请分析一下这篇文章的关键词

AI：我来分析文章的关键词。

[AI会自动调用 analyze_article_content 工具]
```

## ⚠️ 注意事项

### 1. URL格式要求
- 必须是完整的微信文章URL
- 必须以 `https://mp.weixin.qq.com/` 开头
- 确保URL可以正常访问

### 2. 网络和环境要求
- 需要稳定的网络连接
- 需要Chrome浏览器环境
- 建议在有图形界面的环境中运行（虽然支持无头模式）

### 3. 性能考虑
- 爬取速度取决于网络状况和文章长度
- 下载图片会增加处理时间
- 建议不要同时爬取太多文章

### 4. 文件存储
- 文章保存在 `articles/` 目录
- 每篇文章创建独立的文件夹
- 图片保存在对应文章的 `images/` 子目录

## 🐛 故障排除

### 1. Chrome浏览器问题
```bash
# 检查Chrome和ChromeDriver
make check-chrome

# 安装系统依赖（macOS）
make install-system-deps
```

### 2. 爬取失败
- 检查URL是否正确
- 确认网络连接
- 查看服务器日志：`make logs`

### 3. 图片下载失败
- 图片下载失败不影响文章内容爬取
- 可以设置 `download_images: false` 跳过图片下载

### 4. 服务器状态检查
```bash
# 查看服务器状态
make status-servers

# 查看详细日志
tail -f logs/weixin.log
```

## 📚 高级用法

### 1. 自定义爬虫配置

可以通过环境变量配置爬虫行为：

```bash
# 在.env文件中添加
ARTICLES_DIR=articles          # 文章保存目录
DOWNLOAD_IMAGES=true          # 是否下载图片
HEADLESS=true                 # 是否使用无头模式
WAIT_TIME=10                  # 页面等待时间
```

### 2. 程序化使用

```python
# 直接使用爬虫类
from weixin_spider import WeixinSpider

spider = WeixinSpider(headless=True, download_images=True)
article_data = spider.crawl_article_by_url("https://mp.weixin.qq.com/s/...")
spider.save_article_to_file(article_data)
spider.close()
```

### 3. 批量处理脚本

```python
import json
import asyncio

async def batch_crawl(urls):
    results = []
    for url in urls:
        result = await client.call_tool("crawl_weixin_article", {"url": url})
        results.append(json.loads(result))
    return results

# 使用
urls = ["url1", "url2", "url3"]
results = await batch_crawl(urls)
```

## 🎉 总结

微信公众号文章爬取服务器提供了完整的文章爬取、分析和存储功能。通过MCP协议，您可以轻松地在AI对话中使用这些功能，实现智能化的内容处理和分析。

主要优势：
- 🚀 **简单易用**：一键启动，自动管理
- 🔧 **功能完整**：爬取、分析、存储一体化
- 📱 **智能交互**：通过AI对话使用
- 🛡️ **稳定可靠**：完善的错误处理和重试机制
- 📊 **数据丰富**：多格式保存，详细统计分析 