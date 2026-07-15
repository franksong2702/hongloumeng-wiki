#!/usr/bin/env python3
"""生成或核对红楼梦 Wiki 的单一状态快照。

用法：
  python3 scripts/generate_wiki_status.py
  python3 scripts/generate_wiki_status.py --check
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

from wiki_health_check import (
    all_files,
    classify_markdown,
    directory_counts,
)


STATUS_FILE = "WIKI_STATUS.md"
RELEASE_LOG_DATE_RE = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})(?:[｜：:]|\s)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成红楼梦 Wiki 状态页")
    parser.add_argument("--root", help="Wiki 根目录（默认为脚本上级目录）")
    parser.add_argument("--check", action="store_true", help="只核对现有状态页，不写文件")
    return parser.parse_args()


def wiki_root(args: argparse.Namespace) -> Path:
    if args.root:
        return Path(args.root).resolve()
    return Path(__file__).resolve().parents[1]


def release_date(root: Path) -> str:
    """返回可重复的发布日期。

    Vault 与发布仓库统一以 `log.md` 最新发布条目为准。只有日志不可用时才
    回退到 Git 最新提交日期；不使用“今天”，避免同一份内容跨天变成 stale。
    """
    release_log = root / "log.md"
    if release_log.exists():
        dates = [
            match.group(1)
            for line in release_log.read_text(encoding="utf-8").splitlines()
            if (match := RELEASE_LOG_DATE_RE.match(line))
        ]
        if dates:
            return max(dates)

    latest = subprocess.run(
        ["git", "log", "-1", "--format=%as"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if latest.returncode == 0 and latest.stdout.strip():
        return latest.stdout.strip()

    raise RuntimeError("无法从 log.md 或 Git 历史确定可重复的发布日期")


def render(root: Path) -> str:
    files = all_files(root)
    md_files = sorted(path for path in files if path.suffix == ".md")
    product = [path for path in md_files if classify_markdown(path, root) == "product"]
    maintenance = [path for path in md_files if classify_markdown(path, root) == "maintenance"]
    counts = directory_counts(root)
    updated = release_date(root)

    rows = [
        ("章节导读", counts["chapters"]),
        ("简体原文", counts["texts/simplified"]),
        ("繁体原文", counts["texts/traditional"]),
        ("人物", counts["characters"]),
        ("事件", counts["events"]),
        ("概念", counts["concepts"]),
        ("地点", counts["locations"]),
        ("诗词", counts["poetry"]),
        ("红学与研究", counts["redology"]),
        ("背景", counts["background"]),
        ("图谱", counts["maps"]),
        ("时间线", counts["timelines"]),
        ("家族", counts["families"]),
        ("意象", counts["motifs-symbols"]),
        ("查询索引", counts["queries"]),
        ("输出产品", counts["outputs"]),
    ]
    table = "\n".join(f"| {label} | {value} |" for label, value in rows)

    return f"""---
title: 红楼梦 Wiki 当前状态
created: 2026-07-12
updated: {updated}
type: meta
book: 红楼梦
status: generated
tags: [hongloumeng, maintenance, generated]
---

# 红楼梦 Wiki 当前状态

> 本页由 `scripts/generate_wiki_status.py` 生成。数量变化后必须重新生成；Vault 与发布仓库统一使用 `log.md` 最新发布日期，只有日志不可用时才回退到 Git 日期，GitHub Actions 会拒绝不一致的状态页。

## 管理口径

| 口径 | 数量 |
|---|---:|
| 成品 Wiki Markdown | {len(product)} |
| 维护/审查 Markdown | {len(maintenance)} |

`raw/` 是本地可选的采集证据，不属于公共发布仓库或静态站依赖，因此不纳入这张可复现的发布状态表；本地管理时可与成品数分开统计。

## 读者内容

| 模块 | Markdown |
|---|---:|
{table}

## 质量闸门

- 严格健康检查：`python3 scripts/wiki_health_check.py --strict`
- 状态页一致性：`python3 scripts/generate_wiki_status.py --check`
- 外部来源检查：`python3 scripts/external_link_check.py --strict`
- 静态站构建：`python3 scripts/mkdocs_build_check.py`

## 阅读入口

- [[02_Learn/08_book-wikis/红楼梦/index.md|站点首页]]
- [[02_Learn/08_book-wikis/红楼梦/START_HERE.md|完整阅读入口]]
- [[02_Learn/08_book-wikis/红楼梦/log.md|发布日志]]
- [[02_Learn/08_book-wikis/红楼梦/redology/证据使用规范.md|证据使用规范]]
"""


def main() -> int:
    args = parse_args()
    root = wiki_root(args)
    target = root / STATUS_FILE
    expected = render(root)

    if args.check:
        if not target.exists():
            print(f"WIKI_STATUS_CHECK: status=FAIL reason=missing path={target}")
            return 1
        if target.read_text(encoding="utf-8") != expected:
            print(f"WIKI_STATUS_CHECK: status=FAIL reason=stale path={target}")
            return 1
        print(f"WIKI_STATUS_CHECK: status=OK path={target}")
        return 0

    target.write_text(expected, encoding="utf-8")
    print(f"WIKI_STATUS_GENERATE: status=OK path={target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
