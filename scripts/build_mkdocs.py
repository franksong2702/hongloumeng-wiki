#!/usr/bin/env python3
"""
构建红楼梦 Wiki 的 MkDocs 站点。

步骤：
1. 复制所有 .md 文件到临时 docs/ 目录
2. 转换 wikilinks 为标准 markdown 链接
3. 转换 Obsidian 图片嵌入 ![[...]] 为 markdown 图片
4. 从 docs/ 目录结构生成 nav 配置
5. 写入 mkdocs.yml

此脚本不修改任何源文件。所有转换仅在输出目录中执行。
"""

import os
import re
import sys
import yaml
from pathlib import Path

# 目录映射：中文标题用于导航
DIR_NAMES = {
    "chapters": "章节导读",
    "texts": "原文",
    "simplified": "简体",
    "traditional": "繁体",
    "characters": "人物",
    "families": "家族",
    "locations": "地点",
    "events": "事件",
    "concepts": "概念",
    "motifs-symbols": "意象",
    "poetry": "诗词",
    "background": "背景",
    "redology": "红学",
    "timelines": "时间线",
    "maps": "图谱",
    "queries": "索引",
    "outputs": "输出产品",
    "templates": "模板",
    "images": "图片",
}

# 顶层文件
TOP_FILES = ["START_HERE", "README", "SCHEMA", "ROADMAP", "log", "index"]

# 需要跳过的文件/目录
SKIP = {
    "AGENTS.md",
    ".obsidian",
    ".git",
}


def wiki_to_relative_path(source_rel, target_abs):
    """
    将 Obsidian 完整路径链接转换为相对于源文件的相对链接。

    source_rel: 源文件相对于 wiki 根的路径（如 chapters/第001回.md）
    target_abs: 目标文件的 Obsidian 绝对路径
    返回: 相对于源文件的链接路径
    """
    target = target_abs
    if target.startswith("[[") and target.endswith("]]"):
        target = target[2:-2]
    if "|" in target:
        target = target.split("|")[0]
    target = target.strip()
    if not target:
        return None

    # 去掉 Obsidian 根前缀
    prefix = "02_Learn/08_book-wikis/红楼梦/"
    if target.startswith(prefix):
        target_rel = target[len(prefix):]
    else:
        # 检查是否是相对路径
        if not target.startswith("/"):
            return target
        # 其他外部链接，不转换
        return None

    # 计算相对路径
    source_dir = os.path.dirname(source_rel)
    if not source_dir:
        source_dir = "."

    rel = os.path.relpath(target_rel, source_dir)
    # 确保使用正斜杠
    rel = rel.replace("\\", "/")
    return rel


