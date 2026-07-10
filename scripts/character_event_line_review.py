#!/usr/bin/env python3
"""Review character pages by major-event-line coverage.

This script is intentionally read-only. It classifies characters into:
- characters that already have `## 主要事件线`
- event-linked characters without a major event line
- characters with no event-page reverse links

It is used as a governance check for the Hongloumeng Wiki maintenance workflow:
not every character should receive a fake timeline. Characters with only one
known event node should normally remain in the review bucket until more nodes or
missing links are found.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import argparse
import json
import re
import sys

VAULT_PREFIX = "02_Learn/08_book-wikis/红楼梦"
CHAR_LINK_RE = re.compile(r"02_Learn/08_book-wikis/红楼梦/characters/([^\]|#]+)\.md")


def read_title(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^title:\s*(.+)$", text, re.M)
    return match.group(1).strip().strip('"') if match else path.stem


def classify(root: Path) -> dict:
    char_dir = root / "characters"
    event_dir = root / "events"
    if not char_dir.exists() or not event_dir.exists():
        raise FileNotFoundError("expected characters/ and events/ under wiki root")

    event_links: dict[str, set[str]] = defaultdict(set)
    for event_path in sorted(event_dir.glob("*.md"), key=lambda p: p.stem):
        text = event_path.read_text(encoding="utf-8")
        for match in CHAR_LINK_RE.finditer(text):
            event_links[match.group(1)].add(event_path.stem)

    with_line = []
    event_linked_without_line = []
    zero_event_links = []

    for char_path in sorted(char_dir.glob("*.md"), key=lambda p: p.stem):
        text = char_path.read_text(encoding="utf-8")
        name = char_path.stem
        events = sorted(event_links.get(name, set()))
        row = {
            "name": name,
            "path": f"{VAULT_PREFIX}/characters/{name}.md",
            "event_count": len(events),
            "events": events,
            "has_major_event_line": "## 主要事件线" in text,
        }
        if row["has_major_event_line"]:
            with_line.append(row)
        elif events:
            event_linked_without_line.append(row)
        else:
            zero_event_links.append(row)

    event_linked_without_line.sort(key=lambda r: (-r["event_count"], r["name"]))
    zero_event_links.sort(key=lambda r: r["name"])
    with_line.sort(key=lambda r: (-r["event_count"], r["name"]))

    return {
        "total_character_files": len(with_line) + len(event_linked_without_line) + len(zero_event_links),
        "with_major_event_line": with_line,
        "event_linked_without_major_event_line": event_linked_without_line,
        "zero_event_links_without_major_event_line": zero_event_links,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Wiki root directory")
    parser.add_argument("--json-output", help="Optional JSON output path")
    parser.add_argument("--strict-current", action="store_true", help="Assert the current curated character-line baseline")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    data = classify(root)
    with_line = data["with_major_event_line"]
    linked_missing = data["event_linked_without_major_event_line"]
    zero_missing = data["zero_event_links_without_major_event_line"]

    print("CHARACTER_EVENT_LINE_REVIEW")
    print(f"total_character_files={data['total_character_files']}")
    print(f"with_major_event_line={len(with_line)}")
    print(f"event_linked_without_major_event_line={len(linked_missing)}")
    print(f"zero_event_links_without_major_event_line={len(zero_missing)}")

    print("\n[event_linked_without_major_event_line]")
    for row in linked_missing:
        print(f"{row['event_count']:2d}\t{row['name']}\t" + "、".join(row["events"]))

    print("\n[zero_event_links_without_major_event_line]")
    for row in zero_missing:
        print(row["name"])

    if args.json_output:
        Path(args.json_output).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.strict_current:
        expected = (106, 62, 17, 27)
        actual = (data["total_character_files"], len(with_line), len(linked_missing), len(zero_missing))
        if actual != expected:
            print(f"STRICT_CURRENT_MISMATCH expected={expected} actual={actual}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
