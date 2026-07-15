#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
红楼梦 Wiki · 只读健康检查脚本

用法：
  python3 scripts/wiki_health_check.py
  python3 scripts/wiki_health_check.py --strict
  python3 scripts/wiki_health_check.py --output /tmp/hongloumeng_wiki_health_report.txt

设计原则：
  - 默认只读：扫描源文件并打印报告，不修改正文。
  - 默认 exit 0：用于 Phase 0 建立机制时稳定产出报告。
  - --strict：存在结构性问题时 exit 1，适合后续 CI / 发布前闸门。
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote


WIKI_PREFIX = "02_Learn/08_book-wikis/红楼梦/"

SKIP_DIRS = {
    ".git",
    ".github",
    ".obsidian",
    ".wiki-health",
    "__pycache__",
    "site",
    "docs",
}

RAW_DIR = "raw"

MAINTENANCE_MARKDOWN = {
    "MAINTENANCE.md",
    "PHASE_3A_CONTENT_REVIEW.md",
    "PHASE_4A_CROSS_REFERENCE_ARCHITECTURE.md",
    "WIKI_MAINTENANCE_REVIEW.md",
}

MAINTENANCE_DIRS = {
    "scripts",
}

FRONTMATTER_ROOT_SCOPE = {
    "AGENTS.md",
    "SCHEMA.md",
    "ROADMAP.md",
    "START_HERE.md",
    "index.md",
    "WIKI_STATUS.md",
}

FRONTMATTER_REQUIRED_FIELDS = [
    "title",
    "created",
    "updated",
    "type",
    "book",
    "status",
]

PLACEHOLDER_EXCLUDED_FILES = {
    "AGENTS.md",
    "SCHEMA.md",
    "ROADMAP.md",
    "log.md",
    "README.md",
    "START_HERE.md",
    "index.md",
    "MAINTENANCE.md",
    "WIKI_MAINTENANCE_REVIEW.md",
    "PHASE_4A_CROSS_REFERENCE_ARCHITECTURE.md",
}

PLACEHOLDER_EXCLUDED_DIRS = {
    RAW_DIR,
    "templates",
    "scripts",
}

PLACEHOLDER_TERMS = [
    "TODO",
    "待补",
    "暂无",
    "占位",
    "作为关键事件入口保留",
    "推动人物关系变化",
    "通过相关章节可以追踪",
    "本回未单列",
]

PLACEHOLDER_NEGATION_HINTS = [
    "占位句 0",
    "占位符 0",
    "占位词 0",
    "占位句为 0",
    "占位符为 0",
    "占位词为 0",
    "无残留问题",
]

ALIAS_MAP = {
    "宝玉": "characters/贾宝玉.md",
    "黛玉": "characters/林黛玉.md",
    "宝钗": "characters/薛宝钗.md",
    "凤姐": "characters/王熙凤.md",
    "探春": "characters/贾探春.md",
    "惜春": "characters/贾惜春.md",
    "迎春": "characters/贾迎春.md",
    "可卿": "characters/秦可卿.md",
}

THIN_THRESHOLDS = {
    "character": 25,
    "event": 25,
    "location": 25,
    "concept": 30,
    "redology": 45,
    "background": 50,
    "output": 60,
    "family": 25,
    "motif": 25,
    "poem": 30,
    "chapter": 25,
    "timeline": 15,
    "map": 10,
    "query": 10,
}

COUNT_DIRS = [
    "chapters",
    "texts/simplified",
    "texts/traditional",
    "characters",
    "events",
    "concepts",
    "locations",
    "poetry",
    "redology",
    "background",
    "maps",
    "timelines",
    "families",
    "motifs-symbols",
    "queries",
    "outputs",
    "templates",
    "raw",
]

SELF_DESCRIPTION_DOCS = [
    "README.md",
    "index.md",
    "WIKI_STATUS.md",
    "ROADMAP.md",
    "AGENTS.md",
    "outputs/红楼梦编译总评.md",
]

GOVERNANCE_SNAPSHOT_DOC = "outputs/人物事件线剩余人物审查.md"

RELEASE_LOG_DOC = "log.md"
RELEASE_LOG_PATHS = [
    "index.md",
    "START_HERE.md",
    "WIKI_STATUS.md",
    "ROADMAP.md",
    "chapters",
    "characters",
    "concepts",
    "events",
    "families",
    "locations",
    "maps",
    "motifs-symbols",
    "poetry",
    "background",
    "redology",
    "timelines",
    "queries",
    "outputs",
    "scripts/build_mkdocs.py",
    "scripts/generate_wiki_status.py",
    "scripts/external_link_check.py",
    "scripts/mkdocs_build_check.py",
    "scripts/wiki_health_check.py",
    ".github/workflows/deploy.yml",
]

RELEASE_LOG_DATE_RE = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})(?:[｜：:]|\s)")

# 这四页曾以几十个平铺回目替代空间叙事；它们是地点页的阅读体验基线。
LOCATION_READER_HUBS = {
    "locations/怡红院.md",
    "locations/潇湘馆.md",
    "locations/宁国府.md",
    "locations/栊翠庵.md",
}
LOCATION_READER_HEADINGS = (
    "## 空间定位",
    "## 谁在这里相互作用",
    "## 关键事件现场",
    "## 推荐回读",
    "## 继续阅读",
)

CORE_CHAPTER_EDITORIAL = {
    f"chapters/第{number:03d}回.md"
    for number in (1, 3, 5, 6, 13, 17, 18, 23, 27, 32, 33, 34, 40, 41, 52, 56, 63, 66, 69, 74, 77, 78, 96, 97, 98, 105, 120)
}
CORE_CHAPTER_REQUIRED_HEADINGS = ("## 本回辨识", "## 原文回读")
CORE_CHAPTER_FORBIDDEN_PHRASES = (
    "再回到“出场人物”“相关概念”核对人物关系和主题线索",
    "若时间有限，可把本回放入相邻章节连续阅读",
)

RELATIONSHIP_GUIDE_DOC = "outputs/人物关系阅读指南.md"
RELATIONSHIP_GUIDE_HEADINGS = (
    "## 一、宝黛钗：真情、婚姻与不可兼得",
    "## 二、荣国府内宅：长辈授权、管家执行与婚姻冲突",
    "## 三、女儿世界：居所、照护与主仆制度",
    "## 四、宁国府：亲属网络与败相先现",
    "## 五、府外关系：家族边界从哪里被看见",
)
RELATIONSHIP_HUBS = {
    "characters/贾宝玉.md",
    "characters/林黛玉.md",
    "characters/薛宝钗.md",
    "characters/贾母.md",
    "characters/王夫人.md",
    "characters/贾政.md",
    "characters/王熙凤.md",
    "characters/贾琏.md",
    "characters/平儿.md",
    "characters/袭人.md",
    "characters/晴雯.md",
    "characters/紫鹃.md",
    "characters/贾探春.md",
    "characters/李纨.md",
    "characters/贾珍.md",
    "characters/秦可卿.md",
    "characters/尤氏.md",
    "characters/贾蓉.md",
    "characters/薛姨妈.md",
    "characters/薛蟠.md",
}


@dataclass
class Finding:
    severity: str
    category: str
    path: str
    line: int | None
    detail: str

    def render(self) -> str:
        loc = self.path
        if self.line is not None:
            loc += f":{self.line}"
        return f"[{self.severity}] {self.category} · {loc} · {self.detail}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="红楼梦 Wiki 只读健康检查")
    parser.add_argument(
        "--root",
        default=None,
        help="Wiki 根目录；默认取脚本上级目录。",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="存在 ERROR 级发现时返回 exit 1。",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="把报告另存为指定路径；父目录会自动创建。",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="每类发现最多展示多少条样例。",
    )
    return parser.parse_args()


def default_root() -> Path:
    return Path(__file__).resolve().parents[1]


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def should_skip_dir(dirname: str) -> bool:
    return dirname in SKIP_DIRS


def all_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for current, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if not should_skip_dir(d)]
        for name in names:
            files.append(Path(current) / name)
    return files


def classify_markdown(path: Path, root: Path) -> str:
    r = rel(path, root)
    parts = Path(r).parts
    if not parts:
        return "unknown"
    if parts[0] == RAW_DIR:
        return "raw"
    if path.name in MAINTENANCE_MARKDOWN:
        return "maintenance"
    if parts[0] in MAINTENANCE_DIRS:
        return "maintenance"
    return "product"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def iter_non_code_lines(text: str) -> Iterable[tuple[int, str]]:
    in_fence = False
    for line_no, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # 去掉单行 inline code，避免示例误报。
        line = re.sub(r"`[^`\n]*`", "", line)
        yield line_no, line


def parse_frontmatter(text: str) -> tuple[dict[str, str], str | None]:
    if not text.startswith("---\n"):
        return {}, None
    end = text.find("\n---", 4)
    if end == -1:
        return {}, None
    block = text[4:end]
    fields: dict[str, str] = {}
    for raw_line in block.splitlines():
        if not raw_line.strip() or raw_line.startswith((" ", "-")):
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", raw_line)
        if m:
            fields[m.group(1)] = m.group(2).strip()
    return fields, block


