#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号文章爬取示例
演示如何使用微信爬虫功能
"""

import json
import sys
from weixin_spider import WeixinSpider

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 微信公众号文章爬取示例")
    print("=" * 60)
    
    # 示例URL（请替换为实际的微信文章URL）
    example_url = "https://mp.weixin.qq.com/s/example-article-url"
    
    print(f"\n📝 示例说明：")
    print(f"本示例展示如何使用微信爬虫功能爬取公众号文章")
    print(f"请将示例URL替换为实际的微信文章URL")
    print(f"示例URL: {example_url}")
    
    # 获取用户输入
    print(f"\n🔗 请输入要爬取的微信文章URL：")
    print(f"（直接按回车使用示例URL，输入'quit'退出）")
    
    user_input = input().strip()
    
    if user_input.lower() == 'quit':
        print("👋 退出程序")
        return
    
    if user_input:
        url = user_input
    else:
        url = example_url
        print(f"使用示例URL: {url}")
    
    # 验证URL格式
    if not url.startswith("https://mp.weixin.qq.com/"):
        print("❌ 错误：URL必须以 https://mp.weixin.qq.com/ 开头")
        return
    
    # 创建爬虫实例
    print(f"\n🕷️ 初始化爬虫...")
    try:
        spider = WeixinSpider(
            headless=True,        # 使用无头模式
            wait_time=10,         # 等待时间10秒
            download_images=True  # 下载图片
        )
        print("✅ 爬虫初始化成功")
    except Exception as e:
        print(f"❌ 爬虫初始化失败: {e}")
        print("💡 请检查Chrome浏览器是否已安装")
        return
    
    try:
        # 爬取文章
        print(f"\n📄 开始爬取文章...")
        print(f"URL: {url}")
        
        article_data = spider.crawl_article_by_url(url)
        
        if article_data:
            print(f"✅ 文章爬取成功！")
            
            # 显示文章信息
            print(f"\n📊 文章信息：")
            print(f"标题: {article_data.get('title', '未知')}")
            print(f"作者: {article_data.get('author', '未知')}")
            print(f"发布时间: {article_data.get('publish_time', '未知')}")
            print(f"字数: {article_data.get('word_count', 0)}")
            print(f"图片数量: {len(article_data.get('images', []))}")
            
            # 保存文章
            print(f"\n💾 保存文章到文件...")
            success = spider.save_article_to_file(article_data)
            
            if success:
                print(f"✅ 文章保存成功！")
                print(f"📁 文件保存在 articles/ 目录下")
                print(f"包含格式: JSON、TXT、HTML")
                if article_data.get('images'):
                    print(f"📸 图片保存在对应的 images/ 子目录中")
            else:
                print(f"❌ 文章保存失败")
            
            # 显示文章内容预览
            content = article_data.get('content', '')
            if content:
                print(f"\n📖 文章内容预览（前200字符）：")
                print("-" * 40)
                print(content[:200] + "..." if len(content) > 200 else content)
                print("-" * 40)
            
        else:
            print(f"❌ 文章爬取失败")
            print(f"💡 请检查URL是否正确，或网络连接是否正常")
            
    except Exception as e:
        print(f"❌ 爬取过程中出错: {e}")
        
    finally:
        # 关闭爬虫
        print(f"\n🔄 关闭爬虫...")
        spider.close()
        print(f"✅ 爬虫已关闭")
    
    print(f"\n" + "=" * 60)
    print(f"🎉 示例运行完成！")
    print(f"💡 如需在MCP客户端中使用，请运行: make run-all")
    print(f"=" * 60)

if __name__ == "__main__":
    main() 