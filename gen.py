#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一生成脚本入口
用于管理所有页面生成任务
"""

import argparse
import subprocess
import sys
import shutil
from pathlib import Path

def run_script(script_name, *args):
    """运行指定的生成脚本或模块"""
    try:
        if "." in script_name:
            # 模块形式：scripts.home.generator
            module_parts = script_name.split(".")
            module_name = ".".join(module_parts[:-1])
            func_name = module_parts[-1]

            # 动态导入模块
            module = __import__(module_name, fromlist=[func_name])
            func = getattr(module, func_name)
            # 调用生成函数
            func(*args)
        else:
            # 传统脚本形式
            script_path = Path(__file__).parent / "scripts" / f"{script_name}.py"
            if not script_path.exists():
                print(f"错误：脚本 {script_name}.py 不存在")
                return False

            cmd = [sys.executable, str(script_path)] + list(args)
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        print(f"✅ {script_name} 生成完成")
        return True
    except Exception as e:
        print(f"❌ {script_name} 生成失败：{e}")
        return False

def clean_html_dirs(only_targets=None):
    """清理HTML目录下的动态生成内容，确保与data目录完全同步。
    only_targets: 若指定，只清理这些模块对应的目录；否则清理 blog/project/docs/contact/resume 全部。
    """
    html_dir = Path(__file__).parent / "html"

    # 需要清理的目录（对应各个模块）
    all_dirs = ["blog", "project", "docs", "contact", "resume"]
    dirs_to_clean = only_targets if only_targets is not None else all_dirs

    cleaned_count = 0
    for dir_name in dirs_to_clean:
        if dir_name not in all_dirs:
            continue
        target_dir = html_dir / dir_name
        if target_dir.exists():
            shutil.rmtree(target_dir)
            print(f"🗑️ 已清理: {target_dir}")
            cleaned_count += 1

    if cleaned_count > 0:
        print(f"✅ 清理完成，共清理了 {cleaned_count} 个目录")
    else:
        print("ℹ️ 无需清理，所有目录都是干净的")

def main():
    # 确保从任意工作目录运行都能正确导入 scripts 包
    sys.path.insert(0, str(Path(__file__).resolve().parent))

    parser = argparse.ArgumentParser(description="统一页面生成器")
    parser.add_argument(
        "targets",
        nargs="*",
        help="要生成的页面（默认：all）"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细输出"
    )

    args = parser.parse_args()

    # 定义生成任务映射
    tasks = {
        "home": "scripts.home.generator.generate_home_html",
        "resume": "scripts.sections.resume.generator.generate_resume_page",
        "blog": "scripts.sections.blog.generator.scan_and_generate_blog_and_home",
        "project": "scripts.sections.project.generator.scan_and_generate_projects_and_home",
        "docs": "scripts.sections.docs.generator.generate_docs_page_and_home",
        "stack": "scripts.sections.stack.generator.generate_stack_page_and_home",
        "contact": "scripts.sections.contact.generator.generate_contact_page_and_home",
        "guestbook": "scripts.sections.guestbook.generator.generate_guestbook_page_and_home",
    }

    # 处理默认值和验证
    targets = args.targets if args.targets else ["all"]

    # 验证参数
    valid_targets = ["home", "resume", "blog", "project", "docs", "stack", "contact", "guestbook", "all"]
    for target in targets:
        if target not in valid_targets:
            parser.error(f"无效选择: '{target}' (选择: {', '.join(valid_targets)})")

    # 执行生成任务
    success_count = 0
    total_count = 0

    if "all" in targets:
        targets = list(tasks.keys())

    # 在生成之前清理HTML目录（只清理本次会重新生成的模块，避免误删其他模块输出）
    modules_to_clean = ["blog", "project", "docs", "contact", "resume"]
    targets_to_clean = [t for t in targets if t in modules_to_clean]
    if targets_to_clean:
        print("🧹 开始清理HTML目录...")
        clean_html_dirs(only_targets=targets_to_clean)
        print()

    for target in targets:
        if target in tasks:
            total_count += 1
            # 直接运行对应的脚本或模块
            if run_script(tasks[target]):
                success_count += 1
        else:
            print(f"警告：未知目标 '{target}'")
    
    # 如果生成了博客或项目，生成搜索数据
    if any(target in ['blog', 'project', 'all'] for target in targets):
        print("\n🔍 生成搜索数据...")
        try:
            from scripts.common.search_data_generator import generate_search_data
            generate_search_data()
        except Exception as e:
            print(f"⚠️ 搜索数据生成失败：{e}")
    
    # 生成SEO文件（sitemap.xml和robots.txt）
    if any(target in ['blog', 'project', 'home', 'all'] for target in targets):
        print("\n📄 生成SEO文件...")
        try:
            from scripts.common.sitemap_generator import generate_sitemap
            generate_sitemap()
        except Exception as e:
            print(f"⚠️ sitemap生成失败：{e}")
        
        try:
            from scripts.common.robots_generator import generate_robots
            generate_robots()
        except Exception as e:
            print(f"⚠️ robots.txt生成失败：{e}")
    
    # 复制语言数据文件
    if any(target in ['home', 'all'] for target in targets):
        print("\n🌐 复制语言数据文件...")
        try:
            import shutil
            root_dir = Path(__file__).parent
            i18n_source = root_dir / "data" / "i18n.json"
            i18n_dest = root_dir / "html" / "data" / "i18n.json"
            
            if i18n_source.exists():
                i18n_dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(i18n_source, i18n_dest)
                print(f"✅ 语言数据文件已复制: {i18n_dest}")
            else:
                print(f"⚠️ 语言数据文件不存在: {i18n_source}")
        except Exception as e:
            print(f"⚠️ 复制语言数据文件失败：{e}")
    
    # 输出结果统计
    if total_count > 0:
        print(f"\n📊 生成统计：{success_count}/{total_count} 成功")
        if success_count == total_count:
            print("🎉 所有页面生成完成！")
            return 0
        else:
            print("⚠️ 部分页面生成失败")
            return 1
    else:
        print("ℹ️ 没有执行任何生成任务")
        return 0

if __name__ == "__main__":
    sys.exit(main())