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

from collections import Counter, defaultdict
import html
import os
import posixpath
import re
import sys
from pathlib import Path

import yaml


class PythonName:
    """让 PyYAML 输出 MkDocs 所需的 ``!!python/name`` 可调用对象标签。"""

    def __init__(self, name):
        self.name = name


class MkdocsDumper(yaml.Dumper):
    """专用于写出 MkDocs 配置的 YAML dumper。"""


def represent_python_name(dumper, data):
    return dumper.represent_scalar(
        f"tag:yaml.org,2002:python/name:{data.name}",
        "",
    )


MkdocsDumper.add_representer(PythonName, represent_python_name)

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
STATIC_EXTENSIONS = IMAGE_EXTENSIONS | {".css", ".js"}
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
            if filename.endswith(".md") or suffix in STATIC_EXTENSIONS:
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
            if os.path.splitext(fname)[1].lower() in STATIC_EXTENSIONS:
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


def require_nav_page(title, relative_path, docs_root):
    """返回一个必需页面的 nav 项；缺页时在构建阶段明确失败。"""
    if not os.path.isfile(os.path.join(docs_root, relative_path)):
        raise RuntimeError(f"导航必需页面不存在: {relative_path}")
    return {title: relative_path}


def build_subdir_nav(dirname, dirpath, docs_root, excluded_paths=None):
    """构建完整目录的 nav 条目，并允许已在上层突出的页面不重复出现。"""
    excluded_paths = excluded_paths or set()
    entries = []

    # 先处理直接在该目录下的 .md 文件
    md_files = sorted([f for f in os.listdir(dirpath) if f.endswith(".md") and f not in SKIP])
    for fname in md_files:
        rel = os.path.relpath(os.path.join(dirpath, fname), docs_root)
        if rel in excluded_paths:
            continue
        entries.append({make_title(fname): rel})

    # 再处理子目录
    for subname in sorted(os.listdir(dirpath)):
        subpath = os.path.join(dirpath, subname)
        if not os.path.isdir(subpath) or subname.startswith("."):
            continue

        sub_entries = build_subdir_nav(subname, subpath, docs_root, excluded_paths)
        if sub_entries:
            entries.append({make_title(subname): sub_entries})

    return entries


def directory_nav(title, relative_dir, docs_root, excluded_paths=None):
    """把一个完整目录收进可折叠的二级导航。"""
    directory = os.path.join(docs_root, relative_dir)
    entries = build_subdir_nav(relative_dir, directory, docs_root, excluded_paths)
    if not entries:
        raise RuntimeError(f"导航目录为空或不存在: {relative_dir}")
    return {title: entries}


def flatten_nav_paths(nav):
    """提取 nav 中的全部 Markdown 路径，用于防止导航重构时漏页或重复页。"""
    paths = []

    def visit(node):
        if isinstance(node, str):
            paths.append(node)
        elif isinstance(node, list):
            for child in node:
                visit(child)
        elif isinstance(node, dict):
            for child in node.values():
                visit(child)

    visit(nav)
    return paths


def validate_nav_entries(nav, docs_root):
    """要求读者导航中的入口页存在且不重复；长尾文章改由索引与搜索进入。"""
    expected = {
        os.path.relpath(path, docs_root).replace("\\", "/")
        for path in Path(docs_root).rglob("*.md")
    }
    actual_paths = flatten_nav_paths(nav)
    actual = set(actual_paths)
    duplicated = sorted(path for path, count in Counter(actual_paths).items() if count > 1)
    unknown = sorted(actual - expected)
    if duplicated or unknown:
        raise RuntimeError(
            "导航入口无效: "
            f"duplicated={duplicated}, unknown={unknown}"
        )