def frontmatter_sources(text: str) -> list[str]:
    """读取 frontmatter 中的 inline 或多行 `sources` 列表。"""
    _, block = parse_frontmatter(text)
    if block is None:
        return []

    lines = block.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"^sources:\s*(.*)$", line)
        if not match:
            continue
        tail = match.group(1).strip()
        if tail in {"", "[]"}:
            values: list[str] = []
            if tail == "[]":
                return values
            for following in lines[index + 1 :]:
                item = re.match(r"^\s+-\s+(.+?)\s*$", following)
                if item:
                    values.append(item.group(1).strip().strip('"\''))
                    continue
                if following.startswith((" ", "\t")) or not following.strip():
                    continue
                break
            return values

        if tail.startswith("[") and tail.endswith("]"):
            inner = tail[1:-1].strip()
            if not inner:
                return []
            quoted = re.findall(r'["\']([^"\']+)["\']', inner)
            if quoted:
                return [value.strip() for value in quoted if value.strip()]
            return [value.strip() for value in inner.split(",") if value.strip()]

        return [tail.strip('"\'')]
    return []


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---", 4)
    if end == -1:
        return text
    return text[end + 4 :]


def content_line_count(text: str) -> int:
    body = strip_frontmatter(text)
    count = 0
    for _, line in iter_non_code_lines(body):
        if line.strip():
            count += 1
    return count


def build_target_indexes(root: Path, files: list[Path]) -> dict[str, object]:
    rel_files = [rel(p, root) for p in files]
    file_set = set(rel_files)
    md_files = [r for r in rel_files if r.endswith(".md")]
    md_set = set(md_files)
    md_no_ext_set = {r[:-3] for r in md_files}
    stem_map: dict[str, list[str]] = defaultdict(list)
    basename_map: dict[str, list[str]] = defaultdict(list)
    for r in rel_files:
        p = Path(r)
        basename_map[p.name].append(r)
        if r.endswith(".md"):
            stem_map[p.stem].append(r)
    return {
        "file_set": file_set,
        "md_set": md_set,
        "md_no_ext_set": md_no_ext_set,
        "stem_map": stem_map,
        "basename_map": basename_map,
    }


def infer_vault_root(root: Path) -> Path | None:
    marker = "/02_Learn/"
    s = root.as_posix()
    idx = s.find(marker)
    if idx == -1:
        return None
    return Path(s[:idx])


def normalize_wiki_target(target: str) -> str:
    target = target.strip()
    if "|" in target:
        target = target.split("|", 1)[0].strip()
    if "#" in target:
        target = target.split("#", 1)[0].strip()
    if "^" in target:
        target = target.split("^", 1)[0].strip()
    if target.startswith(WIKI_PREFIX):
        target = target[len(WIKI_PREFIX) :]
    return target.strip()


def resolve_wikilink(
    target: str,
    indexes: dict[str, object],
) -> tuple[str, str]:
    """返回 (status, detail)。status: ok / alias / ambiguous / broken / external."""

    target = normalize_wiki_target(target)
    if not target:
        return "ok", "same-file anchor"

    file_set: set[str] = indexes["file_set"]  # type: ignore[assignment]
    md_set: set[str] = indexes["md_set"]  # type: ignore[assignment]
    md_no_ext_set: set[str] = indexes["md_no_ext_set"]  # type: ignore[assignment]
    stem_map: dict[str, list[str]] = indexes["stem_map"]  # type: ignore[assignment]
    basename_map: dict[str, list[str]] = indexes["basename_map"]  # type: ignore[assignment]

    if target in ALIAS_MAP:
        canonical = ALIAS_MAP[target]
        if canonical in md_set:
            return "alias", f"{target} -> {canonical}"
        return "broken", f"alias target missing: {target} -> {canonical}"

    # 明确路径链接：按 Wiki 根目录解析。
    if "/" in target:
        candidates = [target]
        if not Path(target).suffix:
            candidates.append(target + ".md")
        if target.endswith(".md"):
            candidates.append(target[:-3])
        for candidate in candidates:
            if candidate in file_set or candidate in md_set or candidate in md_no_ext_set:
                return "ok", candidate
        if target.startswith("02_Learn/"):
            return "external", f"outside current wiki or bad vault path: {target}"
        return "broken", target

    # 无路径链接：按 Obsidian basename 解析。
    if target in stem_map:
        matches = stem_map[target]
        if len(matches) == 1:
            return "ok", matches[0]
        return "ambiguous", f"{target} -> {matches[:5]}"
    if target in basename_map:
        matches = basename_map[target]
        if len(matches) == 1:
            return "ok", matches[0]
        return "ambiguous", f"{target} -> {matches[:5]}"

    return "broken", target


def check_wikilinks(
    root: Path,
    product_md: list[Path],
    indexes: dict[str, object],
) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    stats = Counter()
    wikilink_re = re.compile(r"(!?)\[\[([^\]]+)\]\]")

    for path in product_md:
        r = rel(path, root)
        text = read_text(path)
        for line_no, line in iter_non_code_lines(text):
            for match in wikilink_re.finditer(line):
                stats["scanned"] += 1
                raw_target = match.group(2)
                status, detail = resolve_wikilink(raw_target, indexes)
                stats[status] += 1
                if status == "broken":
                    findings.append(Finding("ERROR", "wikilink_broken", r, line_no, f"[[{raw_target}]] -> {detail}"))
                elif status == "ambiguous":
                    findings.append(Finding("ERROR", "wikilink_ambiguous", r, line_no, f"[[{raw_target}]] -> {detail}"))
                elif status == "alias":
                    findings.append(Finding("WARN", "wikilink_alias_should_be_canonical", r, line_no, detail))
                elif status == "external":
                    findings.append(Finding("WARN", "wikilink_external_or_bad_vault_path", r, line_no, detail))
    return findings, dict(stats)


def check_table_alias_wikilinks(root: Path, scan_md: list[Path]) -> tuple[list[Finding], dict[str, int]]:
    """禁止在 Markdown 表格行里使用带 alias 的 Obsidian wikilink。

    `[[path|alias]]` 本身是合法 Obsidian 链接，但 Markdown 表格也用 `|` 分列；
    把二者叠在一起时，Obsidian/Markdown 渲染可能把链接切碎，造成看似断链或点击异常。
    需要 alias 链接时，优先改用编号列表或项目列表。
    """
    findings: list[Finding] = []
    stats = Counter()
    alias_wikilink_re = re.compile(r"\[\[[^\]]+\|[^\]]+\]\]")

    for path in scan_md:
        r = rel(path, root)
        text = read_text(path)
        for line_no, line in iter_non_code_lines(text):
            stripped = line.lstrip()
            if not stripped.startswith("|"):
                continue
            if stripped.count("|") < 2:
                continue
            stats["table_rows_scanned"] += 1
            matches = alias_wikilink_re.findall(line)
            if not matches:
                continue
            stats["alias_wikilinks_in_tables"] += len(matches)
            findings.append(
                Finding(
                    "ERROR",
                    "table_alias_wikilink",
                    r,
                    line_no,
                    "Markdown 表格行内不要使用带 |alias 的 wikilink；改用列表或去掉 alias: "
                    + "; ".join(matches[:3]),
                )
            )
    return findings, dict(stats)


def clean_markdown_link_target(target: str) -> str:
    target = target.strip()
    # 去掉可选 title：path "title"
    target = re.sub(r'\s+"[^"]*"\s*$', "", target)
    target = re.sub(r"\s+'[^']*'\s*$", "", target)
    target = unquote(target)
    if "#" in target:
        target = target.split("#", 1)[0]
    if "?" in target:
        target = target.split("?", 1)[0]
    return target.strip()


def check_markdown_links(root: Path, product_md: list[Path]) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    stats = Counter()
    vault_root = infer_vault_root(root)
    md_link_re = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    external_schemes = ("http://", "https://", "mailto:", "tel:", "obsidian://")

    for path in product_md:
        r = rel(path, root)
        text = read_text(path)
        for line_no, line in iter_non_code_lines(text):
            for match in md_link_re.finditer(line):
                raw_target = match.group(1)
                target = clean_markdown_link_target(raw_target)
                if not target or target.startswith("#"):
                    continue
                if target.startswith(external_schemes):
                    stats["external"] += 1
                    continue
                # 本检查只处理本地 Markdown 链接；图片/附件交给 wikilink 或站点构建脚本。
                if not target.endswith(".md"):
                    stats["non_markdown_skipped"] += 1
                    continue

                stats["scanned"] += 1
                if target.startswith("/"):
                    candidate = root / target.lstrip("/")
                else:
                    candidate = path.parent / target

                if candidate.exists():
                    stats["ok"] += 1
                    continue

                # 常见错误：在 Wiki 根目录内把 vault path 当相对路径写。
                suggestion = ""
                if target.startswith(WIKI_PREFIX):
                    stripped = target[len(WIKI_PREFIX) :]
                    stripped_candidate = root / stripped
                    if stripped_candidate.exists():
                        suggestion = f"；疑似应改为 {os.path.relpath(stripped_candidate, path.parent).replace(os.sep, '/')}"
                elif vault_root and target.startswith("02_Learn/"):
                    vault_candidate = vault_root / target
                    if vault_candidate.exists():
                        suggestion = "；目标存在于 vault 内，但不是从当前文件出发的有效相对链接"

                stats["broken"] += 1
                findings.append(
                    Finding(
                        "ERROR",
                        "markdown_link_broken",
                        r,
                        line_no,
                        f"[... ]({raw_target}) -> {target} 不存在{suggestion}",
                    )
                )
    return findings, dict(stats)


