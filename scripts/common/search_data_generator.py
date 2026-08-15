#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索数据生成器
生成包含所有博客和项目信息的JSON文件，用于前端搜索功能
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到路径
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

def load_json_file(file_path):
    """加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 {file_path} 失败: {e}")
        return None

def get_all_blog_items():
    """获取所有博客文章数据"""
    root_dir = Path(__file__).parent.parent.parent
    blog_dir = root_dir / "data" / "blog"
    blog_config_file = blog_dir / "title.json"
    
    blog_items = []
    
    if not blog_config_file.exists():
        return blog_items
    
    blog_config = load_json_file(blog_config_file)
    if not blog_config:
        return blog_items
    
    categories = blog_config.get('categories', [])
    
    for category in categories:
        category_id = category.get('id')
        category_dir = blog_dir / category_id
        
        if not category_dir.exists() or not category_dir.is_dir():
            continue
        
        # 扫描该分类下的所有文章
        for article_dir in category_dir.iterdir():
            if not article_dir.is_dir():
                continue
            
            card_file = article_dir / "card.json"
            if not card_file.exists():
                continue
            
            card_data = load_json_file(card_file)
            if not card_data or card_data.get('status') != 'published':
                continue
            
            # 构建文章URL
            article_url = f"blog/{category_id}/{article_dir.name}/index.html"
            
            blog_items.append({
                'type': 'blog',
                'title': card_data.get('title', ''),
                'summary': card_data.get('summary', ''),
                'category': category.get('name', ''),
                'tags': card_data.get('tags', []),
                'date': card_data.get('date', ''),
                'url': article_url
            })
    
    return blog_items

def get_all_project_items():
    """获取所有项目数据"""
    root_dir = Path(__file__).parent.parent.parent
    project_dir = root_dir / "data" / "project"
    
    project_items = []
    
    if not project_dir.exists():
        return project_items
    
    # 扫描所有项目目录
    for project_dir_item in project_dir.iterdir():
        if not project_dir_item.is_dir() or project_dir_item.name in ['__pycache__']:
            continue
        
        card_file = project_dir_item / "card.json"
        if not card_file.exists():
            continue
        
        card_data = load_json_file(card_file)
        if not card_data or card_data.get('status') not in ['published', 'completed', 'in-development']:
            continue
        
        # 构建项目URL
        project_url = f"project/{project_dir_item.name}/index.html"
        
        project_items.append({
            'type': 'project',
            'title': card_data.get('title', ''),
            'summary': card_data.get('summary', ''),
            'category': card_data.get('category', ''),
            'technologies': card_data.get('technologies', []),
            'date': card_data.get('date', ''),
            'url': project_url
        })
    
    return project_items

def generate_search_data():
    """生成搜索数据JSON文件"""
    root_dir = Path(__file__).parent.parent.parent
    output_file = root_dir / "html" / "search-data.json"
    
    # 获取所有数据
    blog_items = get_all_blog_items()
    project_items = get_all_project_items()
    
    # 合并数据
    all_items = blog_items + project_items
    
    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 写入JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 搜索数据生成完成：{len(blog_items)} 篇博客，{len(project_items)} 个项目")
    return len(all_items)

if __name__ == "__main__":
    generate_search_data()
