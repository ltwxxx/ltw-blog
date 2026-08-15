#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guestbook 留言板模块生成器
生成留言板页面和主页预览
"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import json

def setup_template_env():
    """设置 Jinja2 模板环境"""
    template_dir = Path(__file__).parent.parent.parent.parent / "templates"
    return Environment(
        loader=FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True
    )

def load_json_file(file_path):
    """加载 JSON 文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 {file_path} 失败: {e}")
        return None

def generate_guestbook_page():
    """生成留言板页面"""
    env = setup_template_env()
    
    root_dir = Path(__file__).parent.parent.parent.parent
    frame_file = root_dir / "data" / "guestbook" / "frame.json"
    title_file = root_dir / "data" / "guestbook" / "title.json"
    
    frame_config = load_json_file(frame_file)
    title_config = load_json_file(title_file)
    
    if not frame_config or not title_config:
        print("❌ 无法加载留言板配置")
        return
    
    template = env.get_template('sections/guestbook/page.html')
    html_content = template.render(
        frame=frame_config,
        title_config=title_config
    )
    
    # 保存文件
    output_dir = root_dir / "html" / "guestbook"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "index.html"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 生成留言板页面: {output_file}")

def generate_guestbook_preview_html():
    """生成留言板预览区域HTML"""
    env = setup_template_env()
    
    root_dir = Path(__file__).parent.parent.parent.parent
    title_file = root_dir / "data" / "guestbook" / "title.json"
    
    title_config = load_json_file(title_file)
    
    if not title_config:
        print("无法加载留言板配置")
        return ""
    
    template = env.get_template('home/guestbook_preview.html')
    return template.render(
        title=title_config.get('title', '留言板'),
        subtitle=title_config.get('subtitle', '欢迎留下您的想法和建议')
    )

def generate_guestbook_page_and_home():
    """生成留言板页面并更新主页"""
    # 生成留言板页面
    generate_guestbook_page()
    
    # 更新主页预览
    try:
        from scripts.home.generator import generate_home_html
        generate_home_html()
        print("✅ 主页预览已更新")
    except Exception as e:
        print(f"⚠️ 更新主页预览失败: {e}")

if __name__ == "__main__":
    generate_guestbook_page_and_home()
