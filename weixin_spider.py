#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号文章爬虫 - 集成到当前MCP项目
支持文章内容抓取、图片下载、多种格式保存
"""

import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import os
import logging
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse
import hashlib
from pathlib import Path
import sys
import shutil
import subprocess
import base64
from urllib.parse import unquote

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WeixinSpider:
    def __init__(self, headless=True, wait_time=10, download_images=True):
        """
        初始化爬虫
        :param headless: 是否使用无头模式
        :param wait_time: 页面等待时间
        :param download_images: 是否下载图片
        """
        self.driver = None
        self.wait_time = wait_time
        self.download_images = download_images
        self.session = requests.Session()
        self.setup_session()
        self.setup_driver(headless)
        
    def setup_session(self):
        """设置requests会话"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def setup_driver(self, headless=True):
        """设置Chrome浏览器驱动"""
        try:
            logger.info("正在设置Chrome浏览器驱动...")
            
            options = Options()
            
            if headless:
                options.add_argument('--headless')
                logger.info("使用无头模式")
            
            # 基本设置
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-logging')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--disable-features=TranslateUI')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-renderer-backgrounding')
            options.add_argument('--disable-ipc-flooding-protection')
            options.add_argument('--disable-hang-monitor')
            options.add_argument('--disable-client-side-phishing-detection')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-prompt-on-repost')
            options.add_argument('--disable-sync')
            options.add_argument('--no-first-run')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-component-update')
            options.add_argument('--disable-background-networking')
            options.add_argument('--disable-component-extensions-with-background-pages')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            # 解决渲染器连接问题的关键参数
            options.add_argument('--single-process')
            options.add_argument('--disable-gpu-sandbox')
            options.add_argument('--disable-software-rasterizer')
            options.add_argument('--remote-debugging-port=0')
            options.add_argument('--disable-dev-tools')
            
            # 内存和性能优化
            options.add_argument('--memory-pressure-off')
            options.add_argument('--max_old_space_size=4096')
            
            # 设置用户代理
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36')
            
            # 排除自动化标识
            options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # 设置prefs以避免各种弹窗
            prefs = {
                "profile.default_content_setting_values": {
                    "notifications": 2,
                    "geolocation": 2,
                    "media_stream": 2,
                },
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2 if not self.download_images else 1
            }
            options.add_experimental_option("prefs", prefs)
            
            # 优先尝试使用系统ChromeDriver
            try:
                logger.info("尝试使用系统ChromeDriver...")
                chromedriver_path = shutil.which('chromedriver')
                if chromedriver_path:
                    logger.info(f"找到ChromeDriver路径: {chromedriver_path}")
                    service = Service(chromedriver_path)
                    self.driver = webdriver.Chrome(service=service, options=options)
                    logger.info("使用系统ChromeDriver成功初始化")
                else:
                    raise Exception("未找到系统ChromeDriver")
            except Exception as system_error:
                logger.warning(f"系统ChromeDriver失败: {system_error}")
                try:
                    logger.info("使用webdriver-manager自动下载兼容的ChromeDriver...")
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=options)
                    logger.info("使用webdriver-manager成功初始化ChromeDriver")
                except Exception as wdm_error:
                    logger.error(f"webdriver-manager失败: {wdm_error}")
                    try:
                        logger.info("尝试使用默认ChromeDriver配置...")
                        self.driver = webdriver.Chrome(options=options)
                        logger.info("使用默认配置成功初始化ChromeDriver")
                    except Exception as default_error:
                        logger.error(f"默认配置也失败: {default_error}")
                        raise RuntimeError(f"所有ChromeDriver初始化方法都失败: {default_error}")
            
            # 执行脚本隐藏webdriver属性
            try:
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
                self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']})")
            except Exception as script_error:
                logger.warning(f"执行隐藏脚本失败: {script_error}")
            
            # 设置窗口大小
            try:
                self.driver.set_window_size(1920, 1080)
            except Exception as e:
                logger.warning(f"设置窗口大小失败: {e}")
            
            logger.info("Chrome浏览器驱动设置完成")
            
        except Exception as e:
            logger.error(f"设置Chrome浏览器驱动失败: {e}")
            raise

    def crawl_article_by_url(self, url, retry_times=3):
        """
        通过URL爬取微信公众号文章
        :param url: 文章URL
        :param retry_times: 重试次数
        :return: 文章数据字典
        """
        for attempt in range(retry_times):
            try:
                logger.info(f"第{attempt + 1}次尝试爬取文章: {url}")
                
                # 访问文章页面
                self.driver.get(url)
                
                # 等待页面加载
                WebDriverWait(self.driver, self.wait_time).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # 滚动页面确保内容加载完整
                self._scroll_page()
                
                # 提取文章内容
                article_data = self._extract_article_content()
                article_data['url'] = url
                article_data['crawl_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                logger.info(f"成功爬取文章: {article_data.get('title', 'Unknown')}")
                return article_data
                
            except Exception as e:
                logger.error(f"第{attempt + 1}次爬取失败: {e}")
                if attempt == retry_times - 1:
                    logger.error(f"所有重试都失败了，放弃爬取: {url}")
                    return None
                time.sleep(2)  # 重试前等待
        
        return None

    def _scroll_page(self):
        """滚动页面以加载所有内容"""
        try:
            # 获取页面总高度
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # 滚动到页面底部
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # 等待新内容加载
                time.sleep(2)
                
                # 计算新的页面高度
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                if new_height == last_height:
                    break
                    
                last_height = new_height
                
            # 滚动回顶部
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
        except Exception as e:
            logger.warning(f"滚动页面时出错: {e}")

    def _extract_article_content(self):
        """提取文章内容"""
        try:
            # 等待关键元素加载
            WebDriverWait(self.driver, self.wait_time).until(
                EC.any_of(
                    EC.presence_of_element_located((By.ID, "js_content")),
                    EC.presence_of_element_located((By.CLASS_NAME, "rich_media_content")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".rich_media_area_primary"))
                )
            )
            
            # 获取页面HTML
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 提取标题
            title_selectors = [
                '#activity-name',
                '.rich_media_title',
                'h1',
                '.title'
            ]
            title = self._get_text_by_selectors(soup, title_selectors, "未知标题")
            
            # 提取作者
            author_selectors = [
                '#js_author_name',
                '.rich_media_meta_text',
                '.author',
                '.by'
            ]
            author = self._get_text_by_selectors(soup, author_selectors, "未知作者")
            
            # 提取发布时间
            time_selectors = [
                '#publish_time',
                '.rich_media_meta_text',
                '.time',
                '.date'
            ]
            publish_time = self._get_text_by_selectors(soup, time_selectors, "未知时间")
            
            # 提取正文内容
            content_selectors = [
                '#js_content',
                '.rich_media_content',
                '.content',
                'article'
            ]
            content_element = self._get_element_by_selectors(soup, content_selectors)
            
            if content_element:
                # 提取纯文本内容
                content_text = content_element.get_text(strip=True, separator='\n')
                
                # 提取HTML内容
                content_html = str(content_element)
                
                # 提取图片信息
                images = self._extract_images_from_content(content_element)
            else:
                content_text = "无法提取内容"
                content_html = ""
                images = []
            
            # 构建文章数据
            article_data = {
                'title': title,
                'author': author,
                'publish_time': publish_time,
                'content': content_text,
                'content_html': content_html,
                'images': images,
                'word_count': len(content_text),
                'image_count': len(images)
            }
            
            return article_data
            
        except Exception as e:
            logger.error(f"提取文章内容失败: {e}")
            return {
                'title': '提取失败',
                'author': '未知',
                'publish_time': '未知',
                'content': '内容提取失败',
                'content_html': '',
                'images': [],
                'word_count': 0,
                'image_count': 0
            }

    def _extract_images_from_content(self, content_element):
        """从内容中提取图片信息"""
        images = []
        
        try:
            # 查找所有图片元素
            img_elements = content_element.find_all('img')
            
            for i, img in enumerate(img_elements):
                img_info = {
                    'index': i + 1,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'original_src': img.get('src', ''),
                    'data_src': img.get('data-src', ''),
                    'download_success': False,
                    'local_path': '',
                    'filename': ''
                }
                
                # 确定实际的图片URL
                img_url = img_info['data_src'] or img_info['original_src']
                
                if img_url:
                    # 处理相对URL
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = 'https://mp.weixin.qq.com' + img_url
                    
                    img_info['url'] = img_url
                    images.append(img_info)
                    
        except Exception as e:
            logger.error(f"提取图片信息失败: {e}")
            
        return images

    def _get_text_by_selectors(self, soup, selectors, default=""):
        """通过选择器列表获取文本内容"""
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text:
                        return text
            except Exception:
                continue
        return default

    def _get_element_by_selectors(self, soup, selectors):
        """通过选择器列表获取元素"""
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    return element
            except Exception:
                continue
        return None

    def _download_image(self, img_url, save_dir, filename_prefix="img"):
        """下载单张图片"""
        try:
            # 检查是否为data URL
            if img_url.startswith('data:'):
                return self._save_data_url_image_as_png(img_url, save_dir, filename_prefix)
            
            # 发起请求下载图片
            response = self.session.get(img_url, timeout=30)
            response.raise_for_status()
            
            # 获取内容类型
            content_type = response.headers.get('content-type', '')
            
            # 确定文件扩展名
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'gif' in content_type:
                ext = '.gif'
            elif 'webp' in content_type:
                ext = '.webp'
            else:
                # 从URL推断扩展名
                parsed_url = urlparse(img_url)
                path = parsed_url.path.lower()
                if path.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    ext = os.path.splitext(path)[1]
                else:
                    ext = '.jpg'  # 默认为jpg
            
            # 生成文件名
            timestamp = int(time.time() * 1000)
            filename = f"{filename_prefix}_{timestamp}{ext}"
            filepath = os.path.join(save_dir, filename)
            
            # 保存图片
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"图片下载成功: {filename}")
            return {
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'size': len(response.content)
            }
            
        except Exception as e:
            logger.error(f"下载图片失败 {img_url}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _save_data_url_image_as_png(self, data_url, save_dir, filename_prefix="img"):
        """保存data URL格式的图片为PNG"""
        try:
            # 解析data URL
            header, data = data_url.split(',', 1)
            
            # 解码base64数据
            image_data = base64.b64decode(data)
            
            # 生成文件名
            timestamp = int(time.time() * 1000)
            filename = f"{filename_prefix}_{timestamp}.png"
            filepath = os.path.join(save_dir, filename)
            
            # 保存图片
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            logger.info(f"Data URL图片保存成功: {filename}")
            return {
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'size': len(image_data)
            }
            
        except Exception as e:
            logger.error(f"保存Data URL图片失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _download_all_images(self, images_info, save_dir):
        """下载所有图片"""
        if not self.download_images:
            logger.info("图片下载已禁用")
            return
        
        # 创建保存目录
        os.makedirs(save_dir, exist_ok=True)
        
        success_count = 0
        for i, img_info in enumerate(images_info):
            try:
                img_url = img_info.get('url')
                if not img_url:
                    continue
                
                result = self._download_image(img_url, save_dir, f"img_{i+1}")
                
                if result['success']:
                    img_info['download_success'] = True
                    img_info['local_path'] = result['filepath']
                    img_info['filename'] = result['filename']
                    success_count += 1
                else:
                    img_info['download_success'] = False
                    img_info['error'] = result.get('error', '未知错误')
                    
            except Exception as e:
                logger.error(f"处理图片 {i+1} 时出错: {e}")
                img_info['download_success'] = False
                img_info['error'] = str(e)
        
        logger.info(f"图片下载完成: {success_count}/{len(images_info)}")

    def get_saved_files_info(self):
        """获取最近保存的文件信息"""
        if hasattr(self, '_last_saved_files'):
            return self._last_saved_files
        return []

    def _replace_image_urls_in_html(self, content_html, images):
        """替换HTML内容中的图片URL为本地相对路径"""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(content_html, 'html.parser')
            img_tags = soup.find_all('img')
            
            for img_tag in img_tags:
                original_src = img_tag.get('src', '')
                data_src = img_tag.get('data-src', '')
                
                # 查找对应的本地图片
                for img_info in images:
                    img_url = img_info.get('url', '')
                    if (img_url == original_src or img_url == data_src) and img_info.get('download_success'):
                        # 替换为相对路径
                        local_filename = img_info.get('filename', '')
                        if local_filename:
                            img_tag['src'] = f"images/{local_filename}"
                            # 移除data-src属性
                            if img_tag.get('data-src'):
                                del img_tag['data-src']
                            # 添加alt属性
                            if not img_tag.get('alt'):
                                img_tag['alt'] = f"图片 {img_info.get('index', '')}"
                            break
                else:
                    # 如果图片下载失败，显示占位符
                    placeholder_div = soup.new_tag('div', **{'class': 'image-placeholder'})
                    placeholder_div.string = f"图片加载失败: {img_tag.get('alt', '未知图片')}"
                    img_tag.replace_with(placeholder_div)
            
            return str(soup)
            
        except Exception as e:
            logger.error(f"替换图片URL失败: {e}")
            return content_html

    def save_article_to_file(self, article_data, custom_filename=None):
        """保存文章到文件"""
        try:
            # 生成文件名
            if custom_filename:
                base_filename = custom_filename
            else:
                # 清理标题作为文件名
                title = article_data.get('title', 'unknown_article')
                # 移除特殊字符
                safe_title = re.sub(r'[^\w\s-]', '', title)
                safe_title = re.sub(r'[-\s]+', '-', safe_title)
                base_filename = safe_title[:50]  # 限制长度
            
            # 创建保存目录
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_dir = f"articles/{base_filename}_{timestamp}"
            os.makedirs(save_dir, exist_ok=True)
            

            
            # 保存纯文本格式
            txt_path = os.path.join(save_dir, f"{base_filename}.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f"标题: {article_data.get('title', '')}\n")
                f.write(f"作者: {article_data.get('author', '')}\n")
                f.write(f"发布时间: {article_data.get('publish_time', '')}\n")
                f.write(f"爬取时间: {article_data.get('crawl_time', '')}\n")
                f.write(f"字数: {article_data.get('word_count', 0)}\n")
                f.write(f"图片数: {article_data.get('image_count', 0)}\n")
                f.write(f"URL: {article_data.get('url', '')}\n")
                f.write("-" * 50 + "\n")
                f.write(article_data.get('content', ''))
            
            # 下载图片（在保存JSON之前）
            images = article_data.get('images', [])
            if images and self.download_images:
                images_dir = os.path.join(save_dir, 'images')
                self._download_all_images(images, images_dir)
                # 更新article_data中的图片信息
                article_data['images'] = images
            
            # 保存JSON格式（包含更新后的图片状态）
            json_path = os.path.join(save_dir, f"{base_filename}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2)
            
            # 处理HTML内容中的图片路径
            content_html = article_data.get('content_html', '')
            if content_html and images:
                # 替换HTML中的图片URL为本地相对路径
                content_html = self._replace_image_urls_in_html(content_html, images)
            
            # 保存HTML格式
            html_path = os.path.join(save_dir, f"{base_filename}.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article_data.get('title', '')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
        .header {{ border-bottom: 2px solid #ccc; padding-bottom: 20px; margin-bottom: 20px; }}
        .content {{ margin-top: 20px; }}
        img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; margin: 10px 0; }}
        .image-placeholder {{ 
            background-color: #f5f5f5; 
            border: 2px dashed #ccc; 
            padding: 20px; 
            text-align: center; 
            color: #666; 
            margin: 10px 0; 
            border-radius: 4px; 
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{article_data.get('title', '')}</h1>
        <p><strong>作者:</strong> {article_data.get('author', '')}</p>
        <p><strong>发布时间:</strong> {article_data.get('publish_time', '')}</p>
        <p><strong>字数:</strong> {article_data.get('word_count', 0)}</p>
    </div>
    <div class="content">
        {content_html}
    </div>
</body>
</html>""")
            
            # 记录保存的文件信息
            self._last_saved_files = [
                {"type": "json", "path": json_path},
                {"type": "txt", "path": txt_path}, 
                {"type": "html", "path": html_path}
            ]
            if images and self.download_images:
                images_dir = os.path.join(save_dir, 'images')
                self._last_saved_files.append({"type": "images_dir", "path": images_dir})
            
            logger.info(f"文章保存成功: {save_dir}")
            return True
            
        except Exception as e:
            logger.error(f"保存文章失败: {e}")
            return False

    def close(self):
        """关闭浏览器"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                logger.info("浏览器已关闭")
        except Exception as e:
            logger.error(f"关闭浏览器时出错: {e}")

    def __del__(self):
        """析构函数"""
        self.close() 