def check_frontmatter_sources(root: Path, product_md: list[Path]) -> tuple[list[Finding], dict[str, int]]:
    """校验 `sources:` 中可识别的本地路径，并约束繁体原文的公开来源。

    外部 URL 的可访问性由 `external_link_check.py` 负责；这里仅保证本地路径
    在当前 Vault 中真实存在，并防止发布用繁体原文再次指向机器私有目录。
    """
    findings: list[Finding] = []
    stats = Counter()
    vault_root = infer_vault_root(root)
    external_schemes = ("http://", "https://", "doi:")

    for path in product_md:
        text = read_text(path)
        fields, _ = parse_frontmatter(text)
        values = frontmatter_sources(text)
        if values:
            stats["pages_with_sources"] += 1

        external_values = [value for value in values if value.startswith(external_schemes)]
        if (
            fields.get("type") == "source-text"
            and fields.get("script") == "traditional"
        ):
            stats["traditional_scanned"] += 1
            if external_values:
                stats["traditional_with_external_source"] += 1
            else:
                findings.append(
                    Finding(
                        "ERROR",
                        "traditional_source_external_missing",
                        rel(path, root),
                        None,
                        "繁体发布原文必须至少保留一个可公开复核的外部来源 URL",
                    )
                )

        for value in values:
            stats["entries"] += 1
            if value.startswith(external_schemes):
                stats["external"] += 1
                continue

            clean_value = value.split("#", 1)[0].strip()
            looks_local = (
                clean_value.endswith((".md", ".pdf", ".png", ".jpg", ".jpeg", ".svg"))
                or clean_value.startswith(("02_Learn/", "raw/", "texts/", "characters/", "events/", "concepts/", "redology/", "../", "./"))
            )
            if not looks_local:
                stats["descriptive_skipped"] += 1
                continue

            if clean_value.startswith(WIKI_PREFIX):
                candidate = root / clean_value[len(WIKI_PREFIX) :]
            elif clean_value.startswith("02_Learn/") and vault_root is not None:
                candidate = vault_root / clean_value
            elif clean_value.startswith(("../", "./")):
                candidate = path.parent / clean_value
            else:
                candidate = root / clean_value

            if candidate.exists():
                stats["local_ok"] += 1
                continue

            stats["local_broken"] += 1
            findings.append(
                Finding(
                    "ERROR",
                    "frontmatter_source_local_missing",
                    rel(path, root),
                    None,
                    f"sources 本地路径不存在: {value}",
                )
            )

    return findings, dict(stats)


def chapter_number_from_path(path: Path) -> str | None:
    m = re.search(r"第(\d{3})回\.md$", path.name)
    if not m:
        return None
    return m.group(1)


def chapter_numbers_in_text(text: str) -> set[str]:
    return set(re.findall(r"第(\d{3})回", text))


def resolve_event_target(raw_target: str, indexes: dict[str, object]) -> str | None:
    status, detail = resolve_wikilink(raw_target, indexes)
    if status != "ok":
        return None
    if detail.startswith("events/") and detail.endswith(".md"):
        return detail
    return None


def check_chapter_key_event_links(
    root: Path,
    product_md: list[Path],
    indexes: dict[str, object],
) -> tuple[list[Finding], dict[str, int]]:
    """检查章节页“关键事件”里的事件链接是否落在事件页声明的相关回目内。

    这不是文学语义判断，只做一个低误报的定位一致性检查：
    - 扫描 chapters/第xxx回.md 的 ## 关键事件 区块；
    - 找出指向 events/*.md 的 wikilink；
    - 反查事件页正文是否出现相同“第xxx回”标记。

    若未来确有跨回过程型事件，应在事件页“相关回目/相关章节/原文锚点”
    中显式标出对应回目，而不是让章节页链接到一个没有定位说明的事件页。
    """

    findings: list[Finding] = []
    stats = Counter()
    wikilink_re = re.compile(r"\[\[([^\]]+)\]\]")
    event_chapter_cache: dict[str, set[str]] = {}

    chapter_paths = [
        p
        for p in product_md
        if rel(p, root).startswith("chapters/") and chapter_number_from_path(p) is not None
    ]

    for path in chapter_paths:
        chapter_no = chapter_number_from_path(path)
        if chapter_no is None:
            continue
        r = rel(path, root)
        text = read_text(path)
        in_key_events = False

        for line_no, line in iter_non_code_lines(text):
            if line.startswith("## "):
                in_key_events = line.strip() == "## 关键事件"
                continue
            if not in_key_events:
                continue
            if not line.strip().startswith("- "):
                continue

            for match in wikilink_re.finditer(line):
                raw_target = match.group(1)
                event_rel = resolve_event_target(raw_target, indexes)
                if event_rel is None:
                    stats["non_event_or_unresolved_skipped"] += 1
                    continue

                stats["scanned"] += 1
                if event_rel not in event_chapter_cache:
                    event_path = root / event_rel
                    if event_path.exists():
                        event_chapter_cache[event_rel] = chapter_numbers_in_text(read_text(event_path))
                    else:
                        event_chapter_cache[event_rel] = set()

                event_chapters = event_chapter_cache[event_rel]
                if chapter_no in event_chapters:
                    stats["ok"] += 1
                    continue

                stats["suspect"] += 1
                chapter_label = f"第{chapter_no}回"
                event_labels = ", ".join(f"第{n}回" for n in sorted(event_chapters)) or "未声明相关回目"
                findings.append(
                    Finding(
                        "WARN",
                        "chapter_key_event_link_unlocalized",
                        r,
                        line_no,
                        f"{chapter_label} 关键事件链接到 {event_rel}，但事件页定位为 {event_labels}；请补事件页相关回目或移除误链",
                    )
                )

    for key in ("scanned", "ok", "suspect", "non_event_or_unresolved_skipped"):
        stats.setdefault(key, 0)
    return findings, dict(stats)


def source_text_anchor_spans(lines: list[str]) -> tuple[int, int | None, int | None]:
    """返回 source-text 页中 frontmatter 结束行和阅读提示区间。

    简体原文页顶部常有 `??? note "📖 阅读提示"` 区块；block anchor 必须落在
    小说正文段落中，不能落在 frontmatter 或阅读提示里，否则从事件页跳转时
    会把读者带到 meta 信息，而不是正文现场。
    """

    frontmatter_end = 0
    if lines and lines[0] == "---":
        for line_no, line in enumerate(lines[1:], 2):
            if line == "---":
                frontmatter_end = line_no
                break

    hint_start: int | None = None
    hint_end: int | None = None
    for line_no, line in enumerate(lines, 1):
        if line_no <= frontmatter_end:
            continue
        if "??? note" in line and "阅读提示" in line:
            hint_start = line_no
            hint_end = len(lines)
            for candidate in range(line_no + 1, len(lines) + 1):
                candidate_line = lines[candidate - 1]
                if candidate_line.strip() and not candidate_line.startswith((" ", "\t")):
                    hint_end = candidate - 1
                    break
            break

    return frontmatter_end, hint_start, hint_end


def source_anchor_location(
    line_no: int,
    frontmatter_end: int,
    hint_start: int | None,
    hint_end: int | None,
) -> str:
    if line_no <= frontmatter_end:
        return "frontmatter"
    if hint_start is not None and hint_end is not None and hint_start <= line_no <= hint_end:
        return "reading_hint"
    return "body"


