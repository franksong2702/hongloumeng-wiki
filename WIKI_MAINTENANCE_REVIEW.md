---
title: 红楼梦 Wiki 维护审查与收尾报告
created: 2026-07-08
updated: 2026-07-10
status: final
type: maintenance-review
owner: 学夫
handoff_target: future-agent
book: 红楼梦
tags: [hongloumeng, maintenance, health-check, phase-3q]
---

# 红楼梦 Wiki 维护审查与收尾报告

> 本文档是 `[[02_Learn/08_book-wikis/红楼梦]]` 本轮维护的收尾交接。
> 2026-07-08 的初始审查认为：这个 Wiki 已有结构基础，但缺少可重复运行的健康检查与分阶段维护机制。
> 截至 2026-07-10 09:08，本轮已经完成机制建设、机械修复、链接规范、内容补强、人物事件线与首个小专题端到端抽查。

## 1. 一句话结论

当前红楼梦 Wiki 已经从“靠人工感觉维护”变成“可用脚本验证的分层维护系统”：

- `scripts/wiki_health_check.py --strict` 返回 `exit 0`；
- 当前健康检查为 `ERROR 0 / WARN 0`；
- wikilink、正文锚点引用、事件页正文锚点覆盖、薄页检查均无发现项；
- `raw/` 仍按既定策略作为未跟踪原始文本层保留，不纳入本轮提交。

## 2. 当前健康状态

本节以 2026-07-10 09:08 重新运行的本地健康检查为准。

| 项目 | 当前值 |
|---|---:|
| 成品 Wiki Markdown | 822 |
| raw/ 原始文本 Markdown | 121 |
| 成品+raw 管理口径 | 943 |
| 维护/审查 Markdown | 4 |
| 全部 Markdown | 947 |
| ERROR | 0 |
| WARN | 0 |

关键检查项：

| 检查项 | 结果 |
|---|---:|
| wikilinks | ok=13439, scanned=13439 |
| source_anchor_references | ok=861, scanned=861 |
| event_source_anchor_coverage | ok=176, scanned=176 |
| source_anchors | duplicate=0, body=283 |
| chapter_key_event_links | ok=202, suspect=0 |
| thin_pages | scanned=551，无 thin WARN |

证据文件：`/tmp/hongloumeng_baoyu_beating_precommit_health.md`。

## 3. 本轮维护完成范围

### Phase 0 / Phase 1：维护机制与机械修复

代表 commit：`5c5bf28 建立红楼梦 Wiki 维护机制并完成 Phase 1 机械修复`

完成内容：

- 建立 `[[MAINTENANCE.md]]`；
- 建立 `scripts/wiki_health_check.py`；
- 明确成品层、raw 层、维护文档的统计口径；
- 处理低风险机械问题；
- 确认 `raw/` 本轮不纳入 Git、不移动、不删除。

### Phase 2：链接系统修复

代表 commit：`a597edc Normalize Hongloumeng wiki links`

完成内容：

- 用 alias map 处理简称链接；
- 把短名链接规范为文件级可点击链接，例如 `[[characters/贾宝玉.md|宝玉]]`；
- 让 wikilink 检查从“看起来可能没问题”变成脚本可验证。

### Phase 3A：内容审查分诊

代表 commit：`d3346e5 Add Phase 3A content review triage`

完成内容：

- 生成 `[[PHASE_3A_CONTENT_REVIEW.md]]`；
- 将脚本发现的薄页从机械 WARN 转成人类可判断的 P0/P1/P2 队列；
- 明确 Phase 3 后续不做全库泛泛扩写，而是按类型和价值分批补强。

### Phase 3B / 3C：解释层与人物页补强

代表 commit：

- `3cc939e Expand Phase 3B core explanatory pages`
- `a18da3a Complete Phase 3B explanatory page pass`
- `8b2f8a0 Expand Phase 3C high-link character pages`
- `afa85f3 Expand Phase 3C second character batch`
- `f2234c7 Expand Phase 3C selected character pages`
- `ae9d6ee Finish Phase 3C selected character pass`
- `e221b42 Strengthen remaining thin character pages`

完成内容：

- 补强核心概念、红学、背景等解释层页面；
- 补强高入链人物页和剩余薄人物页；
- 人物页补强坚持“身份—关系—关键事件—叙事功能—相关页面”的 Wiki 导航逻辑。

### Phase 3D 到 3N：事件页、正文锚点与内容页补强

代表 commit：

- `8cff822 Add Phase 3D event localization pass`
- `20a3d8c Fix Phase 3D event chapter inbounds`
- `9a1e976 Audit chapter key event links`
- `9e142c4 Add chapter key event link health check`
- `5524a25 Add Phase 3D event entries`
- `688768d Add Phase 3D early literary events`
- `af3b564 Add Phase 3D mid-story event entries`
- `ba81475 Add Phase 3D high-value event entries`
- `689ca76 Add Phase 3D late-story event entries`
- `253a123 Strengthen Phase 3D closing event pages`
- `38f1c24 Strengthen late marriage tragedy event pages`
- `a6546a5 Strengthen high-value event pages`
- `2157e7d Strengthen early core event pages`
- `2cde3ef Strengthen early social order event pages`
- `58cfc2e Strengthen mid-story emotional event pages`
- `73a55f0 Strengthen late collapse event pages`
- `f903412 Strengthen prophecy and closure event pages`
- `102058b Strengthen lyrical and garden event pages`
- `5897ced Strengthen conflict and revenge event pages`
- `bf2f5d7 Resolve remaining thin event pages`

完成内容：

- 持续补强事件页；
- 将事件页的“相关回目”从泛泛列举改为解释上下文；
- 强化“原文锚点”机制，让事件页能跳到正文现场；
- 处理章节页关键事件链接与事件页回目声明之间的对应关系。

