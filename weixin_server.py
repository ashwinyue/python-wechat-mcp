#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号文章爬取 MCP 服务器
提供微信公众号文章爬取和文件保存功能
"""

import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime
import re
from collections import Counter

# MCP imports
from mcp.server.fastmcp import FastMCP

# 导入微信爬虫
from weixin_spider import WeixinSpider

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastMCP服务器实例
mcp = FastMCP("weixin-spider")

# 全局爬虫实例
spider_instance: Optional[WeixinSpider] = None

def get_spider_instance() -> WeixinSpider:
    """获取爬虫实例（单例模式）"""
    global spider_instance
    if spider_instance is None:
        try:
            spider_instance = WeixinSpider(
                headless=True,  # MCP服务器中使用无头模式
                wait_time=10,
                download_images=True
            )
            logger.info("爬虫实例初始化成功")
        except Exception as e:
            logger.error(f"爬虫实例初始化失败: {e}")
            raise RuntimeError(f"无法初始化爬虫实例: {e}")
    
    # 检查驱动是否仍然有效
    if spider_instance.driver is None:
        logger.warning("检测到驱动已失效，重新初始化...")
        try:
            spider_instance.setup_driver(headless=True)
            logger.info("驱动重新初始化成功")
        except Exception as e:
            logger.error(f"驱动重新初始化失败: {e}")
            # 创建新的爬虫实例
            try:
                spider_instance = WeixinSpider(
                    headless=True,
                    wait_time=10,
                    download_images=True
                )
                logger.info("创建新的爬虫实例成功")
            except Exception as new_e:
                logger.error(f"创建新爬虫实例失败: {new_e}")
                raise RuntimeError(f"无法创建爬虫实例: {new_e}")
    
    return spider_instance

@mcp.tool()
async def crawl_weixin_article(url: str, download_images: bool = True, custom_filename: str = None) -> str:
    """
    爬取微信公众号文章内容并保存到文件
    
    Args:
        url: 微信公众号文章的URL链接，必须以 https://mp.weixin.qq.com/ 开头
        download_images: 是否下载文章中的图片，默认为 true
        custom_filename: 自定义文件名（可选），如果不提供将使用文章标题作为文件名
    
    Returns:
        爬取结果的JSON字符串
    """
    try:
        # 验证URL
        if not url or not isinstance(url, str) or not url.startswith("https://mp.weixin.qq.com/"):
            return json.dumps({
                "status": "error",
                "message": "无效的微信文章URL，必须以 https://mp.weixin.qq.com/ 开头"
            }, ensure_ascii=False, indent=2)
        
        logger.info(f"开始爬取文章: {url}")
        
        # 获取爬虫实例
        spider = get_spider_instance()
        
        # 设置是否下载图片
        spider.download_images = download_images
        
        # 爬取文章
        article_data = spider.crawl_article_by_url(url)
        
        if not article_data:
            return json.dumps({
                "status": "error",
                "message": "无法获取文章内容，请检查URL是否正确或网络连接"
            }, ensure_ascii=False, indent=2)
        
        # 保存文章到文件
        success = spider.save_article_to_file(article_data, custom_filename)
        
        if success:
            # 构建返回结果
            result = {
                "status": "success",
                "message": "文章爬取成功",
                "article": {
                    "title": article_data.get("title", ""),
                    "author": article_data.get("author", ""),
                    "publish_time": article_data.get("publish_time", ""),
                    "url": article_data.get("url", ""),
                    "content_length": len(article_data.get("content", "")),
                    "word_count": article_data.get("word_count", 0),
                    "images_count": len(article_data.get("images", [])),
                    "crawl_time": article_data.get("crawl_time", "")
                },
                "files_saved": {
                    "json": True,
                    "txt": True,
                    "html": True,
                    "images": download_images
                }
            }
            
            if download_images:
                images = article_data.get("images", [])
                success_count = sum(1 for img in images if img.get("download_success", False))
                result["article"]["images_downloaded"] = f"{success_count}/{len(images)}"
            
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            return json.dumps({
                "status": "error",
                "message": "文章爬取成功但保存文件时出错"
            }, ensure_ascii=False, indent=2)
            
    except Exception as e:
        logger.error(f"爬取文章失败: {e}")
        return json.dumps({
            "status": "error",
            "message": f"爬取失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
async def analyze_article_content(article_data: dict, analysis_type: str = "full") -> str:
    """
    分析已爬取的文章内容，提供摘要和统计信息
    
    Args:
        article_data: 文章数据对象，包含标题、内容等信息
        analysis_type: 分析类型：summary(摘要), keywords(关键词), images(图片信息), full(完整分析)
    
    Returns:
        分析结果的JSON字符串
    """
    try:
        if not article_data or not isinstance(article_data, dict):
            return json.dumps({
                "status": "error",
                "message": "article_data 必须是字典格式的文章数据"
            }, ensure_ascii=False, indent=2)
        
        logger.info(f"分析文章内容: analysis_type={analysis_type}")
        
        result = {"analysis_type": analysis_type}
        
        if analysis_type in ["summary", "full"]:
            content = article_data.get("content", "")
            result["summary"] = {
                "title": article_data.get("title", ""),
                "author": article_data.get("author", ""),
                "publish_time": article_data.get("publish_time", ""),
                "word_count": len(content),
                "paragraph_count": len([p for p in content.split('\n') if p.strip()]),
                "estimated_reading_time": f"{max(1, len(content) // 300)} 分钟"
            }
        
        if analysis_type in ["keywords", "full"]:
            content = article_data.get("content", "")
            # 改进的关键词提取（基于词频）
            # 清理文本，保留中文字符和基本标点
            cleaned_text = re.sub(r'[^\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', ' ', content)
            
            # 简单的中文分词（基于标点和空格）
            # 移除常见停用词
            stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '它', '他', '她', '们', '来', '过', '时', '大', '小', '多', '少', '可以', '能够', '应该', '必须', '如果', '因为', '所以', '但是', '然后', '现在', '已经', '还是', '只是', '或者', '以及', '并且', '而且', '不过', '虽然', '尽管', '除了', '通过', '关于', '对于', '由于', '为了', '根据', '按照', '依据', '基于'}
            
            # 提取2-4字的中文词组
            words = []
            text_parts = re.split(r'[，。！？；：\s]+', cleaned_text)
            
            for part in text_parts:
                if len(part) >= 2:
                    # 提取2-4字的连续中文字符，优先提取完整词汇
                    for i in range(len(part)):
                        for length in [4, 3, 2]:  # 优先提取长词
                            if i + length <= len(part):
                                word = part[i:i+length]
                                if (len(word) == length and 
                                    word not in stop_words and 
                                    re.match(r'^[\u4e00-\u9fff]+$', word) and
                                    not any(word.endswith(suffix) for suffix in ['的', '了', '在', '是', '有', '和', '就', '不', '都', '也', '很', '到', '说', '要', '去', '会', '着', '没', '看', '好', '这', '那', '它', '他', '她', '们', '来', '过', '时', '大', '小', '多', '少'])):
                                    words.append(word)
            
            # 统计词频
            word_freq = Counter(words)
            top_keywords = word_freq.most_common(15)
            
            # 过滤掉频次太低的词（少于2次）
            filtered_keywords = [(word, count) for word, count in top_keywords if count >= 2]
            
            result["keywords"] = [{"word": word, "count": count} for word, count in filtered_keywords[:10]]
        
        if analysis_type in ["images", "full"]:
            images = article_data.get("images", [])
            result["images_analysis"] = {
                "total_images": len(images),
                "downloaded_images": sum(1 for img in images if img.get("download_success", False)),
                "failed_images": sum(1 for img in images if not img.get("download_success", False)),
                "image_types": list(set([
                    img.get("url", "").split(".")[-1].lower() 
                    for img in images 
                    if img.get("url") and "." in img.get("url")
                ]))
            }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"分析文章内容失败: {e}")
        return json.dumps({
            "status": "error",
            "message": f"分析失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
async def get_article_statistics(article_data: dict) -> str:
    """
    获取文章的统计信息
    
    Args:
        article_data: 文章数据对象
    
    Returns:
        统计信息的JSON字符串
    """
    try:
        if not article_data or not isinstance(article_data, dict):
            return json.dumps({
                "status": "error",
                "message": "article_data 必须是字典格式的文章数据"
            }, ensure_ascii=False, indent=2)
        
        content = article_data.get("content", "")
        images = article_data.get("images", [])
        
        # 计算统计信息
        stats = {
            "basic_info": {
                "title": article_data.get("title", ""),
                "author": article_data.get("author", ""),
                "publish_time": article_data.get("publish_time", ""),
                "crawl_time": article_data.get("crawl_time", ""),
                "url": article_data.get("url", "")
            },
            "content_stats": {
                "total_characters": len(content),
                "total_words": article_data.get("word_count", len(content)),
                "paragraphs": len([p for p in content.split('\n') if p.strip()]),
                "estimated_reading_time": f"{max(1, len(content) // 300)} 分钟"
            },
            "image_stats": {
                "total_images": len(images),
                "downloaded_images": sum(1 for img in images if img.get("download_success", False)),
                "failed_downloads": sum(1 for img in images if not img.get("download_success", False))
            }
        }
        
        return json.dumps(stats, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"获取文章统计信息失败: {e}")
        return json.dumps({
            "status": "error",
            "message": f"获取统计信息失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
async def generate_reading_notes(article_data: dict, note_style: str = "summary") -> str:
    """
    根据文章内容生成读书笔记
    
    Args:
        article_data: 文章数据对象，包含标题、内容等信息
        note_style: 笔记风格：summary(摘要式), detailed(详细式), mind_map(思维导图式), key_points(要点式), one_sentence(一句话总结)
    
    Returns:
        生成的读书笔记内容
    """
    try:
        if not article_data or not isinstance(article_data, dict):
            return json.dumps({
                "status": "error",
                "message": "article_data 必须是字典格式的文章数据"
            }, ensure_ascii=False, indent=2)
        
        logger.info(f"生成读书笔记: note_style={note_style}")
        
        # 获取文章基本信息
        title = article_data.get("title", "未知标题")
        author = article_data.get("author", "未知作者")
        publish_time = article_data.get("publish_time", "未知时间")
        content = article_data.get("content", "")
        word_count = article_data.get("word_count", len(content))
        
        # 分析关键词
        keywords_result = await analyze_article_content(article_data, "keywords")
        keywords_data = json.loads(keywords_result)
        keywords = keywords_data.get("keywords", [])
        
        # 根据不同风格生成笔记
        if note_style == "summary":
            notes = _generate_summary_notes(title, author, publish_time, content, word_count, keywords)
        elif note_style == "detailed":
            notes = _generate_detailed_notes(title, author, publish_time, content, word_count, keywords)
        elif note_style == "mind_map":
            notes = _generate_mind_map_notes(title, author, publish_time, content, word_count, keywords)
        elif note_style == "key_points":
            notes = _generate_key_points_notes(title, author, publish_time, content, word_count, keywords)
        elif note_style == "one_sentence":
            # 生成一句话总结
            one_sentence = _generate_one_sentence_from_content(title, author, [kw.get("word", "") for kw in keywords[:3]], [])
            notes = f"# 一句话读书笔记：{title}\n\n**{one_sentence}**\n\n---\n*生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}*"
        else:
            notes = _generate_summary_notes(title, author, publish_time, content, word_count, keywords)
        
        return json.dumps({
            "status": "success",
            "note_style": note_style,
            "notes": notes,
            "word_count": len(notes),
            "generated_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"生成读书笔记失败: {e}")
        return json.dumps({
            "status": "error",
            "message": f"生成笔记失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

def _generate_summary_notes(title, author, publish_time, content, word_count, keywords):
    """生成摘要式读书笔记"""
    # 提取文章主要段落
    paragraphs = [p.strip() for p in content.split('\n') if p.strip() and len(p.strip()) > 20]
    
    # 选择关键段落（开头、中间、结尾）
    key_paragraphs = []
    if len(paragraphs) >= 3:
        key_paragraphs.append(paragraphs[0])  # 开头
        key_paragraphs.append(paragraphs[len(paragraphs)//2])  # 中间
        key_paragraphs.append(paragraphs[-1])  # 结尾
    else:
        key_paragraphs = paragraphs
    
    # 生成关键词列表
    keyword_list = "、".join([kw.get("word", "") for kw in keywords[:8]])
    
    notes = f"""# 读书笔记：{title}

