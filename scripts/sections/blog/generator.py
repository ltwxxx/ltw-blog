#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
博客生成器
扫描 data/blog 目录，生成所有博客文章的卡片和完整页面
"""

from pathlib import Path
import json
import shutil
import re
from jinja2 import Environment, FileSystemLoader
import markdown

def setup_template_env():
    """设置 Jinja2 模板环境"""
    template_dir = Path(__file__).parent.parent.parent.parent / "templates"
    return Environment(
        loader=FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True
    )

def add_lazy_loading_to_images(html_content):
    """为HTML中的所有图片添加懒加载属性"""
    # 匹配 <img> 标签，如果还没有 loading 属性，则添加 loading="lazy"
    def add_lazy(match):
        img_tag = match.group(0)
        # 如果已经有 loading 属性，直接返回
        if 'loading=' in img_tag:
            return img_tag
        # 处理自闭合标签 <img ... /> 或普通标签 <img ... >
        if img_tag.endswith('/>'):
            return img_tag.replace('/>', ' loading="lazy" />')
        else:
            return img_tag.replace('>', ' loading="lazy">')
    
    # 匹配所有 <img> 标签
    pattern = r'<img[^>]*>'
    return re.sub(pattern, add_lazy, html_content)

def load_json_file(file_path):
    """加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 {file_path} 失败: {e}")
        return None

def prepare_card_data(card_data, category_name, article_name):
    """准备卡片数据，处理路径和URL"""
    card = card_data.copy()

    # 处理图片路径
    if card.get('image'):
        if card['image'].startswith('http'):
            # 如果是URL，直接使用
            card['image'] = card['image']
        else:
            # 如果是本地文件，确保是正确的相对路径
            if not card['image'].startswith('./'):
                card['image'] = f"./{card['image']}"

    # 生成内容页面URL（相对于文章目录）
    card['content_url'] = f"content.html"

    # 保存文章名称（用于分类页面）
    card['article_name'] = article_name

    # 设置卡片类型
    card['type'] = 'blog'

    return card

def generate_card_html(card_data):
    """生成卡片HTML片段"""
    env = setup_template_env()
    template = env.get_template('components/card.html')
    return template.render(card=card_data)

def generate_article_html(card_data, md_html_content, article_url=None):
    """生成完整文章HTML页面"""
    env = setup_template_env()
    template = env.get_template('components/article.html')
    
    # 加载SEO配置
    root_dir = Path(__file__).parent.parent.parent.parent
    from scripts.common.config import load_json_file
    frame_file = root_dir / "data" / "frame.json"
    frame_config = load_json_file(frame_file) or {}
    
    # 更新card_data，添加URL信息
    if article_url:
        card_data['url'] = article_url
    
    site_url = frame_config.get('site_url', 'https://yourdomain.com')
    
    return template.render(
        card=card_data,
        content_html=md_html_content,
        site_title="个人博客",
        site_url=site_url
    )

def scan_and_generate_blog():
    """扫描博客目录并生成所有文件"""
    print("🔍 开始扫描博客文章...")

    # 设置路径
    data_root = Path(__file__).parent.parent.parent.parent / "data" / "blog"
    output_root = Path(__file__).parent.parent.parent.parent / "html" / "blog"

    if not data_root.exists():
        print("❌ 博客数据目录不存在")
        return

    # 统计信息
    total_articles = 0
    generated_cards = 0
    generated_articles = 0

    # 扫描所有分类目录
    for category_dir in data_root.iterdir():
        if not category_dir.is_dir() or category_dir.name.startswith('.'):
            continue

        category_name = category_dir.name
        print(f"📂 处理分类: {category_name}")

        # 扫描分类下的文章目录
        for article_dir in category_dir.iterdir():
            if not article_dir.is_dir():
                continue

            article_name = article_dir.name
            card_file = article_dir / "card.json"
            content_file = article_dir / "content.md"

            if not card_file.exists():
                print(f"⚠️  跳过 {article_name}: 缺少 card.json")
                continue

            print(f"📝 处理文章: {article_name}")
            total_articles += 1

            # 读取卡片配置
            card_data = load_json_file(card_file)
            if not card_data:
                print(f"❌ 读取 {card_file} 失败")
                continue

            # 准备卡片数据
            prepared_card = prepare_card_data(card_data, category_name, article_name)

            # 读取并转换Markdown内容
            md_content = ""
            if content_file.exists():
                try:
                    with open(content_file, 'r', encoding='utf-8') as f:
                        md_content = f.read()
                except Exception as e:
                    print(f"⚠️ 读取 {content_file} 失败: {e}")

            # 转换Markdown为HTML
            html_content = markdown.markdown(
                md_content,
                extensions=['extra', 'codehilite', 'toc']
            )
            # 为所有图片添加懒加载
            html_content = add_lazy_loading_to_images(html_content)

            # 创建输出目录
            output_dir = output_root / category_name / article_name
            output_dir.mkdir(parents=True, exist_ok=True)

            try:
                # 生成卡片HTML
                card_html = generate_card_html(prepared_card)
                card_output = output_dir / "card.html"
                with open(card_output, 'w', encoding='utf-8') as f:
                    f.write(card_html)
                generated_cards += 1
                print(f"✅ 生成卡片: {card_output}")

                # 生成文章HTML
                article_url = f"blog/{category_name}/{article_name}/content.html"
                article_html = generate_article_html(prepared_card, html_content, article_url)
                article_output = output_dir / "content.html"
                with open(article_output, 'w', encoding='utf-8') as f:
                    f.write(article_html)
                generated_articles += 1
                print(f"✅ 生成文章: {article_output}")

                # 如果图片是本地文件，则复制整个文章目录
                if card_data.get('image') and not card_data['image'].startswith('http'):
                    shutil.copytree(article_dir, output_dir, dirs_exist_ok=True)
                    print(f"✅ 复制文章目录: {article_dir} → {output_dir}")
                else:
                    # 对于URL图片，只复制非图片文件
                    for item in article_dir.iterdir():
                        if item.is_file() and item.name != 'cover.png':
                            shutil.copy2(item, output_dir)
                    print(f"✅ 复制文章文件 (跳过URL图片): {article_dir} → {output_dir}")

            except Exception as e:
                print(f"❌ 生成失败: {e}")

    # 生成分类页面
    print("\n🏗️ 开始生成分类页面...")
    generate_category_pages()

    # 输出统计信息
    print("\n📊 生成统计:")
    print(f"   发现文章: {total_articles}")
    print(f"   生成卡片: {generated_cards}")
    print(f"   生成文章: {generated_articles}")
    print("🎉 博客生成完成！")