def check_source_anchors(root: Path, product_md: list[Path]) -> tuple[list[Finding], dict[str, int]]:
    """检查简体原文页 block anchors 是否唯一且落在正文段落。

    事件页依赖 `texts/simplified/第xxx回.md#^hlm-...` 做精确正文定位。
    若锚点在阅读提示/frontmatter 中，链接虽然“可跳转”，但不会把读者带到原文段落；
    若同一锚点重复出现，Obsidian 跳转结果也不可靠。
    """

    findings: list[Finding] = []
    stats = Counter()
    anchor_re = re.compile(r"\^hlm-[A-Za-z0-9_-]+")
    anchor_locations: dict[str, list[tuple[str, int]]] = defaultdict(list)

    source_paths = [
        p
        for p in product_md
        if rel(p, root).startswith("texts/simplified/") and re.search(r"第\d{3}回\.md$", p.name)
    ]

    for path in source_paths:
        r = rel(path, root)
        lines = read_text(path).splitlines()
        frontmatter_end, hint_start, hint_end = source_text_anchor_spans(lines)
        for line_no, line in enumerate(lines, 1):
            for anchor in anchor_re.findall(line):
                stats["scanned"] += 1
                anchor_locations[anchor].append((r, line_no))
                location = source_anchor_location(line_no, frontmatter_end, hint_start, hint_end)
                stats[f"location:{location}"] += 1
                if location != "body":
                    findings.append(
                        Finding(
                            "ERROR",
                            "source_anchor_not_in_body",
                            r,
                            line_no,
                            f"{anchor} 位于 {location}，应迁移到小说正文段落",
                        )
                    )

    for anchor, locations in sorted(anchor_locations.items()):
        if len(locations) <= 1:
            continue
        stats["duplicate"] += 1
        rendered = ", ".join(f"{path}:{line_no}" for path, line_no in locations[:5])
        findings.append(
            Finding(
                "ERROR",
                "source_anchor_duplicate",
                locations[0][0],
                locations[0][1],
                f"{anchor} 出现 {len(locations)} 次：{rendered}",
            )
        )

    for key in ("scanned", "location:body", "location:reading_hint", "location:frontmatter", "duplicate"):
        stats.setdefault(key, 0)
    return findings, dict(stats)


def source_anchor_paths(root: Path, product_md: list[Path]) -> dict[str, set[str]]:
    """收集原文页中已经声明的 `^hlm-*` block anchor。

    `check_source_anchors` 负责检查“锚点自身是否健康”；本索引用于另一类问题：
    事件页/地图页等链接到 `texts/simplified/第xxx回.md#^hlm-*` 时，目标
    block anchor 是否真的存在。
    """

    anchor_re = re.compile(r"\^hlm-[A-Za-z0-9_-]+")
    anchors_by_path: dict[str, set[str]] = defaultdict(set)
    source_paths = [
        p
        for p in product_md
        if rel(p, root).startswith("texts/simplified/") and re.search(r"第\d{3}回\.md$", p.name)
    ]
    for path in source_paths:
        r = rel(path, root)
        anchors_by_path[r].update(anchor_re.findall(read_text(path)))
    return anchors_by_path


def normalize_source_anchor_link_target(raw_target: str) -> tuple[str, str] | None:
    """从 wikilink/Markdown link target 中取出 `(file_path, ^hlm-anchor)`。

    返回 None 表示该链接不是红楼梦原文 block anchor 链接。
    """

    target = raw_target.strip()
    if "|" in target:
        target = target.split("|", 1)[0].strip()
    target = re.sub(r'\s+"[^"]*"\s*$', "", target)
    target = re.sub(r"\s+'[^']*'\s*$", "", target)
    target = unquote(target)
    if "?" in target:
        target = target.split("?", 1)[0]
    if "#^hlm-" not in target:
        return None
    file_target, anchor = target.split("#", 1)
    file_target = file_target.strip()
    anchor = anchor.strip()
    if not anchor.startswith("^hlm-"):
        return None
    if file_target.startswith(WIKI_PREFIX):
        file_target = file_target[len(WIKI_PREFIX) :]
    if file_target.startswith("/"):
        file_target = file_target.lstrip("/")
    return file_target, anchor


def check_source_anchor_references(root: Path, product_md: list[Path]) -> tuple[list[Finding], dict[str, int]]:
    """检查指向原文 block anchor 的链接是否真的能落到目标锚点。

    Obsidian/Wiki 链接解析只确认 `texts/simplified/第xxx回.md` 存在并不够；
    `#^hlm-*` 缺失时，读者仍然无法跳到正文现场。
    """

    findings: list[Finding] = []
    stats = Counter()
    anchors_by_path = source_anchor_paths(root, product_md)
    wikilink_re = re.compile(r"\[\[([^\]]+)\]\]")
    md_link_re = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")

    for path in product_md:
        r = rel(path, root)
        text = read_text(path)
        for line_no, line in iter_non_code_lines(text):
            raw_targets: list[tuple[str, str]] = []
            raw_targets.extend(("wikilink", match.group(1)) for match in wikilink_re.finditer(line))
            raw_targets.extend(("markdown", match.group(1)) for match in md_link_re.finditer(line))

            for link_kind, raw_target in raw_targets:
                normalized = normalize_source_anchor_link_target(raw_target)
                if normalized is None:
                    continue
                target_path, anchor = normalized
                stats["scanned"] += 1
                stats[f"kind:{link_kind}"] += 1

                if target_path not in anchors_by_path:
                    stats["target_file_missing"] += 1
                    findings.append(
                        Finding(
                            "ERROR",
                            "source_anchor_reference_target_missing",
                            r,
                            line_no,
                            f"{raw_target} -> {target_path} 不存在或不是简体原文页",
                        )
                    )
                    continue

                if anchor not in anchors_by_path[target_path]:
                    stats["anchor_missing"] += 1
                    findings.append(
                        Finding(
                            "ERROR",
                            "source_anchor_reference_missing",
                            r,
                            line_no,
                            f"{raw_target} -> {target_path} 中不存在 {anchor}",
                        )
                    )
                    continue

                stats["ok"] += 1

    for key in ("scanned", "ok", "anchor_missing", "target_file_missing", "kind:wikilink", "kind:markdown"):
        stats.setdefault(key, 0)
    return findings, dict(stats)


def event_has_exact_source_anchor(text: str) -> bool:
    return bool(re.search(r"texts/simplified/第\d{3}回\.md#\^hlm-[A-Za-z0-9_-]+", text))


def check_event_source_anchor_coverage(root: Path, product_md: list[Path]) -> tuple[list[Finding], dict[str, int]]:
    """检查事件页是否提供可直接跳到正文段落的原文锚点。

    只链接到某一回导读/原文文件，对读者定位事件现场仍然不够；事件页至少应
    提供一个 `texts/simplified/第xxx回.md#^hlm-*` 精确锚点。
    """

    findings: list[Finding] = []
    stats = Counter()

    for path in product_md:
        r = rel(path, root)
        if not r.startswith("events/"):
            continue
        text = read_text(path)
        fields, _ = parse_frontmatter(text)
        if fields.get("type") != "event":
            continue

        stats["scanned"] += 1
        has_section = "## 原文锚点" in text
        if has_section:
            stats["has_source_anchor_section"] += 1
        else:
            stats["missing_source_anchor_section"] += 1

        if event_has_exact_source_anchor(text):
            stats["ok"] += 1
            continue

        stats["missing_exact_source_anchor"] += 1
        severity = "WARN" if has_section else "ERROR"
        findings.append(
            Finding(
                severity,
                "event_source_anchor_missing",
                r,
                None,
                "事件页缺少 texts/simplified/第xxx回.md#^hlm-* 精确正文锚点",
            )
        )

    for key in ("scanned", "ok", "has_source_anchor_section", "missing_source_anchor_section", "missing_exact_source_anchor"):
        stats.setdefault(key, 0)
    return findings, dict(stats)


def frontmatter_scope(path: Path, root: Path) -> bool:
    r = rel(path, root)
    parts = Path(r).parts
    if path.name in FRONTMATTER_ROOT_SCOPE:
        return True
    if len(parts) >= 2 and parts[0] not in {RAW_DIR, "scripts"}:
        return True
    return False


def check_frontmatter(root: Path, product_md: list[Path]) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    stats = Counter()
    type_counter = Counter()
    for path in product_md:
        if not frontmatter_scope(path, root):
            continue
        r = rel(path, root)
        stats["scanned"] += 1
        text = read_text(path)
        fields, _ = parse_frontmatter(text)
        if not fields:
            stats["missing_frontmatter"] += 1
            findings.append(Finding("ERROR", "frontmatter_missing", r, 1, "缺少 YAML frontmatter"))
            continue
        type_counter[fields.get("type", "unknown")] += 1
        missing = [field for field in FRONTMATTER_REQUIRED_FIELDS if field not in fields]
        if missing:
            stats["missing_required_fields"] += 1
            findings.append(Finding("ERROR", "frontmatter_required_fields", r, 1, f"缺字段: {', '.join(missing)}"))
    stats.update({f"type:{k}": v for k, v in type_counter.items()})
    return findings, dict(stats)


def check_placeholders(root: Path, product_md: list[Path]) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    stats = Counter()
    for path in product_md:
        r = rel(path, root)
        parts = Path(r).parts
        if path.name in PLACEHOLDER_EXCLUDED_FILES:
            continue
        if parts and parts[0] in PLACEHOLDER_EXCLUDED_DIRS:
            continue
        text = read_text(path)
        for line_no, line in iter_non_code_lines(text):
            for term in PLACEHOLDER_TERMS:
                if term in line:
                    if any(hint in line for hint in PLACEHOLDER_NEGATION_HINTS):
                        stats["negated_mentions_skipped"] += 1
                        continue
                    stats["hits"] += 1
                    findings.append(Finding("ERROR", "placeholder_or_banned_phrase", r, line_no, f"命中 {term!r}: {line.strip()[:100]}"))
    return findings, dict(stats)


