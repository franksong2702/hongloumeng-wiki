---
title: 红楼梦 Wiki 维护机制
created: 2026-07-08
updated: 2026-07-10
type: maintenance-guide
book: 红楼梦
status: active
tags: [hongloumeng, maintenance, health-check, obsidian]
---

# 红楼梦 Wiki 维护机制

> 目标：让 `[[02_Learn/08_book-wikis/红楼梦]]` 的维护从“凭感觉看一遍”变成“先体检、再分批修复、最后留下证据”。

本文是维护入口；审查背景见 `[[WIKI_MAINTENANCE_REVIEW.md]]`。

## 1. 维护原则

1. **先体检，后改正文**：每次维护先运行健康检查，确认问题类型和数量。
2. **分阶段，不混批**：脚本、机械修复、链接系统、内容补强分开做。
3. **只修本阶段问题**：不要在修链接时顺手改文风，不要在补 frontmatter 时顺手重写人物页。
4. **统计口径先写清**：`raw/` 原始文本层和成品 Wiki 层分开计数。
5. **每次完成留三件套**：

```text
验证命令: <原样命令>
返回结果: <exit code / 关键输出行>
证据路径: <日志/截图/报告文件/PR 链接>
```

## 2. 统计口径

后续报告统一使用四个口径：

| 口径 | 含义 |
|---|---|
| 成品 Wiki Markdown | 可作为 Wiki 正文、索引、输出产品、维护元文档之外的正式页面；不含 `raw/`、`MAINTENANCE.md`、`WIKI_MAINTENANCE_REVIEW.md`、`scripts/`。 |
| raw Markdown | `raw/` 下的原始文本层，作为来源或备份层单独统计。 |
| 成品+raw 管理口径 | 成品 Wiki Markdown + raw Markdown。 |
| 维护/审查 Markdown | `MAINTENANCE.md`、`WIKI_MAINTENANCE_REVIEW.md` 等维护过程文件，不混入成品总数。 |

这样可以保留原先“成品层 765”的说法，同时把 `raw/` 的 121 个 Markdown 说清楚。

## 3. 一键健康检查

在 Wiki 根目录运行：

```bash
python3 scripts/wiki_health_check.py
```

如需把报告保存为证据：

```bash
python3 scripts/wiki_health_check.py --output /tmp/hongloumeng_wiki_health_report.txt
```

如需作为发布前闸门：

```bash
python3 scripts/wiki_health_check.py --strict
```

说明：

- 默认模式只负责生成报告，发现问题也返回 `exit 0`，适合当前 Phase 0。
- `--strict` 模式发现 `ERROR` 会返回 `exit 1`，适合后续 CI 或发布前检查。
- 脚本不会修改正文；只有显式传入 `--output` 时才会写报告文件。

## 4. 健康检查覆盖范围

`scripts/wiki_health_check.py` 当前覆盖：

1. 成品 Markdown、`raw/` Markdown、维护 Markdown、全部 Markdown 的数量；
2. 各目录 Markdown 数量；
3. frontmatter 必填字段：`title`、`created`、`updated`、`type`、`book`、`status`；
4. Obsidian wikilink 是否可解析；
5. 短名 alias 是否需要规范化；
6. 本地 Markdown 链接是否有效；
7. 占位词 / 禁止句式扫描，并排除元文档、模板和 `raw/`；
8. 按 `type` 分类的薄页检查；
9. README / index / ROADMAP / AGENTS / 输出总评中的数量自描述是否漂移。

## 5. 静态站严格构建闸门

健康检查验证的是 Obsidian 源文件；发布前还要验证“转换成普通 Markdown 后，静态站的链接是否仍可用”。在 Wiki 根目录运行：

```bash
python3 scripts/mkdocs_build_check.py
```

该脚本会依次：

