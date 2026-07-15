#!/usr/bin/env python3
"""Focused regression tests for frontmatter source path boundaries."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import wiki_health_check as health


class FrontmatterSourceBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "wiki"
        self.root.mkdir()

    def page_with_source(self, root: Path, relative_path: str, source: str) -> Path:
        page = root / relative_path
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(
            "---\n"
            "title: Fixture\n"
            "type: guide\n"
            "sources:\n"
            f"  - {source}\n"
            "---\n\n"
            "Fixture\n",
            encoding="utf-8",
        )
        return page

    def check(self, root: Path, page: Path) -> tuple[list[health.Finding], dict[str, int]]:
        return health.check_frontmatter_sources(root, [page])

    def assert_error(self, findings: list[health.Finding], category: str) -> None:
        self.assertEqual([finding.category for finding in findings], [category])

    def test_wiki_root_local_path_is_allowed(self) -> None:
        source = self.root / "references" / "legal.pdf"
        source.parent.mkdir()
        source.write_bytes(b"fixture")
        page = self.page_with_source(self.root, "page.md", "references/legal.pdf")

        findings, stats = self.check(self.root, page)

        self.assertEqual(findings, [])
        self.assertEqual(stats.get("local_ok"), 1)

    def test_vault_root_local_path_is_allowed_in_vault_mode(self) -> None:
        vault = self.base / "vault"
        root = vault / "02_Learn" / "08_book-wikis" / "红楼梦"
        root.mkdir(parents=True)
        source = vault / "02_Learn" / "shared.md"
        source.write_text("fixture\n", encoding="utf-8")
        page = self.page_with_source(root, "page.md", "02_Learn/shared.md")

        findings, stats = self.check(root, page)

        self.assertEqual(findings, [])
        self.assertEqual(stats.get("local_ok"), 1)

    def test_missing_local_path_keeps_missing_error(self) -> None:
        page = self.page_with_source(self.root, "page.md", "references/missing.pdf")

        findings, stats = self.check(self.root, page)

        self.assert_error(findings, "frontmatter_source_local_missing")
        self.assertEqual(stats.get("local_broken"), 1)

    def test_parent_path_outside_wiki_is_rejected(self) -> None:
        (self.base / "private.md").write_text("private\n", encoding="utf-8")
        page = self.page_with_source(self.root, "page.md", "../private.md")

        findings, stats = self.check(self.root, page)

        self.assert_error(findings, "frontmatter_source_outside_boundary")
        self.assertEqual(stats.get("local_outside_boundary"), 1)
        self.assertEqual(stats.get("local_ok", 0), 0)

    def test_absolute_local_path_is_rejected(self) -> None:
        private = self.base / "private.md"
        private.write_text("private\n", encoding="utf-8")
        absolute_values = (
            private.as_posix(),
            r"C:\private.md",
            r"\\server\share\private.md",
            "~/private.md",
            "file:///private.md",
        )

        for value in absolute_values:
            with self.subTest(value=value):
                page = self.page_with_source(self.root, "page.md", value)
                findings, stats = self.check(self.root, page)

                self.assert_error(findings, "frontmatter_source_absolute_path")
                self.assertEqual(stats.get("local_absolute"), 1)
                self.assertEqual(stats.get("local_ok", 0), 0)

    def test_symlink_target_outside_wiki_is_rejected(self) -> None:
        private = self.base / "private.md"
        private.write_text("private\n", encoding="utf-8")
        (self.root / "linked.md").symlink_to(private)
        page = self.page_with_source(self.root, "page.md", "linked.md")

        findings, stats = self.check(self.root, page)

        self.assert_error(findings, "frontmatter_source_outside_boundary")
        self.assertEqual(stats.get("local_outside_boundary"), 1)
        self.assertEqual(stats.get("local_ok", 0), 0)

    def test_parent_path_that_stays_inside_wiki_is_allowed(self) -> None:
        (self.root / "shared.md").write_text("fixture\n", encoding="utf-8")
        page = self.page_with_source(self.root, "nested/page.md", "../shared.md")

        findings, stats = self.check(self.root, page)

        self.assertEqual(findings, [])
        self.assertEqual(stats.get("local_ok"), 1)


if __name__ == "__main__":
    unittest.main()