def check_thin_pages(root: Path, product_md: list[Path]) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    stats = Counter()
    thin_by_type = Counter()
    for path in product_md:
        r = rel(path, root)
        parts = Path(r).parts
        if parts and parts[0] in {"templates"}:
            continue
        # 人物关系指南以枢纽覆盖和双向入口作为专用质量标准，行数阈值不适用。
        if r == RELATIONSHIP_GUIDE_DOC:
            continue
        if path.name in {"README.md", "log.md", "AGENTS.md", "SCHEMA.md", "ROADMAP.md", "START_HERE.md", "index.md"}:
            continue
        text = read_text(path)
        fields, _ = parse_frontmatter(text)
        page_type = fields.get("type", "unknown")
        if page_type not in THIN_THRESHOLDS:
            continue
        line_count = content_line_count(text)
        stats["scanned"] += 1
        stats[f"type:{page_type}"] += 1
        threshold = THIN_THRESHOLDS[page_type]
        if line_count < threshold:
            thin_by_type[page_type] += 1
            findings.append(
                Finding(
                    "WARN",
                    "thin_page_by_type",
                    r,
                    None,
                    f"type={page_type}, nonblank_lines={line_count}, threshold={threshold}",
                )
            )
    stats.update({f"thin:{k}": v for k, v in thin_by_type.items()})
    return findings, dict(stats)


def section_body(text: str, heading: str) -> str:
    """取一个二级标题的正文，不把后续二级标题误算进来。"""
    start = text.find(heading)
    if start < 0:
        return ""
    body_start = start + len(heading)
    next_heading = re.search(r"^##\s+", text[body_start:], re.M)
    if next_heading is None:
        return text[body_start:]
    return text[body_start : body_start + next_heading.start()]


def check_core_chapter_editorial(root: Path) -> tuple[list[Finding], dict[str, int]]:
    """要求核心回目具备可辨识的编辑层，避免回退为批量套话和泛化标签。"""
    findings: list[Finding] = []
    stats = Counter()
    source_anchor_pattern = re.compile(r"texts/simplified/第\d{3}回\.md#\^hlm-")
    concept_pattern = re.compile(r"/concepts/([^\]|#]+)\.md")

    for rel_path in sorted(CORE_CHAPTER_EDITORIAL):
        path = root / rel_path
        stats["scanned"] += 1
        if not path.exists():
            findings.append(Finding("ERROR", "core_chapter_missing", rel_path, None, "核心回目文件不存在"))
            continue
        text = read_text(path)
        for heading in CORE_CHAPTER_REQUIRED_HEADINGS:
            if heading not in text:
                findings.append(Finding("ERROR", "core_chapter_heading_missing", rel_path, None, f"缺少 {heading}"))
        for phrase in CORE_CHAPTER_FORBIDDEN_PHRASES:
            if phrase in text:
                findings.append(Finding("ERROR", "core_chapter_template_phrase", rel_path, None, f"仍含批量套话：{phrase}"))
        anchors = len(source_anchor_pattern.findall(text))
        if anchors < 1:
            findings.append(Finding("ERROR", "core_chapter_source_anchor_missing", rel_path, None, "缺少简体原文精确锚点"))
        else:
            stats["with_source_anchor"] += 1
        concepts = set(concept_pattern.findall(text))
        if len(concepts) > 5:
            findings.append(Finding("ERROR", "core_chapter_concepts_noisy", rel_path, None, f"相关概念 {len(concepts)} 个，应收敛到 5 个以内"))
        else:
            stats["concepts_curated"] += 1

    if not findings:
        stats["ok"] += 1
    return findings, dict(stats)


def check_research_evidence_layers(root: Path, product_md: list[Path]) -> tuple[list[Finding], dict[str, int]]:
    """要求研究综述/精读页区分原文事实、二手研究与 Wiki 综合。"""
    findings: list[Finding] = []
    stats = Counter()
    source_anchor_pattern = re.compile(r"texts/simplified/第\d{3}回\.md#\^hlm-")
    source_block_pattern = re.compile(r"(?ms)^sources:\s*\n((?:\s+-\s+.+\n?)+)")

    for path in product_md:
        r = rel(path, root)
        if not r.startswith("redology/") or not path.name.endswith(("研究综述.md", "精读.md")):
            continue
        stats["scanned"] += 1
        text = read_text(path)
        block = section_body(text, "## 证据分层")
        if not block:
            findings.append(Finding("ERROR", "research_evidence_section_missing", r, None, "缺少“## 证据分层”"))
            continue
        for label in ("**原文事实**", "**研究观点**", "**Wiki 判断**"):
            if label not in block:
                findings.append(Finding("ERROR", "research_evidence_label_missing", r, None, f"证据分层缺少 {label}"))
        if not source_anchor_pattern.search(block):
            findings.append(Finding("ERROR", "research_primary_anchor_missing", r, None, "证据分层中缺少直接原文锚点"))
        else:
            stats["with_primary_anchor"] += 1
        source_match = source_block_pattern.search(text)
        source_block = source_match.group(1) if source_match else ""
        if not source_block or not ("http://" in source_block or "https://" in source_block or "《" in source_block):
            findings.append(Finding("ERROR", "research_secondary_source_missing", r, None, "sources: 缺少可识别的外部文章或著作"))
        else:
            stats["with_secondary_source"] += 1

    if not findings:
        stats["ok"] += 1
    return findings, dict(stats)


def wikilink_targets(text: str) -> set[str]:
    return {
        normalize_wiki_target(match.group(1))
        for match in re.finditer(r"\[\[([^\]]+)\]\]", text)
    }


def check_location_reader_structure(root: Path, product_md: list[Path]) -> tuple[list[Finding], dict[str, int]]:
    """防止地点页重新退化为无说明的长回目清单。"""
    findings: list[Finding] = []
    stats = Counter()

    for path in product_md:
        r = rel(path, root)
        if not r.startswith("locations/"):
            continue
        text = read_text(path)
        fields, _ = parse_frontmatter(text)
        if fields.get("type") != "location":
            continue
        stats["scanned"] += 1
        page_ok = True

        related_chapters = {
            target
            for target in wikilink_targets(section_body(text, "## 相关章节"))
            if re.fullmatch(r"chapters/第\d{3}回\.md", target)
        }
        stats["flat_chapter_links"] += len(related_chapters)
        if len(related_chapters) > 8:
            findings.append(
                Finding(
                    "ERROR",
                    "location_flat_chapter_list",
                    r,
                    None,
                    f"“相关章节”平铺 {len(related_chapters)} 回；应改为关键事件现场与推荐回读",
                )
            )
            page_ok = False

        if r not in LOCATION_READER_HUBS:
            if page_ok:
                stats["ok"] += 1
            continue

        for heading in LOCATION_READER_HEADINGS:
            if heading not in text:
                findings.append(Finding("ERROR", "location_reader_structure_missing", r, None, f"缺少 {heading}"))
                page_ok = False

        event_targets = {
            target
            for target in wikilink_targets(section_body(text, "## 关键事件现场"))
            if target.startswith("events/") and target.endswith(".md")
        }
        chapter_targets = {
            target
            for target in wikilink_targets(section_body(text, "## 推荐回读"))
            if re.fullmatch(r"chapters/第\d{3}回\.md", target)
        }
        stats["hub_event_links"] += len(event_targets)
        stats["hub_recommended_chapters"] += len(chapter_targets)
        if len(event_targets) < 3:
            findings.append(Finding("ERROR", "location_reader_events_thin", r, None, f"关键事件现场仅 {len(event_targets)} 条，应至少 3 条"))
            page_ok = False
        if len(chapter_targets) < 2:
            findings.append(Finding("ERROR", "location_reader_recommended_chapters_thin", r, None, f"推荐回读仅 {len(chapter_targets)} 回，应至少 2 回"))
            page_ok = False

        if page_ok:
            stats["ok"] += 1

    return findings, dict(stats)


