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

from collections import defaultdict
import html
import os
import posixpath
import re
import sys

import yaml

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

# 顶层文件。README 与 index 同时存在时，MkDocs 会将前者排除；静态站只保留 index。
TOP_FILES = ["START_HERE", "SCHEMA", "ROADMAP", "log", "index"]

VAULT_LINK_PREFIX = "02_Learn/08_book-wikis/红楼梦/"

# 不是读者站内容的目录或文件。raw/ 是原始材料层，维护文档是仓库治理层；二者不应进入
# 公开阅读导航，也不应让 MkDocs 的 nav 检查产生噪声。
SKIP_DIRS = {".obsidian", ".git", "_mkdocs_build", "raw", "templates"}
SKIP_FILES = {
    "AGENTS.md",
    "README.md",
    "MAINTENANCE.md",
    "PHASE_3A_CONTENT_REVIEW.md",
    "PHASE_4A_CROSS_REFERENCE_ARCHITECTURE.md",
    "WIKI_MAINTENANCE_REVIEW.md",
}
SKIP = SKIP_DIRS | SKIP_FILES

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico"}
ROOT_PATH_NAMES = set(DIR_NAMES) | {"images"}


def should_skip_dir(dirname):
    """判断目录是否不应被复制进静态站。"""
    return dirname.startswith(".") or dirname in SKIP_DIRS


def should_skip_file(filename):
    """判断文件是否不应被复制进静态站。"""
    return filename in SKIP_FILES


def collect_source_files(src_root):
    """收集会被复制到 docs/ 的 Markdown 和静态资源相对路径。"""
    files = set()
    for root, dirs, filenames in os.walk(src_root):
        dirs[:] = [dirname for dirname in dirs if not should_skip_dir(dirname)]
        for filename in filenames:
            if should_skip_file(filename):
                continue
            suffix = os.path.splitext(filename)[1].lower()
            if filename.endswith(".md") or suffix in IMAGE_EXTENSIONS:
                source = os.path.join(root, filename)
                files.add(os.path.relpath(source, src_root).replace("\\", "/"))
    return files


def build_page_index(src_root, source_files):
    """为短 wikilink 建立唯一文件名/标题索引，歧义链接交给同目录解析。"""
    candidates = defaultdict(set)
    title_pattern = re.compile(r"^title:\s*[\"']?(.+?)[\"']?\s*$", re.MULTILINE)

    for relative_path in source_files:
        if not relative_path.endswith(".md"):
            continue
        stem = posixpath.splitext(posixpath.basename(relative_path))[0]
        candidates[stem].add(relative_path)

        source_path = os.path.join(src_root, relative_path)
        with open(source_path, "r", encoding="utf-8") as file:
            header = file.read(4096)
        match = title_pattern.search(header)
        if match:
            candidates[match.group(1).strip()].add(relative_path)

    return {
        name: next(iter(paths))
        for name, paths in candidates.items()
        if len(paths) == 1
    }


def collect_heading_anchor_aliases(src_root, source_files, page_index):
    """收集 source 中指向 Markdown 标题的锚点，供静态副本补充兼容 id。"""
    aliases = defaultdict(set)
    wikilink_pattern = re.compile(r"(?<!!)\[\[(.+?)\]\]")

    for source_rel in source_files:
        if not source_rel.endswith(".md"):
            continue
        source_path = os.path.join(src_root, source_rel)
        with open(source_path, "r", encoding="utf-8") as file:
            content = file.read()

        for match in wikilink_pattern.finditer(content):
            target, _ = split_wikilink_parts(match.group(1))
            if "#" not in target:
                continue
            _, fragment = target.split("#", 1)
            fragment = fragment.strip()
            if not fragment or fragment.startswith("^") or re.fullmatch(r"L\d+", fragment):
                continue

            resolved_url = resolve_wiki_target(source_rel, target, source_files, page_index)
            if not resolved_url:
                continue
            relative_target = resolved_url.split("#", 1)[0]
            source_dir = posixpath.dirname(source_rel) or "."
            target_rel = posixpath.normpath(posixpath.join(source_dir, relative_target))
            if target_rel in source_files:
                aliases[target_rel].add(fragment)

    return aliases


def split_target_and_fragment(target):
    """将 wikilink 目标分成路径和锚点，并将 Obsidian block anchor 转为网页锚点。"""
    if "#" not in target:
        return target, ""
    path, fragment = target.split("#", 1)
    return path, fragment.lstrip("^")


def add_markdown_extension(candidate, source_files):
    """Obsidian 允许省略 .md；只在确有对应页面时补上，绝不改图片扩展名。"""
    if candidate in source_files:
        return candidate
    if not posixpath.splitext(candidate)[1] and f"{candidate}.md" in source_files:
        return f"{candidate}.md"
    return None


