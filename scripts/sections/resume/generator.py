#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历页面生成器
生成独立的简历页面，包含PDF预览和下载功能
"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader

def setup_template_env():
    """设置 Jinja2 模板环境"""
    template_dir = Path(__file__).parent.parent.parent.parent / "templates"
    return Environment(
        loader=FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True
    )

def load_resume_config():
    """加载简历页面配置"""
    from scripts.common.config import load_frame_config

    # 加载简历页面框架配置
    frame_config = load_frame_config('resume')

    # 确保PDF路径正确
    if 'pdf_path' not in frame_config:
        frame_config['pdf_path'] = 'data/resume/resume.pdf'

    return frame_config

def generate_resume_page_html():
    """生成简历页面HTML"""
    # 设置模板环境
    env = setup_template_env()

    # 加载配置
    config = load_resume_config()

    # 生成各部分HTML
    nav_html = generate_resume_nav_html(env, config)
    content_html = generate_resume_content_html(env, config)
    footer_html = generate_resume_footer_html(env, config)

    # 渲染完整页面
    base_template = env.get_template('base.html')
    html_content = base_template.render(
        site_title=config.get('page_title', '简历页面'),
        nav_html=nav_html,
        content_html=content_html,
        footer_html=footer_html
    )

    return html_content

def generate_resume_nav_html(env, config):
    """生成简历页面专用导航栏"""
    template = env.get_template('sections/resume/nav.html')
    return template.render(**config)

def generate_resume_content_html(env, config):
    """生成简历页面内容"""
    template = env.get_template('sections/resume/page.html')
    return template.render(**config)

def generate_resume_footer_html(env, config):
    """生成简历页面页脚"""
    template = env.get_template('footer.html')
    return template.render(
        footer_text=config.get('footer_text', '© 2025 个人主页'),
        footer_tagline=config.get('footer_extra', ''),
        page_type='resume'
    )

def generate_resume_page():
    """生成简历页面并保存到文件"""
    # 生成HTML内容
    html_content = generate_resume_page_html()

    # 保存到文件 - 生成到 html/resume/index.html
    root_dir = Path(__file__).parent.parent.parent.parent
    output_dir = root_dir / "html" / "resume"
    output_file = output_dir / "index.html"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # 复制PDF文件到html/resume目录
    import shutil
    pdf_source = root_dir / "data" / "resume" / "resume.pdf"
    pdf_dest = output_dir / "resume.pdf"
    if pdf_source.exists():
        shutil.copy2(pdf_source, pdf_dest)
        print(f"✅ PDF文件已复制: {pdf_dest}")
    else:
        print(f"⚠️ 警告：PDF文件不存在: {pdf_source}")

    print(f"简历页面 HTML 已生成: {output_file}")

if __name__ == "__main__":
    generate_resume_page()