def get_all_cards_for_category(category_id):
    """获取指定分类下的所有文章卡片"""
    root_dir = Path(__file__).parent.parent.parent.parent
    blog_dir = root_dir / "data" / "blog" / category_id

    cards = []

    if blog_dir.exists():
        # 扫描所有子目录（文章）
        for article_dir in blog_dir.iterdir():
            if article_dir.is_dir():
                card_file = article_dir / "card.json"
                if card_file.exists():
                    card_data = load_json_file(card_file)
                    if card_data and card_data.get('status') == 'published':
                        # 构建文章路径
                        article_path = f"{category_id}/{article_dir.name}"
                        # 准备卡片数据
                        prepared_card = prepare_card_data(card_data, category_id, article_dir.name)
                        # 为分类页面添加文章名称
                        prepared_card['article_name'] = article_dir.name
                        cards.append(prepared_card)

    # 按日期排序，最新的在前
    cards.sort(key=lambda x: x.get('date', ''), reverse=True)

    return cards

def generate_category_pages():
    """生成所有分类的完整页面"""
    # 设置模板环境
    env = setup_template_env()

    # 加载框架配置
    frame_file = Path(__file__).parent.parent.parent.parent / "data" / "blog" / "frame.json"
    frame_config = load_json_file(frame_file)

    # 加载博客配置
    blog_config_file = Path(__file__).parent.parent.parent.parent / "data" / "blog" / "title.json"
    blog_config = load_json_file(blog_config_file)

    if not frame_config or not blog_config:
        print("❌ 无法加载框架或博客配置")
        return

    template = env.get_template('sections/blog/all_content_page.html')

    generated_pages = 0

    for category in blog_config.get('categories', []):
        # 获取该分类的所有文章
        category_cards = get_all_cards_for_category(category['id'])

        # 为分类页面调整图片路径（相对于分类页面）
        for card in category_cards:
            if card.get('image') and not card['image'].startswith('http'):
                if card['image'].startswith('./'):
                    image_name = card['image'][2:]  # 移除 ./
                    card['image'] = f"{card['article_name']}/{image_name}"

        if not category_cards:
            print(f"⚠️ 分类 '{category['name']}' 没有文章，跳过")
            continue

        # 准备模板数据
        template_data = {
            'frame': frame_config,
            'category_name': category['name'],
            'category_description': category.get('description', ''),
            'category_icon': category.get('icon', 'fa-folder'),
            'total_articles': len(category_cards),
            'cards': category_cards
        }

        # 生成HTML
        html_content = template.render(**template_data)

        # 保存文件
        output_dir = Path(__file__).parent.parent.parent.parent / "html" / "blog" / category['id']
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{category['id']}.html"
        output_file.write_text(html_content, encoding='utf-8')

        print(f"✅ 生成分类页面: {category['name']} ({len(category_cards)}篇文章)")
        generated_pages += 1

    print(f"📊 分类页面生成完成: {generated_pages}个页面")

def generate_blog_page():
    """生成博客页面并保存（如果需要的话）"""
    # 这里可以生成博客首页或其他页面
    pass

def scan_and_generate_blog_and_home():
    """生成博客页面并更新主页预览"""
    # 先生成博客页面
    scan_and_generate_blog()

    # 再更新主页预览
    try:
        from scripts.home.generator import generate_home_html
        generate_home_html()
        print("✅ 主页预览已更新")
    except Exception as e:
        print(f"⚠️ 更新主页预览失败: {e}")

if __name__ == "__main__":
    scan_and_generate_blog()