## 📚 文章信息
- **标题**：{title}
- **作者**：{author}
- **发布时间**：{publish_time}
- **字数**：{word_count}字
- **笔记生成时间**：{datetime.now().strftime('%Y年%m月%d日')}

## 🎯 核心要点

### 关键词
{keyword_list}

### 主要内容
{chr(10).join([f"{i+1}. {para[:200]}..." if len(para) > 200 else f"{i+1}. {para}" for i, para in enumerate(key_paragraphs)])}

## 💡 个人思考
- 这篇文章主要讲述了{title.replace('聊一聊我是如何学习', '').replace('的', '')}相关内容
- 作者{author}分享了自己的经验和见解
- 值得进一步思考和实践的地方：
  □ 
  □ 
  □ 

## 📝 行动计划
- [ ] 
- [ ] 
- [ ] 

---
*本笔记由AI自动生成，建议结合个人理解进行补充和完善*
"""
    return notes

def _generate_detailed_notes(title, author, publish_time, content, word_count, keywords):
    """生成详细式读书笔记"""
    # 按段落分析内容
    paragraphs = [p.strip() for p in content.split('\n') if p.strip() and len(p.strip()) > 10]
    
    # 生成关键词分析
    keyword_analysis = "\n".join([f"- **{kw.get('word', '')}**：出现{kw.get('count', 0)}次" for kw in keywords[:10]])
    
    notes = f"""# 详细读书笔记：{title}

