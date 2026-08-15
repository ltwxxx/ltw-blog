#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robots.txt生成器
生成robots.txt文件
"""

from pathlib import Path

def get_site_url():
    """获取网站URL"""
    import json
    root_dir = Path(__file__).parent.parent.parent
    frame_file = root_dir / "data" / "frame.json"
    try:
        with open(frame_file, 'r', encoding='utf-8') as f:
            frame_config = json.load(f)
            return frame_config.get('site_url', 'https://yourdomain.com')
    except Exception:
        return 'https://yourdomain.com'

def generate_robots():
    """生成robots.txt文件"""
    root_dir = Path(__file__).parent.parent.parent
    output_file = root_dir / "html" / "robots.txt"
    site_url = get_site_url()
    
    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    robots_content = """# robots.txt
# 允许所有搜索引擎抓取

User-agent: *
Allow: /

# 禁止抓取临时文件和系统文件
Disallow: /html/
Disallow: /*.json$
Disallow: /*.md$

# 网站地图
Sitemap: {}/sitemap.xml
""".format(site_url)
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(robots_content)
    
    print(f"✅ 生成robots.txt: {output_file}")
    return True

if __name__ == "__main__":
    generate_robots()