def check_relationship_reading_surface(root: Path, product_md: list[Path]) -> tuple[list[Finding], dict[str, int]]:
    """保持人物关系指南与首批关系枢纽人物页之间的双向阅读入口。"""
    findings: list[Finding] = []
    stats = Counter()
    product_by_rel = {rel(path, root): path for path in product_md}
    guide = product_by_rel.get(RELATIONSHIP_GUIDE_DOC)
    if guide is None:
        findings.append(Finding("ERROR", "relationship_guide_missing", RELATIONSHIP_GUIDE_DOC, None, "缺少人物关系阅读指南"))
        return findings, dict(stats)

    guide_text = read_text(guide)
    guide_fields, _ = parse_frontmatter(guide_text)
    stats["guide_scanned"] += 1
    if guide_fields.get("type") != "output":
        findings.append(Finding("ERROR", "relationship_guide_type", RELATIONSHIP_GUIDE_DOC, 1, "人物关系阅读指南的 type 应为 output"))
    missing_guide_headings = [heading for heading in RELATIONSHIP_GUIDE_HEADINGS if heading not in guide_text]
    if missing_guide_headings:
        findings.append(Finding("ERROR", "relationship_guide_sections_missing", RELATIONSHIP_GUIDE_DOC, None, f"缺少关系主线: {missing_guide_headings}"))
    guide_targets = wikilink_targets(guide_text)
    missing_hubs_in_guide = sorted(RELATIONSHIP_HUBS - guide_targets)
    if missing_hubs_in_guide:
        findings.append(Finding("ERROR", "relationship_guide_hubs_missing", RELATIONSHIP_GUIDE_DOC, None, f"未覆盖关系枢纽: {missing_hubs_in_guide}"))

    for hub_rel in sorted(RELATIONSHIP_HUBS):
        stats["hub_scanned"] += 1
        path = product_by_rel.get(hub_rel)
        if path is None:
            findings.append(Finding("ERROR", "relationship_hub_missing", hub_rel, None, "关系枢纽人物页不存在"))
            continue
        text = read_text(path)
        fields, _ = parse_frontmatter(text)
        if fields.get("type") != "character":
            findings.append(Finding("ERROR", "relationship_hub_type", hub_rel, 1, "关系枢纽应为 character 页面"))
            continue
        body = section_body(text, "## 关系阅读")
        if not body:
            findings.append(Finding("ERROR", "relationship_hub_section_missing", hub_rel, None, "缺少 ## 关系阅读"))
            continue
        targets = wikilink_targets(body)
        character_targets = {target for target in targets if target.startswith("characters/") and target.endswith(".md")}
        if RELATIONSHIP_GUIDE_DOC not in targets:
            findings.append(Finding("ERROR", "relationship_hub_guide_missing", hub_rel, None, "关系阅读区块未回链人物关系阅读指南"))
        if len(character_targets) < 3:
            findings.append(Finding("ERROR", "relationship_hub_links_thin", hub_rel, None, f"关系阅读区块仅链接 {len(character_targets)} 名人物，应至少 3 名"))
        else:
            stats["hub_with_three_character_links"] += 1

    if not findings:
        stats["ok"] += 1
    return findings, dict(stats)


def count_markdown_in(root: Path, subdir: str) -> int:
    path = root / subdir
    if not path.exists():
        return 0
    return sum(1 for p in path.rglob("*.md") if p.is_file() and not any(part in SKIP_DIRS for part in p.parts))


def directory_counts(root: Path) -> dict[str, int]:
    return {d: count_markdown_in(root, d) for d in COUNT_DIRS}


def check_self_description(
    root: Path,
    product_count: int,
    managed_count: int,
    maintenance_count: int,
    dir_counts: dict[str, int],
) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    stats = Counter()
    output_actual = dir_counts.get("outputs", 0)

    total_patterns = [
        re.compile(r"总文件数[：:\s]*([0-9]+)"),
        re.compile(r"总 Markdown 文件\s*\|\s*([0-9]+)"),
        re.compile(r"\|\s*\*\*总计\*\*\s*\|\s*\*\*([0-9]+)\*\*"),
        re.compile(r"\|\s*\*\*总 Markdown\*\*\s*\|\s*\*\*([0-9]+)\*\*"),
    ]
    product_patterns = [
        re.compile(r"^\|\s*成品 Wiki Markdown\s*\|\s*(?:\*\*)?([0-9]+)(?:\*\*)?\s*\|", re.M),
    ]
    managed_patterns = [
        re.compile(r"^\|\s*(?:\*\*)?成品\s*\+?\s*raw 管理口径(?:\*\*)?\s*\|\s*(?:\*\*)?([0-9]+)(?:\*\*)?\s*\|", re.M),
    ]
    all_markdown_patterns = [
        re.compile(r"^\|\s*全部 Markdown\s*\|\s*(?:\*\*)?([0-9]+)(?:\*\*)?\s*\|", re.M),
    ]
    output_patterns = [
        re.compile(r"^\|\s*输出产品\s*\|\s*\*?([0-9]+)\*?\s*\|", re.M),
        re.compile(r"^\|\s*`?outputs/?`?[^|]*\|\s*\*?([0-9]+)\*?\s*\|", re.M),
    ]

    for rel_doc in SELF_DESCRIPTION_DOCS:
        path = root / rel_doc
        if not path.exists():
            continue
        text = read_text(path)
        for pattern in product_patterns:
            for match in pattern.finditer(text):
                claimed = int(match.group(1))
                stats["product_claims"] += 1
                if claimed != product_count:
                    findings.append(
                        Finding(
                            "ERROR",
                            "self_description_product_count",
                            rel_doc,
                            None,
                            f"成品口径声称 {claimed}，实际 {product_count}",
                        )
                    )
        for pattern in total_patterns:
            for match in pattern.finditer(text):
                claimed = int(match.group(1))
                stats["total_claims"] += 1
                # 目前公开口径应是成品 Wiki Markdown；raw 原始文本另列。
                if claimed != product_count:
                    findings.append(
                        Finding(
                            "ERROR",
                            "self_description_total_count",
                            rel_doc,
                            None,
                            f"声称 {claimed}，当前成品口径 {product_count}；成品+raw 管理口径 {managed_count}",
                        )
                    )
        for pattern in managed_patterns:
            for match in pattern.finditer(text):
                claimed = int(match.group(1))
                stats["managed_claims"] += 1
                if claimed != managed_count:
                    findings.append(
                        Finding(
                            "ERROR",
                            "self_description_managed_count",
                            rel_doc,
                            None,
                            f"成品+raw 声称 {claimed}，实际 {managed_count}",
                        )
                    )
        for pattern in all_markdown_patterns:
            for match in pattern.finditer(text):
                claimed = int(match.group(1))
                expected = managed_count + maintenance_count
                stats["all_markdown_claims"] += 1
                if claimed != expected:
                    findings.append(
                        Finding(
                            "ERROR",
                            "self_description_all_markdown_count",
                            rel_doc,
                            None,
                            f"全部 Markdown 声称 {claimed}，实际 {expected}",
                        )
                    )
        for pattern in output_patterns:
            for match in pattern.finditer(text):
                claimed = int(match.group(1))
                stats["output_claims"] += 1
                if claimed != output_actual:
                    findings.append(
                        Finding(
                            "ERROR",
                            "self_description_outputs_count",
                            rel_doc,
                            None,
                            f"outputs 声称 {claimed}，实际 Markdown {output_actual}",
                        )
                    )
    return findings, dict(stats)


def check_version_consistency(root: Path) -> tuple[list[Finding], dict[str, int]]:
    """确保 README、SCHEMA 与站点首页使用同一版本号。"""
    findings: list[Finding] = []
    stats = Counter()
    versions: dict[str, str] = {}

    for name in ("SCHEMA.md", "index.md"):
        path = root / name
        if not path.exists():
            findings.append(Finding("ERROR", "version_document_missing", name, None, "版本文档不存在"))
            continue
        fields, _ = parse_frontmatter(read_text(path))
        version = fields.get("version", "")
        if version:
            versions[name] = version
            stats["declared"] += 1
        else:
            findings.append(Finding("ERROR", "version_missing", name, 1, "frontmatter 缺少 version"))

    readme = root / "README.md"
    if readme.exists():
        match = re.search(r"当前版本[：:]\s*(v\d+\.\d+\.\d+)", read_text(readme))
        if match:
            versions["README.md"] = match.group(1)
            stats["declared"] += 1
        else:
            findings.append(Finding("ERROR", "version_missing", "README.md", None, "缺少当前版本声明"))

    if versions and len(set(versions.values())) == 1:
        stats["consistent"] += 1
    elif versions:
        findings.append(
            Finding(
                "ERROR",
                "version_mismatch",
                "SCHEMA.md",
                None,
                f"版本号不一致: {versions}",
            )
        )
    return findings, dict(stats)