def resolve_wiki_target(source_rel, target, source_files, page_index):
    """把 Obsidian 目标解析为 docs/ 中存在的文件，并生成相对 Markdown URL。"""
    target = target.strip()
    if not target or target.startswith(("http://", "https://", "mailto:")):
        return None

    path_part, fragment = split_target_and_fragment(target)
    path_part = path_part.strip().replace("\\", "/")
    if not path_part:
        return f"#{fragment}" if fragment else None

    if path_part.startswith(VAULT_LINK_PREFIX):
        candidates = [path_part[len(VAULT_LINK_PREFIX):]]
    elif path_part.startswith("/"):
        candidates = [path_part.lstrip("/")]
    else:
        source_dir = posixpath.dirname(source_rel) or "."
        normalised = posixpath.normpath(path_part)
        first_component = normalised.split("/", 1)[0]
        candidates = []
        if first_component in ROOT_PATH_NAMES:
            candidates.append(normalised)
        candidates.append(posixpath.normpath(posixpath.join(source_dir, normalised)))
        candidates.append(normalised)
        if "/" not in normalised and not posixpath.splitext(normalised)[1]:
            indexed_path = page_index.get(normalised)
            if indexed_path:
                candidates.append(indexed_path)

    target_rel = None
    for candidate in candidates:
        candidate = posixpath.normpath(candidate)
        if candidate.startswith("../"):
            continue
        target_rel = add_markdown_extension(candidate, source_files)
        if target_rel:
            break

    if not target_rel:
        return None

    source_dir = posixpath.dirname(source_rel) or "."
    relative_url = posixpath.relpath(target_rel, source_dir)
    # #L33 是历史行号坐标而非可发布锚点；保留到对应原文页的链接，而不制造一个必坏锚点。
    if re.fullmatch(r"L\d+", fragment):
        return relative_url
    if fragment:
        return f"{relative_url}#{fragment}"
    return relative_url


def split_wikilink_parts(full):
    """解析普通或表格转义的 alias 分隔符。"""
    if r"\|" in full:
        return full.split(r"\|", 1)
    if "|" in full:
        return full.split("|", 1)
    return full, None


def link_label(path, label):
    """为未显式指定 alias 的 wikilink 生成可读文字。"""
    if label and label.strip():
        return label.strip()
    path_part, fragment = split_target_and_fragment(path)
    if not path_part:
        return fragment
    return posixpath.splitext(posixpath.basename(path_part.strip()))[0]


def convert_wikilink_in_file(content, source_rel, source_files, page_index, heading_aliases):
    """转换文件中的 wikilinks、图片嵌入和 Obsidian block anchors。"""
    # 历史表格中曾使用全角方括号避免列分隔冲突，先恢复再统一转换。
    content = content.replace("［［", "[[").replace("］］", "]]")

    # 1. 转换图片嵌入: ![[path|size]] → ![alt](relative-path)
    def replace_image(match):
        img_path, _ = split_wikilink_parts(match.group(1))
        rel = resolve_wiki_target(source_rel, img_path, source_files, page_index)
        if not rel:
            return match.group(0)
        alt = posixpath.splitext(posixpath.basename(img_path.split("#", 1)[0].strip()))[0]
        return f"![{alt}]({rel})"

    content = re.sub(r'!\[\[(.+?)\]\]', replace_image, content)

    # 2. 转换 wikilinks: [[path|label]] → [label](relative-path)
    def replace_wikilink(match):
        path, label = split_wikilink_parts(match.group(1))
        path = path.strip()
        if not path:
            return match.group(0)
        rel = resolve_wiki_target(source_rel, path, source_files, page_index)
        if rel is None:
            # 不生成一个已知会坏的 Markdown 链接；原始 Wiki 的健康检查仍负责报告内容层问题。
            return link_label(path, label)
        return f"[{link_label(path, label)}]({rel})"

    content = re.sub(r'\[\[(.+?)\]\]', replace_wikilink, content)

    # 3. 转换 Obsidian block anchors 为 HTML 锚点（网页上不可见，但深链接可跳转）。
    content = re.sub(
        r'\s*\^([a-zA-Z0-9\u4e00-\u9fff-]+)(?:\s|$)',
        r' <a id="\1"></a> ',
        content,
    )

    # MkDocs 对非拉丁标题会生成 _1 之类的 id；为源文件实际引用过的标题补一个稳定别名。
    for anchor in sorted(heading_aliases.get(source_rel, set())):
        heading_pattern = re.compile(
            rf"^(#{{1,6}}\s+{re.escape(anchor)}\s*#*\s*)$",
            re.MULTILINE,
        )
        safe_anchor = html.escape(anchor, quote=True)
        content = heading_pattern.sub(rf'<a id="{safe_anchor}"></a>\n\1', content)

    return content

def copy_and_convert(src_root, dst_root):
    """复制文件并转换 wikilinks。"""
    converted_files = []
    source_files = collect_source_files(src_root)
    page_index = build_page_index(src_root, source_files)
    heading_aliases = collect_heading_anchor_aliases(src_root, source_files, page_index)

    for root, dirs, files in os.walk(src_root):
        # 过滤
        dirs[:] = [dirname for dirname in dirs if not should_skip_dir(dirname)]

        for fname in files:
            if should_skip_file(fname):
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

            content = convert_wikilink_in_file(
                content,
                src_rel,
                source_files,
                page_index,
                heading_aliases,
            )

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
            "admonition",
            "pymdownx.details",
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