### 正文锚点专项

代表 commit：

- `d98c639 Fix source anchor body placement checks`
- `ff5bac9 Add source anchor coverage checks`
- `a99433d Fix source anchor targets`

完成内容：

- 检查 block anchor 是否真正落在正文段落，而不是阅读提示或 frontmatter；
- 增加事件页正文锚点覆盖检查；
- 修复缺失或错误的正文锚点引用。

### Phase 3O / 3P：剩余薄页收尾

代表 commit：

- `98dec9c Strengthen thin location pages`
- `d6f64c8 Strengthen thin motif pages`
- `f3291a1 Strengthen thin output guides`
- `0d94d99 Strengthen thin poem pages`

完成内容：

- 清理剩余地点、母题、输出产品、诗词薄页；
- 重点补“正文定位 / 阅读入口 / 对读路线”，避免为清 WARN 写空泛赏析；
- 最终将 `thin_page_by_type` WARN 清零。

## 4. 当前 Git 状态说明

进入 Phase 3Q 前的状态：

```text
?? WIKI_MAINTENANCE_REVIEW.md
?? raw/
```

解释：

- `WIKI_MAINTENANCE_REVIEW.md`：原为未跟踪的初始审查草稿；本文件已更新为当前收尾报告，建议作为维护文档纳入 Git。
- `raw/`：仍是未跟踪原始文本层。本轮策略是不纳入 Git、不移动、不删除、不新增 `.gitignore`。未来如要处理，应单独开一阶段讨论。

## 5. 后续维护方法

后续 Agent 接手时，优先按以下顺序工作：

1. 先运行健康检查：

   ```bash
   python3 scripts/wiki_health_check.py --strict --output /tmp/hongloumeng_wiki_health_check.txt
   ```

2. 如果健康检查仍为 `ERROR 0 / WARN 0`，不要为了“继续优化”而批量改正文。
3. 如需继续维护，建议只做有明确目标的小切片，例如：
   - 版本号 / README / MkDocs 发布文档对齐；
   - 某一条人物线或事件线的人工精读；
   - `raw/` 是否纳入 Git 的单独决策；
   - GitHub Pages / MkDocs 构建验证。
4. 不要把 `raw/` 与成品 Wiki 页面混在同一统计口径里。
5. 任何新改动完成后，都必须留下：验证命令、返回结果、证据路径。

## 6. 给后续 Agent 的可执行提示词

```text
你正在维护 Obsidian vault 中的 `02_Learn/08_book-wikis/红楼梦` Wiki。

当前状态以 `WIKI_MAINTENANCE_REVIEW.md` 和 `MAINTENANCE.md` 为准。不要依赖 2026-07-08 初始审查里的旧数字。

开始前必须运行：
python3 scripts/wiki_health_check.py --strict --output /tmp/hongloumeng_wiki_health_check.txt

如果结果是 ERROR 0 / WARN 0，请不要做全库“顺手优化”。只在用户明确指定的小范围内修改。

特别注意：
- `raw/` 是未跟踪原始文本层，本轮维护策略是不纳入 Git、不移动、不删除。
- 事件页必须尽量提供 `texts/simplified/第xxx回.md#^hlm-*` 原文锚点。
- 诗词、人物、事件、地点页的补强目标是提升导航能力，不是写泛泛赏析。
- 提交前必须运行 `python3 scripts/wiki_health_check.py --strict` 和 `git diff --check`。
```

## 7. 历史起点说明

2026-07-08 的初始审查曾记录：

```text
成品 Markdown：765
raw Markdown：121
全部 Markdown：886
Git 状态：M README.md；?? raw/
```

这些数字只代表维护开始前的历史快照。经过本轮新增维护机制、内容补强、事件页和原文层修复后，当前数字已经变化。后续维护必须以重新运行脚本为准。

## 8. 初见审查提醒

一个谨慎维护者可能会质疑：

> 现在 `ERROR 0 / WARN 0`，是否意味着这个 Wiki 内容已经“文学上完美”？

不是。健康检查只证明结构、链接、锚点、薄页阈值这些可机械验证项已经达标；它不能替代红学判断，也不能证明每一页的观点都已经最优。当前可确认的是：Wiki 已经具备稳定维护机制，后续可以在这个机制上做人工精读，而不是继续靠脚本扫薄页大规模补内容。

## 9. 小专题端到端抽查机制

健康检查归零后，不再做全库泛泛扩写；后续内容维护以一个“小专题链路”为单位抽查。机械边界如下：

1. **人物入口**：核心参与人物页应能进入事件页；只有事件确实构成人物主线时，才加入 `## 主要事件线`。
2. **事件解释**：事件页必须说明哪一回是前因、哪一回真正发生、哪一回写直接余波，不能只并列回目编号。
3. **正文现场**：关键因果、事件本身和重要后果应各有语义明确的 `^hlm-*` 正文锚点；锚点标签必须与实际落点相符。
4. **章节回返**：相关章节导读应能回到事件页，并为关键场景提供原文定位。
5. **横向解释**：事件页应接到必要的概念或红学页，但不为增加链接数量而扩写外围页面。
6. **维护闸门**：修改后运行健康检查、人物事件线统计、人物—事件反链检查和 `git diff --check`。

首个样例为[[02_Learn/08_book-wikis/红楼梦/events/宝玉挨打.md|宝玉挨打]]：链路按“第028回远因—第032回近因—第033回本事—第034回余波”组织，并把蒋玉菡、贾母、林黛玉等必要人物入口接回事件现场。后续专题可复用同一套检查顺序，但不能机械复制相同人物数量或回目数量。