def run_git(root: Path, arguments: list[str]) -> subprocess.CompletedProcess[str] | None:
    """只读执行 Git 查询；脱离 Git 仓库时返回 None，不把环境限制误报成内容错误。"""
    try:
        return subprocess.run(
            ["git", *arguments],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError:
        return None


def check_release_log(root: Path) -> tuple[list[Finding], dict[str, int]]:
    """要求读者可见的发布变动与 log.md 同步，避免日志长期停留在旧版本。"""
    findings: list[Finding] = []
    stats = Counter()
    path = root / RELEASE_LOG_DOC
    if not path.exists():
        findings.append(Finding("ERROR", "release_log_missing", RELEASE_LOG_DOC, None, "缺少面向读者的发布日志"))
        return findings, dict(stats)

    dated_entries = []
    for line_no, line in enumerate(read_text(path).splitlines(), 1):
        match = RELEASE_LOG_DATE_RE.match(line)
        if match:
            dated_entries.append((match.group(1), line_no))

    stats["dated_entries"] = len(dated_entries)
    if not dated_entries:
        findings.append(Finding("ERROR", "release_log_format", RELEASE_LOG_DOC, 1, "缺少格式为 `## YYYY-MM-DD｜说明` 的发布记录"))
        return findings, dict(stats)

    latest_log_date, latest_log_line = dated_entries[0]
    if latest_log_date != max(date for date, _ in dated_entries):
        findings.append(Finding("ERROR", "release_log_order", RELEASE_LOG_DOC, latest_log_line, "发布记录应按日期倒序，最新记录必须位于顶部"))

    latest_commit = run_git(
        root,
        ["log", "-1", "--format=%as", "--", *RELEASE_LOG_PATHS],
    )
    if latest_commit is None or latest_commit.returncode != 0 or not latest_commit.stdout.strip():
        stats["git_history_unavailable"] += 1
        return findings, dict(stats)

    latest_release_date = latest_commit.stdout.strip()
    stats["git_history_checked"] += 1
    if latest_log_date < latest_release_date:
        findings.append(
            Finding(
                "ERROR",
                "release_log_stale",
                RELEASE_LOG_DOC,
                latest_log_line,
                f"最新日志日期 {latest_log_date}，但读者可见内容或发布机制最新变更日期为 {latest_release_date}",
            )
        )

    changed_paths: set[str] = set()
    worktree_paths = [*RELEASE_LOG_PATHS, RELEASE_LOG_DOC]
    for arguments in (
        ["diff", "--name-only", "--", *worktree_paths],
        ["diff", "--cached", "--name-only", "--", *worktree_paths],
    ):
        changed = run_git(root, arguments)
        if changed is not None and changed.returncode == 0:
            changed_paths.update(path for path in changed.stdout.splitlines() if path)

    if changed_paths:
        stats["uncommitted_release_paths"] = len(changed_paths)
        if RELEASE_LOG_DOC not in changed_paths:
            findings.append(
                Finding(
                    "ERROR",
                    "release_log_missing_for_worktree_change",
                    RELEASE_LOG_DOC,
                    latest_log_line,
                    f"当前待提交的读者可见改动未同步更新 log.md: {sorted(changed_paths)}",
                )
            )

    if not findings:
        stats["ok"] += 1
    return findings, dict(stats)


def parse_int_tuple(raw: str, expected_length: int) -> tuple[int, ...] | None:
    """Parse a compact frontmatter list such as ``[106, 62, 17, 27]``."""

    value = raw.strip()
    if not (value.startswith("[") and value.endswith("]")):
        return None
    try:
        items = tuple(int(item.strip()) for item in value[1:-1].split(",") if item.strip())
    except ValueError:
        return None
    return items if len(items) == expected_length else None


def check_governance_snapshots(root: Path) -> tuple[list[Finding], dict[str, int]]:
    """Keep the human-readable character-line review in sync with live scripts.

    The review page carries the current baseline in frontmatter and repeats it in
    prose for readers. This check validates both surfaces against the read-only
    character-line scripts, so a later event-link fix cannot silently leave an
    old heading or ``--strict-current`` explanation behind.
    """

    findings: list[Finding] = []
    stats = Counter()
    path = root / GOVERNANCE_SNAPSHOT_DOC
    if not path.exists():
        findings.append(Finding("ERROR", "governance_snapshot_missing", GOVERNANCE_SNAPSHOT_DOC, None, "缺少人物事件线当前快照文档"))
        return findings, dict(stats)

    text = read_text(path)
    fields, _ = parse_frontmatter(text)
    documented_line = parse_int_tuple(fields.get("character_event_line_baseline", ""), 4)
    documented_reverse = parse_int_tuple(fields.get("character_event_reverse_baseline", ""), 3)

    try:
        from character_event_line_review import CURRENT_BASELINE as line_script_baseline
        from character_event_line_review import classify as classify_character_event_lines
        from character_event_reverse_link_check import CURRENT_BASELINE as reverse_script_baseline
        from character_event_reverse_link_check import check_reverse_links
    except ImportError as exc:
        findings.append(Finding("ERROR", "governance_snapshot_import", GOVERNANCE_SNAPSHOT_DOC, None, f"无法导入人物线检查脚本: {exc}"))
        return findings, dict(stats)

    line_data = classify_character_event_lines(root)
    live_line = (
        line_data["total_character_files"],
        len(line_data["with_major_event_line"]),
        len(line_data["event_linked_without_major_event_line"]),
        len(line_data["zero_event_links_without_major_event_line"]),
    )
    reverse_data = check_reverse_links(root)
    live_reverse = (
        reverse_data["scanned_characters"],
        reverse_data["scanned_event_links"],
        len(reverse_data["gaps"]),
    )

    checks = [
        ("character_event_line_baseline", documented_line, tuple(line_script_baseline), live_line),
        ("character_event_reverse_baseline", documented_reverse, tuple(reverse_script_baseline), live_reverse),
    ]
    for field_name, documented, script_baseline, live in checks:
        stats["scanned"] += 1
        if documented is None:
            findings.append(Finding("ERROR", "governance_snapshot_format", GOVERNANCE_SNAPSHOT_DOC, 1, f"frontmatter {field_name} 应为整数列表"))
            continue
        if documented != script_baseline:
            findings.append(Finding("ERROR", "governance_snapshot_script_mismatch", GOVERNANCE_SNAPSHOT_DOC, 1, f"{field_name}={documented}，脚本基线={script_baseline}"))
        if documented != live:
            findings.append(Finding("ERROR", "governance_snapshot_live_mismatch", GOVERNANCE_SNAPSHOT_DOC, 1, f"{field_name}={documented}，实时统计={live}"))
        if documented == script_baseline == live:
            stats["ok"] += 1

    summary_patterns = [
        ("人物页总数", r"- 人物页总数：(\d+)", documented_line[0] if documented_line else None),
        ("主要事件线人数", r"- 已有 `## 主要事件线`：(\d+)", documented_line[1] if documented_line else None),
        ("单点反链人数", r"- 还有事件页反链、但暂不补主要事件线：(\d+)", documented_line[2] if documented_line else None),
        ("零反链人数", r"- 当前没有事件页反链、暂不补主要事件线：(\d+)", documented_line[3] if documented_line else None),
        ("单点分组标题", r"^## 暂不补：有事件页反链但只有单点的 (\d+) 人$", documented_line[2] if documented_line else None),
        ("反链闸门", r"当前反链闸门：已有主要事件线的 (\d+) 人物，共 (\d+) 条人物线事件链接，事件页反链缺口为 (\d+)", documented_reverse),
    ]
    for label, pattern, expected in summary_patterns:
        stats["prose_scanned"] += 1
        match = re.search(pattern, text, re.M)
        if match is None or expected is None:
            findings.append(Finding("ERROR", "governance_snapshot_prose_missing", GOVERNANCE_SNAPSHOT_DOC, None, f"缺少或无法解析{label}"))
            continue
        actual = tuple(int(value) for value in match.groups())
        expected_tuple = expected if isinstance(expected, tuple) else (expected,)
        if actual != expected_tuple:
            findings.append(Finding("ERROR", "governance_snapshot_prose_mismatch", GOVERNANCE_SNAPSHOT_DOC, None, f"{label}={actual}，应为{expected_tuple}"))
            continue
        stats["prose_ok"] += 1

    expected_single_names = {
        row["name"] for row in line_data["event_linked_without_major_event_line"]
    }
    expected_zero_names = {
        row["name"] for row in line_data["zero_event_links_without_major_event_line"]
    }
    single_section = re.search(
        r"## 暂不补：有事件页反链但只有单点的 \d+ 人\n(.*?)(?=\n## 暂不补：当前零事件反链)",
        text,
        re.S,
    )
    zero_section = re.search(
        r"## 暂不补：当前零事件反链的 \d+ 人\n(.*?)(?=\n## 后续维护闸门)",
        text,
        re.S,
    )
    if single_section is None:
        findings.append(Finding("ERROR", "governance_snapshot_member_section_missing", GOVERNANCE_SNAPSHOT_DOC, None, "缺少单点反链人物表"))
    else:
        documented_single_names = {
            match.group(1).strip()
            for match in re.finditer(r"^\|\s*([^|]+?)\s*\|", single_section.group(1), re.M)
            if match.group(1).strip() not in {"人物", "---"}
        }
        stats["member_lists_scanned"] += 1
        if documented_single_names != expected_single_names:
            findings.append(Finding("ERROR", "governance_snapshot_member_mismatch", GOVERNANCE_SNAPSHOT_DOC, None, f"单点反链人物表与实时结果不一致；缺少={sorted(expected_single_names - documented_single_names)}，多出={sorted(documented_single_names - expected_single_names)}"))
        else:
            stats["member_lists_ok"] += 1

    if zero_section is None:
        findings.append(Finding("ERROR", "governance_snapshot_member_section_missing", GOVERNANCE_SNAPSHOT_DOC, None, "缺少零反链人物名单"))
    else:
        documented_zero_names = {
            match.group(1).strip()
            for match in re.finditer(r"^-\s+([^\n]+)$", zero_section.group(1), re.M)
        }
        stats["member_lists_scanned"] += 1
        if documented_zero_names != expected_zero_names:
            findings.append(Finding("ERROR", "governance_snapshot_member_mismatch", GOVERNANCE_SNAPSHOT_DOC, None, f"零反链人物名单与实时结果不一致；缺少={sorted(expected_zero_names - documented_zero_names)}，多出={sorted(documented_zero_names - expected_zero_names)}"))
        else:
            stats["member_lists_ok"] += 1

    return findings, dict(stats)


def render_section(title: str, lines: list[str]) -> list[str]:
    out = [f"\n## {title}"]
    out.extend(lines or ["无"])
    return out


def summarize_findings(findings: list[Finding], limit: int) -> list[str]:
    grouped: dict[str, list[Finding]] = defaultdict(list)
    for finding in findings:
        grouped[finding.category].append(finding)

    lines: list[str] = []
    for category in sorted(grouped):
        items = grouped[category]
        sev = Counter(item.severity for item in items)
        lines.append(f"- {category}: {len(items)}（" + ", ".join(f"{k}={v}" for k, v in sorted(sev.items())) + "）")
        for item in items[:limit]:
            lines.append(f"  - {item.render()}")
        if len(items) > limit:
            lines.append(f"  - ... 另有 {len(items) - limit} 条，调大 --limit 查看")
    return lines


def render_report(
    root: Path,
    all_md: list[Path],
    product_md: list[Path],
    raw_md: list[Path],
    maintenance_md: list[Path],
    dir_counts: dict[str, int],
    all_stats: dict[str, dict[str, int]],
    findings: list[Finding],
    limit: int,
) -> str:
    now = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_count = sum(1 for f in findings if f.severity == "ERROR")
    warn_count = sum(1 for f in findings if f.severity == "WARN")
    managed_count = len(product_md) + len(raw_md)

    lines: list[str] = [
        "# 红楼梦 Wiki 健康检查报告",
        "",
        f"- 生成时间: {now}",
        f"- Wiki 根目录: {root}",
        f"- 总体状态: {'NEEDS_ATTENTION' if error_count else 'OK'}",
        f"- ERROR: {error_count}",
        f"- WARN: {warn_count}",
        "",
        "## 统计口径",
        f"- 成品 Wiki Markdown: {len(product_md)}（排除 raw/、维护交接文档、脚本目录文档）",
        f"- raw/ 原始文本 Markdown: {len(raw_md)}",
        f"- 成品+raw 管理口径: {managed_count}",
        f"- 维护/审查 Markdown: {len(maintenance_md)}",
        f"- 全部 Markdown: {len(all_md)}",
    ]

    count_lines = [f"- {name}: {count}" for name, count in dir_counts.items()]
    # 图片不是 Markdown，但 README 中单独声明，顺手只读报告，避免混到 Markdown 总数。
    image_dir = root / "images"
    if image_dir.exists():
        image_count = sum(1 for p in image_dir.iterdir() if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".svg", ".webp"})
        count_lines.append(f"- images/*: {image_count} image files")
    lines.extend(render_section("目录计数", count_lines))

    stat_lines: list[str] = []
    for name, stats in all_stats.items():
        if not stats:
            stat_lines.append(f"- {name}: 无统计")
            continue
        compact = ", ".join(f"{k}={v}" for k, v in sorted(stats.items()))
        stat_lines.append(f"- {name}: {compact}")
    lines.extend(render_section("检查统计", stat_lines))

    lines.extend(render_section("发现项", summarize_findings(findings, limit)))

    lines.extend(
        render_section(
            "解释",
            [
                "- alias 类型 WARN 表示短名可通过 alias map 解析，但建议在 Phase 2 改成文件级链接，例如 [[characters/贾宝玉.md|宝玉]]。",
                "- table_alias_wikilink 表示 Markdown 表格行里出现 `[[path|alias]]`；表格分隔符 `|` 会和 Obsidian alias 冲突，应用列表或去掉 alias。",
                "- chapter_key_event_link_unlocalized 表示章节页“关键事件”链接到事件页，但该事件页没有声明对应回目；通常应补事件页定位或移除误链。",
                "- source_anchor_not_in_body/source_anchor_duplicate 表示原文 block anchor 不在小说正文段落或重复；这会导致事件页跳转不到真正正文现场，属于 ERROR。",
                "- source_anchor_reference_missing 表示页面链接到了不存在的原文 block anchor；链接文件存在但无法精确跳转，属于 ERROR。",
                "- frontmatter_source_local_missing 表示 `sources:` 声明了本地文件但目标不存在；traditional_source_external_missing 表示繁体发布原文缺少可公开复核的来源 URL。",
                "- event_source_anchor_missing 表示事件页没有提供 `texts/simplified/第xxx回.md#^hlm-*` 精确正文锚点；若已有“原文锚点”区块则先作为 WARN。",
                "- thin_page_by_type 是内容编辑提示，不等同于错误；不同 type 使用不同阈值。",
                "- location_flat_chapter_list 表示地点页把超过 8 个回目平铺为“相关章节”；应改为有解释的关键事件现场和推荐回读。",
                "- location_reader_* 表示怡红院、潇湘馆、宁国府、栊翠庵缺少既定的空间阅读结构或关键入口。",
                "- relationship_* 表示人物关系阅读指南或首批关系枢纽人物页缺少双向、可点击的人物关系入口。",
                "- release_log_stale/release_log_missing_for_worktree_change 表示读者可见内容或发布机制已经变更，但 log.md 未在同一发布批次中更新，属于 ERROR。",
                "- 默认运行只生成报告；如需把结构问题作为闸门，请加 --strict。",
            ],
        )
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve() if args.root else default_root()
    if not root.exists():
        print(f"Wiki 根目录不存在: {root}", file=sys.stderr)
        return 2

    files = all_files(root)
    md_files = sorted([p for p in files if p.suffix == ".md"])
    product_md = sorted([p for p in md_files if classify_markdown(p, root) == "product"])
    raw_md = sorted([p for p in md_files if classify_markdown(p, root) == "raw"])
    maintenance_md = sorted([p for p in md_files if classify_markdown(p, root) == "maintenance"])

    indexes = build_target_indexes(root, files)
    dir_counts = directory_counts(root)

    findings: list[Finding] = []
    all_stats: dict[str, dict[str, int]] = {}

    checkers = [
        ("frontmatter", lambda: check_frontmatter(root, product_md)),
        ("frontmatter_sources", lambda: check_frontmatter_sources(root, product_md)),
        ("wikilinks", lambda: check_wikilinks(root, product_md, indexes)),
        ("table_alias_wikilinks", lambda: check_table_alias_wikilinks(root, product_md + maintenance_md)),
        ("markdown_links", lambda: check_markdown_links(root, product_md)),
        ("chapter_key_event_links", lambda: check_chapter_key_event_links(root, product_md, indexes)),
        ("source_anchors", lambda: check_source_anchors(root, product_md)),
        ("source_anchor_references", lambda: check_source_anchor_references(root, product_md)),
        ("event_source_anchor_coverage", lambda: check_event_source_anchor_coverage(root, product_md)),
        ("placeholders", lambda: check_placeholders(root, product_md)),
        ("thin_pages", lambda: check_thin_pages(root, product_md)),
        ("core_chapter_editorial", lambda: check_core_chapter_editorial(root)),
        ("research_evidence_layers", lambda: check_research_evidence_layers(root, product_md)),
        ("location_reader_structure", lambda: check_location_reader_structure(root, product_md)),
        ("relationship_reading_surface", lambda: check_relationship_reading_surface(root, product_md)),
        ("self_description", lambda: check_self_description(root, len(product_md), len(product_md) + len(raw_md), len(maintenance_md), dir_counts)),
        ("version_consistency", lambda: check_version_consistency(root)),
        ("release_log", lambda: check_release_log(root)),
        ("governance_snapshots", lambda: check_governance_snapshots(root)),
    ]

    for name, checker in checkers:
        checker_findings, stats = checker()
        findings.extend(checker_findings)
        all_stats[name] = stats

    report = render_report(
        root=root,
        all_md=md_files,
        product_md=product_md,
        raw_md=raw_md,
        maintenance_md=maintenance_md,
        dir_counts=dir_counts,
        all_stats=all_stats,
        findings=findings,
        limit=args.limit,
    )

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
    print(report)

    has_error = any(f.severity == "ERROR" for f in findings)
    if args.strict and has_error:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