def generate_nav(docs_root):
    """生成以读者任务组织、但不遗漏任何页面的六区导航。"""
    featured_outputs = {
        "outputs/红楼梦速读指南.md",
        "outputs/红楼梦阅读路线.md",
        "outputs/红楼梦研究型阅读路线.md",
        "outputs/红楼梦人物手册.md",
        "outputs/金陵十二钗研究手册.md",
        "outputs/红楼梦主题导读.md",
        "outputs/红学争议导览.md",
        "outputs/大观园空间阅读手册.md",
        "outputs/人物关系阅读指南.md",
    }
    nav = [
        {
            "开始阅读": [
                require_nav_page("首页", "index.md", docs_root),
                require_nav_page("完整阅读入口", "START_HERE.md", docs_root),
                require_nav_page("速读指南", "outputs/红楼梦速读指南.md", docs_root),
                require_nav_page("分阶段阅读路线", "outputs/红楼梦阅读路线.md", docs_root),
                require_nav_page("研究型阅读路线", "outputs/红楼梦研究型阅读路线.md", docs_root),
            ]
        },
        {
            "人物与情节": [
                require_nav_page("人物索引", "queries/人物索引.md", docs_root),
                require_nav_page("事件索引", "queries/事件索引.md", docs_root),
                require_nav_page("人物关系阅读指南", "outputs/人物关系阅读指南.md", docs_root),
                require_nav_page("人物手册", "outputs/红楼梦人物手册.md", docs_root),
                require_nav_page("金陵十二钗手册", "outputs/金陵十二钗研究手册.md", docs_root),
                require_nav_page("人物关系图", "maps/人物关系图.md", docs_root),
            ]
        },
        {
            "主题与研究": [
                require_nav_page("主题导读", "outputs/红楼梦主题导读.md", docs_root),
                require_nav_page("红学争议导览", "outputs/红学争议导览.md", docs_root),
                require_nav_page("概念索引", "queries/概念索引.md", docs_root),
                require_nav_page("诗词索引", "queries/诗词索引.md", docs_root),
                require_nav_page("红学大家索引", "redology/红学大家索引.md", docs_root),
                directory_nav("意象", "motifs-symbols", docs_root),
                directory_nav("历史与制度背景", "background", docs_root),
                directory_nav("更多阅读产品", "outputs", docs_root, featured_outputs),
            ]
        },
        {
            "空间、家族与时间": [
                require_nav_page("大观园空间阅读手册", "outputs/大观园空间阅读手册.md", docs_root),
                directory_nav("图谱", "maps", docs_root, {"maps/人物关系图.md"}),
                require_nav_page("地点索引", "queries/地点索引.md", docs_root),
                directory_nav("家族", "families", docs_root),
                directory_nav("时间线", "timelines", docs_root),
            ]
        },
        {
            "章节与原文": [
                require_nav_page("回目索引", "queries/回目索引.md", docs_root),
                require_nav_page("简体原文索引", "queries/简体原文索引.md", docs_root),
                require_nav_page("繁体原文索引", "queries/繁体原文索引.md", docs_root),
                require_nav_page("原文锚点索引", "queries/原文锚点索引.md", docs_root),
            ]
        },
        {
            "查阅与关于": [
                require_nav_page("当前状态", "WIKI_STATUS.md", docs_root),
                require_nav_page("研究路线图", "ROADMAP.md", docs_root),
                require_nav_page("Wiki Schema", "SCHEMA.md", docs_root),
                require_nav_page("更新日志", "log.md", docs_root),
            ]
        },
    ]
    validate_nav_entries(nav, docs_root)
    return nav


def write_mkdocs_config(nav, dst_dir, docs_root):
    """写入 mkdocs.yml 配置文件。"""
    config = {
        "site_name": "红楼梦 Wiki",
        "site_description": "红楼梦人物、事件、空间、原文与红学研究的交叉阅读站",
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
                "navigation.tabs",
                "navigation.tabs.sticky",
                "navigation.sections",
                "navigation.path",
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
        "extra_css": ["stylesheets/reader.css"],
        "extra_javascript": [
            "https://cdn.jsdelivr.net/npm/mermaid@11.12.2/dist/mermaid.min.js",
            "javascripts/mermaid-init.js",
        ],
        # 长尾文章通过分类索引和全文搜索进入，避免把 700+ 条目塞进左侧导航。
        # not_in_nav 仅抑制“有意不入侧栏”的提示，不影响页面构建、直链或搜索收录。
        "not_in_nav": """/characters/**
/events/**
/concepts/**
/locations/**
/poetry/**
/redology/**
!/redology/红学大家索引.md
/chapters/**
/texts/**""",

        "markdown_extensions": [
            "tables",
            "fenced_code",
            "attr_list",
            "md_in_html",
            "def_list",
            "footnotes",
            "admonition",
            "pymdownx.details",
            {
                "pymdownx.superfences": {
                    "custom_fences": [
                        {
                            "name": "mermaid",
                            "class": "mermaid",
                            "format": PythonName("pymdownx.superfences.fence_code_format"),
                        }
                    ]
                }
            },
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
        yaml.dump(
            config,
            f,
            Dumper=MkdocsDumper,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        )

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