## 📖 基本信息
| 项目 | 内容 |
|------|------|
| 标题 | {title} |
| 作者 | {author} |
| 发布时间 | {publish_time} |
| 字数统计 | {word_count}字 |
| 段落数量 | {len(paragraphs)}段 |
| 笔记日期 | {datetime.now().strftime('%Y年%m月%d日 %H:%M')} |

## 🔍 关键词分析
{keyword_analysis}

## 📋 内容结构分析

### 文章脉络
"""
    
    # 添加段落分析
    for i, para in enumerate(paragraphs[:10]):  # 只分析前10段
        if len(para) > 50:  # 只分析较长的段落
            notes += f"\n**第{i+1}段**：{para[:150]}{'...' if len(para) > 150 else ''}\n"
    
    notes += f"""

## 💭 深度思考

### 主要观点
1. 
2. 
3. 

### 论证逻辑
- 
- 
- 

### 启发与收获
- 
- 
- 

## 🎯 实践应用

### 可行动的建议
1. 
2. 
3. 

### 需要进一步学习的内容
- 
- 
- 

## 📚 相关阅读推荐
- 
- 
- 

## 🔖 重要摘录
> 

---
*详细笔记模板，请根据个人理解填充具体内容*
"""
    return notes

def _generate_mind_map_notes(title, author, publish_time, content, word_count, keywords):
    """生成思维导图式读书笔记"""
    # 提取主要概念
    main_concepts = [kw.get("word", "") for kw in keywords[:6]]
    
    notes = f"""# 思维导图式笔记：{title}

