#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网站地图生成器
生成sitemap.xml文件，包含所有页面URL
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from scripts.common.search_data_generator import get_all_blog_items, get_all_project_items

def load_json_file(file_path):
    """加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 {file_path} 失败: {e}")
        return None

def get_site_url():
    """获取网站URL"""
    root_dir = Path(__file__).parent.parent.parent
    frame_file = root_dir / "data" / "frame.json"
    frame_config = load_json_file(frame_file)
    return frame_config.get('site_url', 'https://yourdomain.com') if frame_config else 'https://yourdomain.com'

def generate_sitemap():
    """生成sitemap.xml文件"""
    root_dir = Path(__file__).parent.parent.parent
    output_file = root_dir / "html" / "sitemap.xml"
    site_url = get_site_url()
    
    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    urls = []
    
    # 1. 首页
    urls.append({
        'loc': f"{site_url}/home.html",
        'lastmod': datetime.now().strftime('%Y-%m-%d'),
        'changefreq': 'daily',
        'priority': '1.0'
    })
    
    # 2. 简历页
    urls.append({
        'loc': f"{site_url}/resume/index.html",
        'lastmod': datetime.now().strftime('%Y-%m-%d'),
        'changefreq': 'monthly',
        'priority': '0.9'
    })
    
    # 3. 项目列表页
    urls.append({
        'loc': f"{site_url}/project/index.html",
        'lastmod': datetime.now().strftime('%Y-%m-%d'),
        'changefreq': 'weekly',
        'priority': '0.8'
    })
    
    # 4. 文档页
    urls.append({
        'loc': f"{site_url}/docs/index.html",
        'lastmod': datetime.now().strftime('%Y-%m-%d'),
        'changefreq': 'monthly',
        'priority': '0.7'
    })
    
    # 5. 留言板
    urls.append({
        'loc': f"{site_url}/guestbook/index.html",
        'lastmod': datetime.now().strftime('%Y-%m-%d'),
        'changefreq': 'weekly',
        'priority': '0.7'
    })
    
    # 6. 所有博客文章
    blog_items = get_all_blog_items()
    for item in blog_items:
        urls.append({
            'loc': f"{site_url}/{item['url']}",
            'lastmod': item.get('date', datetime.now().strftime('%Y-%m-%d')),
            'changefreq': 'monthly',
            'priority': '0.8'
        })
    
    # 7. 博客分类页
    blog_config_file = root_dir / "data" / "blog" / "title.json"
    blog_config = load_json_file(blog_config_file)
    if blog_config:
        for category in blog_config.get('categories', []):
            urls.append({
                'loc': f"{site_url}/blog/{category['id']}/{category['id']}.html",
                'lastmod': datetime.now().strftime('%Y-%m-%d'),
                'changefreq': 'weekly',
                'priority': '0.7'
            })
    
    # 8. 所有项目详情页
    project_items = get_all_project_items()
    for item in project_items:
        urls.append({
            'loc': f"{site_url}/{item['url']}",
            'lastmod': item.get('date', datetime.now().strftime('%Y-%m-%d')),
            'changefreq': 'monthly',
            'priority': '0.8'
        })
    
    # 生成XML
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url in urls:
        xml_content += '  <url>\n'
        xml_content += f'    <loc>{url["loc"]}</loc>\n'
        xml_content += f'    <lastmod>{url["lastmod"]}</lastmod>\n'
        xml_content += f'    <changefreq>{url["changefreq"]}</changefreq>\n'
        xml_content += f'    <priority>{url["priority"]}</priority>\n'
        xml_content += '  </url>\n'
    
    xml_content += '</urlset>\n'
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"✅ 生成sitemap.xml: {output_file} (共 {len(urls)} 个URL)")
    return len(urls)

if __name__ == "__main__":
    generate_sitemap()