1. 运行 `scripts/build_mkdocs.py`，在 `_mkdocs_build/docs/` 生成副本；
2. 将 vault 根路径、短名链接、图片链接和 `#^block-anchor` 转成 MkDocs 可识别的相对链接；
3. 执行 `mkdocs build --strict`；只要严格构建非零退出，整条命令就非零退出；
4. 将转换与构建输出写入 `_mkdocs_build/mkdocs-strict-build.log`。

边界：`raw/`、模板和维护文档不属于读者静态站，因此不参与这项构建。历史 `#L33` 这类行号坐标在静态站中没有稳定锚点，会保留“跳到原文页”的链接而不伪造锚点；正文精确定位仍应使用 `#^hlm-...` block anchor。

## 6. 读者发布日志

[[log.md]] 不是逐条复制 Git commit 的开发日志，而是面向读者的发布记录。以下变化必须在同一发布批次中更新 `log.md`：

1. 新增或重组读者的主要阅读路径；
2. 大批内容补强、原文定位规则或跨页关系发生变化；
3. MkDocs、导航、搜索或 GitHub Pages 的可见行为发生变化。

`scripts/wiki_health_check.py --strict` 会比较最新日志日期、Git 中的读者可见变动，以及当前待提交改动。三者不同步时会报告 `release_log_*` ERROR，避免日志再次停在旧版本。

## 7. 当前 alias map 起点

Phase 2 前不要盲目批量改短名链接。先用健康检查报告确认短名数量，再按 alias map 统一转换。

初始 alias map：

| 短名 | 规范目标 |
|---|---|
| 宝玉 | `characters/贾宝玉.md` |
| 黛玉 | `characters/林黛玉.md` |
| 宝钗 | `characters/薛宝钗.md` |
| 凤姐 | `characters/王熙凤.md` |
| 探春 | `characters/贾探春.md` |
| 惜春 | `characters/贾惜春.md` |
| 迎春 | `characters/贾迎春.md` |
| 可卿 | `characters/秦可卿.md` |

建议目标格式：

```md
[[characters/贾宝玉.md|宝玉]]
```

## 8. 维护阶段

### Phase 0：只读维护基础设施

目标：建立检查能力，不改正文。

交付物：

- `scripts/wiki_health_check.py`
- `MAINTENANCE.md`
- 一份健康检查报告

### Phase 1：低风险机械修复

范围：

1. 修复 README 中错误的本地相对链接；
2. 明确 `765 / 886 / raw 121` 的统计口径；
3. 修复 README / index / outputs / ROADMAP 中数量不一致；
4. 补齐缺失的 `updated` frontmatter；
5. 明确 `raw/` 是否纳入 Git。

### Phase 2：链接系统修复

范围：

1. 固化 alias map；
2. 把短名链接转成文件级可点击链接；
3. 再运行 `--strict` 检查断链。

### Phase 3：内容质量补强

范围：

1. 按 `character/event/location/concept/redology` 等 type 分类处理薄页；
2. 优先补 sources、关系网络、章节抓手和主题分析；
3. 不做全库统一文风清洗。

## 9. Git 与发布边界

维护前先查看：

```bash
git status --short
```

当前已知需要特别注意：

- `README.md` 可能已有未归属改动；
- `raw/` 可能是未跟踪状态；
- 当前策略（2026-07-08 Phase 1B-C）：`raw/` 仅作为当前存在的原始文本层在文档和健康检查中单独统计；本轮不纳入 Git、不新增 `.gitignore`、不移动/删除 `raw/`；
- 未确认前不要部署 GitHub Pages，不要启用自动任务。

## 10. 完成报告模板

每阶段完成后使用：

```text
已完成:
- <具体文件/脚本/报告>

验证命令: <原样命令>
返回结果: <exit code / 关键输出行>
证据路径: <报告文件或日志路径>

初见审查:
- 质疑: <一个多疑维护者会问的问题>
- 回应: <为什么当前处理仍然成立 / 哪些留到下一阶段>

确信度:
- 高/中/低；如果中或低，说明需要用户确认什么。
```