```
{title}
├── 📚 基本信息
│   ├── 作者：{author}
│   ├── 时间：{publish_time}
│   └── 字数：{word_count}字
│
├── 🎯 核心概念
│   ├── {main_concepts[0] if len(main_concepts) > 0 else '概念1'}
│   ├── {main_concepts[1] if len(main_concepts) > 1 else '概念2'}
│   ├── {main_concepts[2] if len(main_concepts) > 2 else '概念3'}
│   └── {main_concepts[3] if len(main_concepts) > 3 else '概念4'}
│
├── 💡 主要观点
│   ├── 观点1：
│   ├── 观点2：
│   └── 观点3：
│
├── 🔗 逻辑关系
│   ├── 因果关系：
│   ├── 对比关系：
│   └── 递进关系：
│
├── 📝 实践要点
│   ├── 方法1：
│   ├── 方法2：
│   └── 方法3：
│
└── 🎓 学习收获
    ├── 新知识：
    ├── 新方法：
    └── 新思路：
```

## 🧠 思维拓展

### 联想网络
- {main_concepts[0] if len(main_concepts) > 0 else '核心概念'} → 
- {main_concepts[1] if len(main_concepts) > 1 else '相关概念'} → 
- {main_concepts[2] if len(main_concepts) > 2 else '延伸概念'} → 

### 问题思考
1. 为什么？
2. 如何做？
3. 还有什么？

---
*思维导图帮助建立知识间的连接，促进深度理解*
"""
    return notes

def _generate_key_points_notes(title, author, publish_time, content, word_count, keywords):
    """生成要点式读书笔记"""
    # 提取关键句子
    sentences = [s.strip() for s in content.replace('。', '。\n').split('\n') if s.strip() and len(s.strip()) > 15]
    key_sentences = sentences[:8]  # 取前8个关键句子
    
    notes = f"""# 要点式笔记：{title}

## ℹ️ 文章速览
**标题**：{title}  
**作者**：{author}  
**时间**：{publish_time}  
**字数**：{word_count}字  

