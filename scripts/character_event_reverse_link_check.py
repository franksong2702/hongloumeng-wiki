#!/usr/bin/env python3
"""Check reverse links for character major event lines.

Read-only governance check:
- For every character page with `## 主要事件线`, extract event wikilinks in that section.
- Verify each target event file exists.
- Verify each target event file links back to the source character page.

This prevents one-way navigation such as:
  characters/贾宝玉.md -> events/宝玉挨打.md
without the corresponding event page mentioning/linking 贾宝玉.
"""
from __future__ import annotations

from pathlib import Path
import argparse
import json
import re
import sys

VAULT_PREFIX = "02_Learn/08_book-wikis/红楼梦"
EVENT_LINK_RE = re.compile(r"\[\[(02_Learn/08_book-wikis/红楼梦/events/[^\]|#]+\.md)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
SECTION_RE = re.compile(r"## 主要事件线\n(.*?)(?=\n## |\Z)", re.S)


def normalize_root(path: str) -> Path:
    root = Path(path).expanduser().resolve()
    if not (root / "characters").exists() or not (root / "events").exists():
        raise FileNotFoundError(f"wiki root must contain characters/ and events/: {root}")
    return root


def relative_to_vault_target(root: Path, target: str) -> Path:
    """Resolve a vault-absolute wikilink target against the wiki root.

    Target format is expected to start with VAULT_PREFIX, for example:
    02_Learn/08_book-wikis/红楼梦/events/宝玉挨打.md
    """
    prefix = f"{VAULT_PREFIX}/"
    if not target.startswith(prefix):
        return root / target
    return root / target[len(prefix):]


def check_reverse_links(root: Path) -> dict:
    gaps: list[dict] = []
    scanned_characters = 0
    scanned_event_links = 0
    scanned_sections = 0

    for char_path in sorted((root / "characters").glob("*.md"), key=lambda p: p.stem):
        text = char_path.read_text(encoding="utf-8")
        if "## 主要事件线" not in text:
            continue
        scanned_characters += 1
        section_match = SECTION_RE.search(text)
        if not section_match:
            gaps.append({
                "character": str(char_path.relative_to(root)),
                "event_target": "(section)",
                "reason": "cannot_extract_major_event_line_section",
            })
            continue
        scanned_sections += 1
        section = section_match.group(1)
        char_name = char_path.stem
        reverse_needles = [
            f"/characters/{char_name}.md",
            f"characters/{char_name}.md",
        ]
        for target in EVENT_LINK_RE.findall(section):
            scanned_event_links += 1
            event_path = relative_to_vault_target(root, target)
            if not event_path.exists():
                gaps.append({
                    "character": str(char_path.relative_to(root)),
                    "event_target": target,
                    "reason": "target_missing",
                })
                continue
            event_text = event_path.read_text(encoding="utf-8")
            if not any(needle in event_text for needle in reverse_needles):
                gaps.append({
                    "character": str(char_path.relative_to(root)),
                    "event_target": target,
                    "reason": f"missing_reverse:{char_name}",
                })

    return {
        "scanned_characters": scanned_characters,
        "scanned_sections": scanned_sections,
        "scanned_event_links": scanned_event_links,
        "gaps": gaps,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Wiki root directory")
    parser.add_argument("--json-output", help="Optional JSON output path")
    parser.add_argument("--strict-current", action="store_true", help="Assert the current curated reverse-link baseline")
    args = parser.parse_args()

    root = normalize_root(args.root)
    result = check_reverse_links(root)
    gaps = result["gaps"]

    print(
        "CHARACTER_EVENT_REVERSE_LINK_CHECK: "
        f"scanned_characters={result['scanned_characters']} "
        f"scanned_event_links={result['scanned_event_links']} "
        f"gaps={len(gaps)}"
    )
    for gap in gaps:
        print(f"- {gap['event_target']} <- {gap['character']}: {gap['reason']}")

    if args.json_output:
        Path(args.json_output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.strict_current:
        expected = (59, 363, 0)
        actual = (result["scanned_characters"], result["scanned_event_links"], len(gaps))
        if actual != expected:
            print(f"STRICT_CURRENT_MISMATCH expected={expected} actual={actual}", file=sys.stderr)
            return 1
    return 1 if gaps else 0


if __name__ == "__main__":
    raise SystemExit(main())