def convert_wikilink_in_file(content, source_rel):
    """转换文件中的所有 wikilinks 和 Obsidian 图片嵌入。"""

    # 1. 转换图片嵌入: ![[path|size]] → ![alt](path)
    def replace_image(match):
        full = match.group(1)
        parts = full.split("|", 1)
        img_path = parts[0].strip()

        # 转换图片路径
        prefix = "02_Learn/08_book-wikis/红楼梦/"
        if img_path.startswith(prefix):
            img_path = img_path[len(prefix):]

        # 计算相对路径
        source_dir = os.path.dirname(source_rel)
        if not source_dir:
            source_dir = "."
        rel = os.path.relpath(img_path, source_dir).replace("\\", "/")

        # 从 path 中提取文件名作为 alt text
        alt = os.path.basename(img_path).replace(".png", "").replace(".jpg", "").replace(".svg", "")
        return f"![{alt}]({rel})"

    content = re.sub(r'!\[\[(.+?)\]\]', replace_image, content)

    # 2. 转换 wikilinks: [[path|label]] → [label](path)
    # 需要处理表格中的转义: ［［path\|label］］
    def replace_wikilink(match):
        full = match.group(1)
        if "|" in full:
            path, label = full.split("|", 1)
        else:
            path = full
            label = None

        path = path.strip()
        if not path:
            return match.group(0)

        # 转换路径
        rel = wiki_to_relative_path(source_rel, path)
        if rel is None:
            # 无法转换，去掉链接保留纯文本
            if label:
                return label
            # 从路径提取文件名
            fname = path.split("/")[-1]
            if fname.endswith(".md"):
                fname = fname[:-3]
            return fname

        # 确保 markdown 链接用 .md 后缀
        if not rel.endswith(".md"):
            rel += ".md"

        # 提取 label
        if label is None or label.strip() == "":
            # 无 label，从路径提取
            fname = os.path.basename(path)
            if fname.endswith(".md"):
                fname = fname[:-3]
            label = fname
        else:
            label = label.strip()

        return f"[{label}]({rel})"

    content = re.sub(r'\[\[(.+?)\]\]', replace_wikilink, content)

    # 3. 处理表格中转义的 wikilinks: ［［path\|label］］
    # (Unicode brackets from earlier escaping)
    content = content.replace("［［", "[[").replace("］］", "]]")
    content = re.sub(r'\\\|', '|ESCAPED_PIPE|', content)  # 临时保护表格中的 |
    # 重新转换（如果有剩余）
    content = re.sub(r'\[\[(.+?)\]\]', replace_wikilink, content)
    content = content.replace('|ESCAPED_PIPE|', '|')

    # 4. 转换 Obsidian block anchors 为 HTML 锚点
    # ^hlm-001-zhen-shiyin-meng → <a id="hlm-001-zhen-shiyin-meng"></a>
    # 网页上不可见，但深链接仍然可以跳过去
    content = re.sub(r'\s*\^([a-zA-Z0-9\u4e00-\u9fff-]+)(?:\s|$)',
                     r' <a id="\1"></a> ', content)

    # 5. 修复 wikilink 转换后锚点链接的问题：
    #    - 去掉 .md# 后面的多余 .md 后缀
    #    - 去掉 #^ 中的 ^ 符号
    content = re.sub(r'\.md#\^([a-zA-Z0-9\u4e00-\u9fff-]+)\.md',
                     r'#\1', content)
    content = re.sub(r'#\^([a-zA-Z0-9\u4e00-\u9fff-]+)\.md',
                     r'#\1', content)
    content = re.sub(r'#\^([a-zA-Z0-9\u4e00-\u9fff-]+)',
                     r'#\1', content)

    return content


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico"}

def copy_and_convert(src_root, dst_root):
    """复制文件并转换 wikilinks。"""
    converted_files = []

    for root, dirs, files in os.walk(src_root):
        # 过滤
        dirs[:] = [d for d in dirs if d not in SKIP and not d.startswith(".")]

        for fname in files:
            if fname in SKIP:
                continue

            src = os.path.join(root, fname)
            src_rel = os.path.relpath(src, src_root)
            dst = os.path.join(dst_root, src_rel)

            os.makedirs(os.path.dirname(dst), exist_ok=True)

            # 图片等静态资源直接复制，不转换
            if os.path.splitext(fname)[1].lower() in IMAGE_EXTENSIONS:
                with open(src, "rb") as f_in, open(dst, "wb") as f_out:
                    f_out.write(f_in.read())
                converted_files.append(src_rel)
                continue

            if not fname.endswith(".md"):
                continue

            with open(src, "r", encoding="utf-8") as f:
                content = f.read()

            content = convert_wikilink_in_file(content, src_rel)

            with open(dst, "w", encoding="utf-8") as f:
                f.write(content)

            converted_files.append(src_rel)

    return converted_files


def make_title(name):
    """从文件名或目录名生成中文标题。"""
    if name in DIR_NAMES:
        return DIR_NAMES[name]
    title = name.replace(".md", "")
    return title


def generate_nav(docs_root):
    """从目录结构生成 MkDocs nav 配置。"""
    nav = []

    # 顶层文件
    for fname in TOP_FILES:
        fpath = f"{fname}.md"
        full = os.path.join(docs_root, fpath)
        if os.path.exists(full):
            nav.append({make_title(fname): fpath})

    # 目录
    for dname in sorted(os.listdir(docs_root)):
        dpath = os.path.join(docs_root, dname)
        if not os.path.isdir(dpath) or dname.startswith("."):
            continue

        subdir_nav = build_subdir_nav(dname, dpath, docs_root)
        if subdir_nav:
            nav.append({make_title(dname): subdir_nav})

    return nav