## 🎯 核心要点

### 关键词频分析
"""
    
    for i, kw in enumerate(keywords[:8], 1):
        notes += f"{i}. **{kw.get('word', '')}** (出现{kw.get('count', 0)}次)\n"
    
    notes += f"""
### 重要观点提取
"""
    
    for i, sentence in enumerate(key_sentences, 1):
        if len(sentence) > 100:
            notes += f"{i}. {sentence[:100]}...\n"
        else:
            notes += f"{i}. {sentence}\n"
    
    notes += f"""

## ✅ 行动清单

### 立即可做
- [ ] 
- [ ] 
- [ ] 

### 计划执行
- [ ] 
- [ ] 
- [ ] 

### 长期目标
- [ ] 
- [ ] 
- [ ] 

## 🔍 深入研究方向
1. 
2. 
3. 

## 📌 记忆要点
- 
- 
- 

---
*要点式笔记便于快速回顾和执行*
"""
    return notes

@mcp.tool()
async def generate_one_sentence_summary(article_data: dict) -> str:
    """
    生成文章的一句话读书笔记
    
    Args:
        article_data: 文章数据对象，包含标题、内容等信息
    
    Returns:
        一句话总结的JSON字符串
    """
    try:
        if not article_data or not isinstance(article_data, dict):
            return json.dumps({
                "status": "error",
                "message": "article_data 必须是字典格式的文章数据"
            }, ensure_ascii=False, indent=2)
        
        logger.info("生成一句话读书笔记")
        
        # 获取文章基本信息
        title = article_data.get("title", "未知标题")
        author = article_data.get("author", "未知作者")
        content = article_data.get("content", "")
        
        # 分析关键词
        keywords_result = await analyze_article_content(article_data, "keywords")
        keywords_data = json.loads(keywords_result)
        keywords = keywords_data.get("keywords", [])
        
        # 提取核心关键词（前3个）
        core_keywords = [kw.get("word", "") for kw in keywords[:3]]
        
        # 提取文章的第一段和最后一段作为核心观点
        paragraphs = [p.strip() for p in content.split('\n') if p.strip() and len(p.strip()) > 20]
        
        # 生成一句话总结
        one_sentence = _generate_one_sentence_from_content(title, author, core_keywords, paragraphs)
        
        return json.dumps({
            "status": "success",
            "title": title,
            "author": author,
            "core_keywords": core_keywords,
            "one_sentence_summary": one_sentence,
            "generated_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"生成一句话读书笔记失败: {e}")
        return json.dumps({
            "status": "error",
            "message": f"生成失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

def _generate_one_sentence_from_content(title, author, keywords, paragraphs):
    """根据文章内容生成一句话总结"""
    
    # 分析标题中的关键信息
    title_clean = title.replace('聊一聊', '').replace('我是如何', '').replace('的', '')
    
    # 构建核心主题
    if keywords:
        main_topic = keywords[0]  # 第一个关键词作为主题
        supporting_topics = "、".join(keywords[1:3]) if len(keywords) > 1 else ""
    else:
        main_topic = title_clean
        supporting_topics = ""
    
    # 根据不同类型的文章生成不同的总结模式
    if "学习" in title or "如何" in title:
        # 学习方法类文章
        if supporting_topics:
            summary = f"作者{author}分享了学习{main_topic}的方法，重点强调了{supporting_topics}的重要性，建议通过实践和持续学习来掌握相关技能。"
        else:
            summary = f"作者{author}分享了学习{main_topic}的经验和方法，强调了实践的重要性。"
    
    elif "技术" in title or "开发" in title:
        # 技术类文章
        if supporting_topics:
            summary = f"这篇文章介绍了{main_topic}技术，涵盖了{supporting_topics}等核心概念，为开发者提供了实用的技术指导。"
        else:
            summary = f"这篇文章介绍了{main_topic}相关的技术内容和实践经验。"
    
    elif "思考" in title or "观点" in title or "看法" in title:
        # 观点思考类文章
        if supporting_topics:
            summary = f"作者{author}对{main_topic}进行了深入思考，从{supporting_topics}等角度分析了相关问题，提出了独到的见解。"
        else:
            summary = f"作者{author}对{main_topic}进行了深入思考，分享了个人的观点和见解。"
    
    elif "介绍" in title or "什么是" in title:
        # 介绍说明类文章
        if supporting_topics:
            summary = f"这篇文章详细介绍了{main_topic}的概念和应用，重点阐述了{supporting_topics}等关键要素。"
        else:
            summary = f"这篇文章详细介绍了{main_topic}的相关内容和基本概念。"
    
    else:
        # 通用模式
        if supporting_topics:
            summary = f"作者{author}围绕{main_topic}主题，深入探讨了{supporting_topics}等关键问题，为读者提供了有价值的见解和建议。"
        else:
            summary = f"作者{author}围绕{main_topic}主题分享了个人的经验和见解。"
    
    return summary

@mcp.tool()
async def crawl_and_create_reading_notes(url: str, note_style: str = "summary", download_images: bool = True, custom_filename: str = None) -> str:
    """
    一句话完成：爬取微信文章并生成读书笔记
    
    Args:
        url: 微信文章URL
        note_style: 笔记风格：summary(摘要式), detailed(详细式), mind_map(思维导图式), key_points(要点式), one_sentence(一句话总结)
        download_images: 是否下载图片，默认为True
        custom_filename: 自定义文件名（可选）
    
    Returns:
        完整操作结果的JSON字符串，包含爬取结果、分析结果和笔记内容
    """
    try:
        logger.info(f"开始一站式处理: url={url}, note_style={note_style}")
        
        # 第一步：爬取文章
        logger.info("步骤1: 爬取微信文章...")
        spider = WeixinSpider(download_images=download_images)
        
        article_data = spider.crawl_article_by_url(url)
        if not article_data:
            return json.dumps({
                "status": "error",
                "message": "文章爬取失败，请检查URL是否正确"
            }, ensure_ascii=False, indent=2)
        
        # 保存爬取的文章
        if custom_filename:
            save_success = spider.save_article_to_file(article_data, custom_filename)
        else:
            save_success = spider.save_article_to_file(article_data)
        
        logger.info(f"文章爬取完成: 标题={article_data.get('title')}, 字数={article_data.get('word_count')}")
        
        # 第二步：分析文章内容
        logger.info("步骤2: 分析文章内容...")
        analysis_result = await analyze_article_content(article_data, "full")
        analysis_data = json.loads(analysis_result)
        
        # 第三步：生成读书笔记
        logger.info(f"步骤3: 生成{note_style}风格读书笔记...")
        notes_result = await generate_reading_notes(article_data, note_style)
        notes_data = json.loads(notes_result)
        
        # 第四步：保存读书笔记到文件
        logger.info("步骤4: 保存读书笔记...")
        if notes_data.get("status") == "success":
            notes_content = notes_data.get("notes", "")
            
            # 确保reading_notes目录存在
            notes_dir = "reading_notes"
            os.makedirs(notes_dir, exist_ok=True)
            
            # 生成文件名
            title = article_data.get("title", "未知标题")
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')
            
            if custom_filename:
                filename = f"{custom_filename}_{note_style}笔记.md"
            else:
                filename = f"{safe_title}_{note_style}笔记.md"
            
            file_path = os.path.join(notes_dir, filename)
            
            # 保存笔记文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(notes_content)
            
            file_size = os.path.getsize(file_path)
            logger.info(f"读书笔记已保存到: {file_path}")
        
        # 返回完整结果
        return json.dumps({
            "status": "success",
            "message": "文章爬取、分析和笔记生成完成",
            "article_info": {
                "title": article_data.get("title"),
                "author": article_data.get("author"),
                "publish_time": article_data.get("publish_time"),
                "word_count": article_data.get("word_count"),
                "images_count": len(article_data.get("images", [])),
                "download_success": sum(1 for img in article_data.get("images", []) if img.get("download_success", False))
            },
            "analysis_summary": {
                "keywords_count": len(analysis_data.get("keywords", [])) if analysis_data.get("status") == "success" else 0,
                "has_summary": "summary" in analysis_data if analysis_data.get("status") == "success" else False,
                "images_analyzed": len(analysis_data.get("images", [])) if analysis_data.get("status") == "success" else 0
            },
            "notes_info": {
                "style": note_style,
                "word_count": notes_data.get("word_count", 0),
                "file_path": file_path if notes_data.get("status") == "success" else None,
                "file_size": file_size if notes_data.get("status") == "success" else 0
            },
            "files_created": {
                "article_files": spider.get_saved_files_info() if save_success else [],
                "notes_file": file_path if notes_data.get("status") == "success" else None
            },
            "processing_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"一站式处理失败: {e}")
        return json.dumps({
            "status": "error",
            "message": f"处理失败: {str(e)}",
            "step": "未知步骤"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
async def create_and_save_reading_notes(article_data: dict, note_style: str = "summary", save_to_file: bool = True, custom_filename: str = None) -> str:
    """
    生成读书笔记并保存到文件
    
    Args:
        article_data: 文章数据对象，包含标题、内容等信息
        note_style: 笔记风格：summary(摘要式), detailed(详细式), mind_map(思维导图式), key_points(要点式), one_sentence(一句话总结)
        save_to_file: 是否保存到文件，默认为True
        custom_filename: 自定义文件名（可选）
    
    Returns:
        操作结果的JSON字符串
    """
    try:
        if not article_data or not isinstance(article_data, dict):
            return json.dumps({
                "status": "error",
                "message": "article_data 必须是字典格式的文章数据"
            }, ensure_ascii=False, indent=2)
        
        logger.info(f"创建并保存读书笔记: note_style={note_style}, save_to_file={save_to_file}")
        
        # 生成读书笔记
        notes_result = await generate_reading_notes(article_data, note_style)
        notes_data = json.loads(notes_result)
        
        if notes_data.get("status") != "success":
            return notes_result
        
        notes_content = notes_data.get("notes", "")
        
        result = {
            "status": "success",
            "note_style": note_style,
            "notes_generated": True,
            "notes_word_count": len(notes_content),
            "generated_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 如果需要保存到文件
        if save_to_file:
            # 生成文件名
            if not custom_filename:
                title = article_data.get("title", "未知文章")
                # 清理标题作为文件名
                safe_title = re.sub(r'[^\w\s-]', '', title)
                safe_title = re.sub(r'[-\s]+', '-', safe_title)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                custom_filename = f"读书笔记_{safe_title}_{note_style}_{timestamp}"
            
            # 确保文件名以.md结尾（Markdown格式）
            if not custom_filename.endswith('.md'):
                custom_filename += '.md'
            
            # 创建notes目录
            notes_dir = "reading_notes"
            os.makedirs(notes_dir, exist_ok=True)
            
            # 完整文件路径
            file_path = os.path.join(notes_dir, custom_filename)
            
            # 保存文件
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(notes_content)
                
                result.update({
                    "file_saved": True,
                    "file_path": file_path,
                    "file_size": len(notes_content.encode('utf-8'))
                })
                
                logger.info(f"读书笔记已保存到: {file_path}")
                
            except Exception as e:
                result.update({
                    "file_saved": False,
                    "save_error": str(e)
                })
                logger.error(f"保存笔记文件失败: {e}")
        else:
            result.update({
                "file_saved": False,
                "notes_content": notes_content
            })
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"创建并保存读书笔记失败: {e}")
        return json.dumps({
            "status": "error",
            "message": f"操作失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
async def save_article_to_file(article_data: dict, custom_filename: str = None) -> str:
    """
    将文章数据保存到文件（JSON、TXT、HTML格式）
    
    Args:
        article_data: 文章数据对象
        custom_filename: 自定义文件名（可选）
    
    Returns:
        保存结果的字符串
    """
    try:
        if not article_data or not isinstance(article_data, dict):
            return "错误：article_data 必须是字典格式的文章数据"
        
        # 获取爬虫实例
        spider = get_spider_instance()
        
        # 保存文章
        success = spider.save_article_to_file(article_data, custom_filename)
        
        if success:
            return "文章保存成功！已生成 JSON、TXT、HTML 格式的文件"
        else:
            return "错误：文章保存失败"
            
    except Exception as e:
        logger.error(f"保存文章失败: {e}")
        return f"错误：保存失败 - {str(e)}"

def cleanup():
    """清理资源"""
    global spider_instance
    if spider_instance:
        try:
            spider_instance.close()
            logger.info("爬虫实例已关闭")
        except Exception as e:
            logger.error(f"关闭爬虫实例失败: {e}")

if __name__ == "__main__":
    try:
        # 注册清理函数
        import atexit
        atexit.register(cleanup)
        
        logger.info("启动微信公众号文章爬取 MCP 服务器...")
        
        # 以标准 I/O 方式运行 MCP 服务器
        mcp.run(transport='stdio')
        
    except Exception as e:
        import traceback
        logger.error(f"服务器运行失败: {e}")
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        sys.exit(1) 