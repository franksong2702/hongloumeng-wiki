#!/usr/bin/env python3
"""检查成品 Wiki 中的外部 HTTP(S) 来源。

404/410 视为确定断链；403、429、5xx、TLS 和超时只列为需复核，
避免受反爬或短暂网络波动影响发布。
"""

from __future__ import annotations

import argparse
import json
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


URL_RE = re.compile(r"https?://[^\s)>\]\"']+")
SKIP_DIRS = {".git", "_mkdocs_build", "raw", "site", "docs"}
BROKEN_STATUS = {404, 410}
USER_AGENT = "Mozilla/5.0 (compatible; HongloumengWikiSourceAudit/1.0)"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="检查 Wiki 外部来源链接")
    parser.add_argument("--root", help="Wiki 根目录")
    parser.add_argument("--output", help="JSON 报告路径")
    parser.add_argument("--strict", action="store_true", help="发现 404/410 时返回 exit 1")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--timeout", type=float, default=12.0)
    return parser.parse_args()


def root_from_args(args: argparse.Namespace) -> Path:
    if args.root:
        return Path(args.root).resolve()
    return Path(__file__).resolve().parents[1]


def collect_urls(root: Path) -> dict[str, set[str]]:
    urls: dict[str, set[str]] = defaultdict(set)
    for path in root.rglob("*.md"):
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for raw in URL_RE.findall(text):
            url = raw.rstrip(".,;:，。；：")
            urls[url].add(rel.as_posix())
    return urls


def check_one(url: str, timeout: float) -> dict[str, object]:
    parts = urllib.parse.urlsplit(url)
    request_url = urllib.parse.urlunsplit(
        (
            parts.scheme,
            parts.netloc.encode("idna").decode("ascii"),
            urllib.parse.quote(parts.path, safe="/%:@"),
            urllib.parse.quote_plus(parts.query, safe="=&%:@/"),
            urllib.parse.quote(parts.fragment, safe=""),
        )
    )
    request = urllib.request.Request(
        request_url,
        headers={"User-Agent": USER_AGENT, "Range": "bytes=0-8191"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=ssl.create_default_context()) as response:
            response.read(1024)
            return {
                "url": url,
                "status": response.status,
                "final_url": response.geturl(),
                "error": "",
            }
    except urllib.error.HTTPError as exc:
        return {"url": url, "status": exc.code, "final_url": exc.geturl(), "error": ""}
    except Exception as exc:  # 网络/TLS 错误只作人工复核
        return {
            "url": url,
            "status": None,
            "final_url": "",
            "error": f"{type(exc).__name__}: {str(exc)[:240]}",
        }


def classify(row: dict[str, object]) -> str:
    status = row["status"]
    if status is None:
        return "review"
    if status in BROKEN_STATUS:
        return "broken"
    if 200 <= int(status) < 400:
        return "ok"
    return "review"


def main() -> int:
    args = parse_args()
    root = root_from_args(args)
    url_files = collect_urls(root)
    rows: list[dict[str, object]] = []

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {executor.submit(check_one, url, args.timeout): url for url in url_files}
        for future in as_completed(futures):
            row = future.result()
            row["classification"] = classify(row)
            row["files"] = sorted(url_files[str(row["url"])])
            rows.append(row)

    rows.sort(key=lambda row: (str(row["classification"]), str(row["url"])))
    summary = Counter(str(row["classification"]) for row in rows)
    report = {
        "root": str(root),
        "unique_urls": len(rows),
        "summary": dict(summary),
        "results": rows,
    }

    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        "EXTERNAL_LINK_CHECK: "
        f"unique={len(rows)} ok={summary['ok']} review={summary['review']} broken={summary['broken']}"
    )
    for row in rows:
        if row["classification"] == "ok":
            continue
        detail = row["status"] if row["status"] is not None else row["error"]
        print(f"- {str(row['classification']).upper()} {detail} {row['url']} files={','.join(row['files'])}")

    if args.strict and summary["broken"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
