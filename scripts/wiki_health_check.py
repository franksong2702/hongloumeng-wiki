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
    "ROADMAP.md",
    "AGENTS.md",
    "outputs/红楼梦编译总评.md",
]


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
    output_patterns = [
        re.compile(r"^\|\s*输出产品\s*\|\s*\*?([0-9]+)\*?\s*\|", re.M),
        re.compile(r"^\|\s*`?outputs/?`?[^|]*\|\s*\*?([0-9]+)\*?\s*\|", re.M),
    ]

    for rel_doc in SELF_DESCRIPTION_DOCS:
        path = root / rel_doc
        if not path.exists():
            continue
        text = read_text(path)
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
                "- thin_page_by_type 是内容编辑提示，不等同于错误；不同 type 使用不同阈值。",
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
        ("wikilinks", lambda: check_wikilinks(root, product_md, indexes)),
        ("markdown_links", lambda: check_markdown_links(root, product_md)),
        ("placeholders", lambda: check_placeholders(root, product_md)),
        ("thin_pages", lambda: check_thin_pages(root, product_md)),
        ("self_description", lambda: check_self_description(root, len(product_md), len(product_md) + len(raw_md), dir_counts)),
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