def build_subdir_nav(dirname, dirpath, docs_root):
    """构建子目录的 nav 条目。"""
    entries = []

    # 先处理直接在该目录下的 .md 文件
    md_files = sorted([f for f in os.listdir(dirpath) if f.endswith(".md") and f not in SKIP])
    for fname in md_files:
        rel = os.path.relpath(os.path.join(dirpath, fname), docs_root)
        entries.append({make_title(fname): rel})

    # 再处理子目录
    for subname in sorted(os.listdir(dirpath)):
        subpath = os.path.join(dirpath, subname)
        if not os.path.isdir(subpath) or subname.startswith("."):
            continue

        sub_entries = build_subdir_nav(subname, subpath, docs_root)
        if sub_entries:
            entries.append({make_title(subname): sub_entries})

    return entries


def write_mkdocs_config(nav, dst_dir, docs_root):
    """写入 mkdocs.yml 配置文件。"""
    config = {
        "site_name": "红楼梦 Wiki",
        "site_description": "红楼梦 Obsidian Wiki — 120 回章节导读、105 个人物、52 个红学专题",
        "site_author": "红楼梦 Wiki 团队",
        "repo_url": "https://github.com/franksong2702/hongloumeng-wiki",
        "repo_name": "franksong2702/hongloumeng-wiki",
        # 使用相对路径，确保在 CI 和本地都可用
        "docs_dir": ".",
        "site_dir": "../_site",

        "theme": {
            "name": "material",
            "language": "zh",
            "features": [
                "navigation.sections",
                "navigation.expand",
                "navigation.top",
                "navigation.tracking",
                "search.highlight",
                "search.share",
                "search.suggest",
                "content.tabs.link",
                "content.code.copy",
            ],
            "palette": [
                {
                    "media": "(prefers-color-scheme: light)",
                    "scheme": "default",
                    "toggle": {"icon": "material/brightness-7", "name": "切换到暗色模式"},
                },
                {
                    "media": "(prefers-color-scheme: dark)",
                    "scheme": "slate",
                    "toggle": {"icon": "material/brightness-4", "name": "切换到亮色模式"},
                },
            ],
            "icon": {
                "repo": "fontawesome/brands/github",
            },
        },

        "nav": nav,

        "markdown_extensions": [
            "tables",
            "fenced_code",
            "attr_list",
            "md_in_html",
            "def_list",
            "footnotes",
            {"toc": {"permalink": True}},
        ],

        "plugins": [
            {"search": {
                "lang": ["zh"],
                "separator": r"[\s\-,:!=\[\]()\"'/]+",
            }},
        ],

        "extra": {
            "social": [
                {
                    "icon": "fontawesome/brands/github",
                    "link": "https://github.com/franksong2702/hongloumeng-wiki",
                    "name": "GitHub 仓库",
                },
            ],
        },
    }

    yml_path = os.path.join(docs_root, "mkdocs.yml")
    with open(yml_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)

    return yml_path


def main():
    if len(sys.argv) > 1:
        wiki_root = sys.argv[1]
    else:
        wiki_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    build_dir = os.path.join(wiki_root, "_mkdocs_build")
    docs_dir = os.path.join(build_dir, "docs")

    # 清理旧构建
    if os.path.exists(build_dir):
        import shutil
        shutil.rmtree(build_dir)

    print(f"源目录: {wiki_root}")
    print(f"构建目录: {build_dir}")

    # 1. 复制并转换
    print("正在转换文件...")
    files = copy_and_convert(wiki_root, docs_dir)
    print(f"转换了 {len(files)} 个文件")

    # 2. 生成 nav
    print("正在生成导航...")
    nav = generate_nav(docs_dir)

    # 3. 写入配置
    print("正在写入 mkdocs.yml...")
    write_mkdocs_config(nav, build_dir, docs_dir)

    print(f"完成！构建目录: {build_dir}")
    print(f"运行: mkdocs build -f {os.path.join(docs_dir, 'mkdocs.yml')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
