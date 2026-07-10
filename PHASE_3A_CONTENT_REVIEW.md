---
title: 红楼梦 Wiki Phase 3A 内容审查分诊
created: 2026-07-08
updated: 2026-07-10
type: maintenance-report
book: 红楼梦
status: historical-snapshot
tags: [hongloumeng, maintenance, content-review, phase-3a]
---

# 红楼梦 Wiki Phase 3A 内容审查分诊

> **历史快照，不是当前待办。** 本文记录 2026-07-08 的薄页分诊输入；其 P0/P1/P2 队列已在后续 Phase 3B—3P 中完成处理。当前结构与内容状态应以 [[02_Learn/08_book-wikis/红楼梦/WIKI_MAINTENANCE_REVIEW.md]]、[[02_Learn/08_book-wikis/红楼梦/outputs/人物事件线剩余人物审查.md]] 和最新健康检查为准。

- 生成时间：2026-07-08 10:50:30
- 输入报告：`/tmp/hongloumeng_wiki_health_phase3a_input.txt`
- 依据脚本：`scripts/wiki_health_check.py`
- 范围：只做内容分诊，不改任何正文页。

## 1. 结论先说

Phase 3A 的目标不是“把 241 个 WARN 全部清零”，而是把脚本发现的薄页转成人可以判断的编辑队列。

- 结构性错误：0。
- 脚本指出的内容候选：241 个 `thin_page_by_type`。
- 本报告将 241 个候选分成：P0 高优先审查、P1 二线补强、P2 保留短页候选。
- 下一步 Phase 3B 不建议全库扩写，建议从 P0 中再选一个小切片试点。

## 2. 分诊结果总览

### 2.1 按优先级

| 优先级 | 数量 | 含义 |
|---|---:|---|
| P0 | 61 | 高入链 / 核心类型 / 缺口明显，优先进入人工内容审查与试点扩写。 |
| P1 | 163 | 有补强价值，但应等 P0 风格稳定后批量处理。 |
| P2 | 17 | 低入链或次要页面，短页可能合理，暂不建议为清 WARN 而扩写。 |
| 合计 | 241 | 全部来自 `thin_page_by_type` WARN。 |

### 2.2 按页面类型

| type | 薄页数 | P0 | P1 | P2 |
|---|---:|---:|---:|---:|
| background | 4 | 2 | 2 | 0 |
| character | 76 | 12 | 53 | 11 |
| concept | 18 | 13 | 5 | 0 |
| event | 108 | 12 | 90 | 6 |
| location | 15 | 6 | 9 | 0 |
| motif | 5 | 5 | 0 | 0 |
| output | 2 | 1 | 1 | 0 |
| poem | 5 | 3 | 2 | 0 |
| redology | 8 | 7 | 1 | 0 |

## 3. 分诊规则

脚本只给出“行数低于阈值”，本报告额外加入两个只读信号：

1. **入链数**：有多少已解析 wikilink 指向该页；入链越高，页面越像 Wiki 枢纽。
2. **缺口**：`threshold - nonblank_lines`；缺口越大，越像骨架页。

具体规则：

| type | P0 规则 | P1 规则 | P2 规则 |
|---|---|---|---|
| character | 入链 ≥ 30 | 入链 ≥ 10 或缺口 ≥ 10 | 其余 |
| event | 入链 ≥ 10 | 入链 ≥ 5 或缺口 ≥ 12 | 其余 |
| concept | 入链 ≥ 25 或缺口 ≥ 8 | 其余 | 暂无 |
| location | 入链 ≥ 10 | 入链 ≥ 4 或缺口 ≥ 10 | 其余 |
| redology | 入链 ≥ 20 或缺口 ≥ 10 | 其余 | 暂无 |
| background | 入链 ≥ 3 或缺口 ≥ 10 | 其余 | 暂无 |
| poem | 入链 ≥ 10 或缺口 ≥ 5 | 其余 | 暂无 |
| motif | 入链 ≥ 6 或缺口 ≥ 5 | 其余 | 暂无 |
| output | 缺口 ≥ 8 | 其余 | 暂无 |

> 注意：P0 也不是“立刻扩写”的命令，只是 Phase 3B 最该先看的队列。

## 4. Phase 3B 推荐切片

我建议不要一次处理 61 个 P0。更稳的切法是：

1. **概念 / 红学 / 背景优先**：这些页是解释层，补好后能反哺人物、事件和输出产品。
2. **再做高入链人物**：例如平儿、贾雨村、贾琏、李纨、尤氏等。
3. **最后做关键事件**：例如海棠诗社、香菱学诗、鸳鸯拒婚、葫芦案等。

建议 Phase 3B 第一批控制在 10-20 页，完成后再决定是否扩大。

## 5. P0 高优先审查队列

| type | 页面 | 行数 | 阈值 | 缺口 | 入链 | 当前 status | 建议动作 |
|---|---|---:|---:|---:|---:|---|---|
| background | [[background/科举与仕途.md]] | 43 | 50 | 7 | 5 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| background | [[background/清代家族制度.md]] | 36 | 50 | 14 | 3 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| character | [[characters/平儿.md]] | 18 | 25 | 7 | 92 | `curated-v2` | 优先扩写：补人物小传、关系、关键章节 |
| character | [[characters/贾雨村.md]] | 18 | 25 | 7 | 77 | `curated-v2` | 优先扩写：补人物小传、关系、关键章节 |
| character | [[characters/贾琏.md]] | 21 | 25 | 4 | 53 | `curated-v2` | 优先扩写：补人物小传、关系、关键章节 |
| character | [[characters/李纨.md]] | 24 | 25 | 1 | 49 | `curated-v3` | 优先扩写：补人物小传、关系、关键章节 |
| character | [[characters/尤氏.md]] | 24 | 25 | 1 | 44 | `curated-v2` | 优先扩写：补人物小传、关系、关键章节 |
| character | [[characters/薛蟠.md]] | 20 | 25 | 5 | 40 | `curated-v2` | 优先扩写：补人物小传、关系、关键章节 |
| character | [[characters/甄士隐.md]] | 21 | 25 | 4 | 38 | `curated-v2` | 优先扩写：补人物小传、关系、关键章节 |
| character | [[characters/鸳鸯.md]] | 17 | 25 | 8 | 35 | `curated-v2` | 优先扩写：补人物小传、关系、关键章节 |
| character | [[characters/薛姨妈.md]] | 19 | 25 | 6 | 35 | `curated-v2` | 优先扩写：补人物小传、关系、关键章节 |
| character | [[characters/紫鹃.md]] | 20 | 25 | 5 | 35 | `curated-v2` | 优先扩写：补人物小传、关系、关键章节 |
| character | [[characters/贾赦.md]] | 19 | 25 | 6 | 32 | `curated-v2` | 优先扩写：补人物小传、关系、关键章节 |
| character | [[characters/贾惜春.md]] | 23 | 25 | 2 | 32 | `curated-v3` | 优先扩写：补人物小传、关系、关键章节 |
| concept | [[concepts/佛道.md]] | 23 | 30 | 7 | 117 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| concept | [[concepts/奴仆制度.md]] | 28 | 30 | 2 | 107 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| concept | [[concepts/空.md]] | 29 | 30 | 1 | 84 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| concept | [[concepts/真假.md]] | 28 | 30 | 2 | 82 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| concept | [[concepts/疾病.md]] | 25 | 30 | 5 | 75 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| concept | [[concepts/科举仕途.md]] | 24 | 30 | 6 | 64 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| concept | [[concepts/梦.md]] | 29 | 30 | 1 | 55 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| concept | [[concepts/金玉良缘.md]] | 26 | 30 | 4 | 49 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| concept | [[concepts/护官符.md]] | 21 | 30 | 9 | 37 | `curated-v3` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| concept | [[concepts/考证派.md]] | 27 | 30 | 3 | 28 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| concept | [[concepts/木石前盟.md]] | 24 | 30 | 6 | 26 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| concept | [[concepts/门第.md]] | 17 | 30 | 13 | 13 | `curated-v1` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| concept | [[concepts/功名.md]] | 17 | 30 | 13 | 9 | `curated-v1` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| event | [[events/海棠诗社.md]] | 22 | 25 | 3 | 18 | `curated-v3` | 优先扩写：补事件经过、叙事功能、相关章节 |
| event | [[events/香菱学诗.md]] | 17 | 25 | 8 | 16 | `curated-v3` | 优先扩写：补事件经过、叙事功能、相关章节 |
| event | [[events/鸳鸯拒婚.md]] | 18 | 25 | 7 | 16 | `curated-v3` | 优先扩写：补事件经过、叙事功能、相关章节 |
| event | [[events/葫芦案.md]] | 21 | 25 | 4 | 16 | `curated-v3` | 优先扩写：补事件经过、叙事功能、相关章节 |
| event | [[events/芳官出家.md]] | 12 | 25 | 13 | 13 | `curated-v2` | 优先扩写：补事件经过、叙事功能、相关章节 |
| event | [[events/宝黛诉肺腑.md]] | 11 | 25 | 14 | 12 | `curated-v2` | 优先扩写：补事件经过、叙事功能、相关章节 |
| event | [[events/秦可卿之死.md]] | 24 | 25 | 1 | 12 | `curated-v3` | 优先扩写：补事件经过、叙事功能、相关章节 |
| event | [[events/贾雨村起复.md]] | 12 | 25 | 13 | 11 | `curated-v2` | 优先扩写：补事件经过、叙事功能、相关章节 |
| event | [[events/宝玉梦游太虚幻境.md]] | 23 | 25 | 2 | 11 | `curated-v3` | 优先扩写：补事件经过、叙事功能、相关章节 |
| event | [[events/刘姥姥一进荣国府.md]] | 24 | 25 | 1 | 11 | `curated-v3` | 优先扩写：补事件经过、叙事功能、相关章节 |
| event | [[events/宝玉出家.md]] | 24 | 25 | 1 | 11 | `curated-v3` | 优先扩写：补事件经过、叙事功能、相关章节 |
| event | [[events/甄士隐梦太虚.md]] | 23 | 25 | 2 | 10 | `curated-v3` | 优先扩写：补事件经过、叙事功能、相关章节 |
| location | [[locations/蘅芜苑.md]] | 23 | 25 | 2 | 26 | `curated-v2` | 优先扩写：补空间功能、居住者/事件、章节抓手 |
| location | [[locations/稻香村.md]] | 23 | 25 | 2 | 24 | `curated-v2` | 优先扩写：补空间功能、居住者/事件、章节抓手 |
| location | [[locations/太虚幻境.md]] | 23 | 25 | 2 | 21 | `curated-v2` | 优先扩写：补空间功能、居住者/事件、章节抓手 |
| location | [[locations/秋爽斋.md]] | 21 | 25 | 4 | 18 | `curated-v3` | 优先扩写：补空间功能、居住者/事件、章节抓手 |
| location | [[locations/铁槛寺.md]] | 24 | 25 | 1 | 13 | `curated-v2` | 优先扩写：补空间功能、居住者/事件、章节抓手 |
| location | [[locations/梨香院.md]] | 21 | 25 | 4 | 11 | `curated-v2` | 优先扩写：补空间功能、居住者/事件、章节抓手 |
| motif | [[motifs-symbols/风月宝鉴.md]] | 18 | 25 | 7 | 7 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| motif | [[motifs-symbols/石头.md]] | 19 | 25 | 6 | 7 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| motif | [[motifs-symbols/芙蓉.md]] | 22 | 25 | 3 | 6 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| motif | [[motifs-symbols/海棠.md]] | 19 | 25 | 6 | 4 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| motif | [[motifs-symbols/金锁.md]] | 19 | 25 | 6 | 2 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| output | [[outputs/海棠诗社图文对照.md]] | 49 | 60 | 11 | 2 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| poem | [[poetry/葬花吟.md]] | 26 | 30 | 4 | 20 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| poem | [[poetry/芙蓉女儿诔.md]] | 27 | 30 | 3 | 15 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| poem | [[poetry/螃蟹咏.md]] | 21 | 30 | 9 | 13 | `curated-v3` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| redology | [[redology/主要争议.md]] | 34 | 45 | 11 | 50 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| redology | [[redology/前八十回与后四十回.md]] | 44 | 45 | 1 | 33 | `curated-v3` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| redology | [[redology/四春与李纨的制度性命运研究综述.md]] | 32 | 45 | 13 | 32 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| redology | [[redology/脂砚斋批语.md]] | 36 | 45 | 9 | 24 | `curated-v3` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| redology | [[redology/贾府被抄与家族终局研究综述.md]] | 42 | 45 | 3 | 24 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| redology | [[redology/甄士隐贾雨村与真假结构研究综述.md]] | 27 | 45 | 18 | 19 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| redology | [[redology/香菱的薄命与诗学研究综述.md]] | 27 | 45 | 18 | 12 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |

## 6. 完整薄页分诊清单

| 优先级 | type | 页面 | 行数 | 阈值 | 缺口 | 入链 | 出链 | 当前 status | 建议动作 |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| P0 | background | [[background/科举与仕途.md]] | 43 | 50 | 7 | 5 | 17 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | background | [[background/清代家族制度.md]] | 36 | 50 | 14 | 3 | 19 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | character | [[characters/平儿.md]] | 18 | 25 | 7 | 92 | 6 | `curated-v2` | 优先扩写：补人物小传、关系、关键章节 |
| P0 | character | [[characters/贾雨村.md]] | 18 | 25 | 7 | 77 | 6 | `curated-v2` | 优先扩写：补人物小传、关系、关键章节 |
| P0 | character | [[characters/贾琏.md]] | 21 | 25 | 4 | 53 | 10 | `curated-v2` | 优先扩写：补人物小传、关系、关键章节 |
| P0 | character | [[characters/李纨.md]] | 24 | 25 | 1 | 49 | 9 | `curated-v3` | 优先扩写：补人物小传、关系、关键章节 |
| P0 | character | [[characters/尤氏.md]] | 24 | 25 | 1 | 44 | 10 | `curated-v2` | 优先扩写：补人物小传、关系、关键章节 |
| P0 | character | [[characters/薛蟠.md]] | 20 | 25 | 5 | 40 | 10 | `curated-v2` | 优先扩写：补人物小传、关系、关键章节 |
| P0 | character | [[characters/甄士隐.md]] | 21 | 25 | 4 | 38 | 7 | `curated-v2` | 优先扩写：补人物小传、关系、关键章节 |
| P0 | character | [[characters/鸳鸯.md]] | 17 | 25 | 8 | 35 | 5 | `curated-v2` | 优先扩写：补人物小传、关系、关键章节 |
| P0 | character | [[characters/薛姨妈.md]] | 19 | 25 | 6 | 35 | 8 | `curated-v2` | 优先扩写：补人物小传、关系、关键章节 |
| P0 | character | [[characters/紫鹃.md]] | 20 | 25 | 5 | 35 | 9 | `curated-v2` | 优先扩写：补人物小传、关系、关键章节 |
| P0 | character | [[characters/贾赦.md]] | 19 | 25 | 6 | 32 | 8 | `curated-v2` | 优先扩写：补人物小传、关系、关键章节 |
| P0 | character | [[characters/贾惜春.md]] | 23 | 25 | 2 | 32 | 8 | `curated-v3` | 优先扩写：补人物小传、关系、关键章节 |
| P0 | concept | [[concepts/佛道.md]] | 23 | 30 | 7 | 117 | 13 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | concept | [[concepts/奴仆制度.md]] | 28 | 30 | 2 | 107 | 14 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | concept | [[concepts/空.md]] | 29 | 30 | 1 | 84 | 15 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | concept | [[concepts/真假.md]] | 28 | 30 | 2 | 82 | 12 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | concept | [[concepts/疾病.md]] | 25 | 30 | 5 | 75 | 13 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | concept | [[concepts/科举仕途.md]] | 24 | 30 | 6 | 64 | 14 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | concept | [[concepts/梦.md]] | 29 | 30 | 1 | 55 | 15 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | concept | [[concepts/金玉良缘.md]] | 26 | 30 | 4 | 49 | 11 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | concept | [[concepts/护官符.md]] | 21 | 30 | 9 | 37 | 7 | `curated-v3` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | concept | [[concepts/考证派.md]] | 27 | 30 | 3 | 28 | 8 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | concept | [[concepts/木石前盟.md]] | 24 | 30 | 6 | 26 | 10 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | concept | [[concepts/门第.md]] | 17 | 30 | 13 | 13 | 4 | `curated-v1` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | concept | [[concepts/功名.md]] | 17 | 30 | 13 | 9 | 4 | `curated-v1` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | event | [[events/海棠诗社.md]] | 22 | 25 | 3 | 18 | 9 | `curated-v3` | 优先扩写：补事件经过、叙事功能、相关章节 |
| P0 | event | [[events/香菱学诗.md]] | 17 | 25 | 8 | 16 | 8 | `curated-v3` | 优先扩写：补事件经过、叙事功能、相关章节 |
| P0 | event | [[events/鸳鸯拒婚.md]] | 18 | 25 | 7 | 16 | 7 | `curated-v3` | 优先扩写：补事件经过、叙事功能、相关章节 |
| P0 | event | [[events/葫芦案.md]] | 21 | 25 | 4 | 16 | 8 | `curated-v3` | 优先扩写：补事件经过、叙事功能、相关章节 |
| P0 | event | [[events/芳官出家.md]] | 12 | 25 | 13 | 13 | 12 | `curated-v2` | 优先扩写：补事件经过、叙事功能、相关章节 |
| P0 | event | [[events/宝黛诉肺腑.md]] | 11 | 25 | 14 | 12 | 4 | `curated-v2` | 优先扩写：补事件经过、叙事功能、相关章节 |
| P0 | event | [[events/秦可卿之死.md]] | 24 | 25 | 1 | 12 | 9 | `curated-v3` | 优先扩写：补事件经过、叙事功能、相关章节 |
| P0 | event | [[events/贾雨村起复.md]] | 12 | 25 | 13 | 11 | 10 | `curated-v2` | 优先扩写：补事件经过、叙事功能、相关章节 |
| P0 | event | [[events/宝玉梦游太虚幻境.md]] | 23 | 25 | 2 | 11 | 9 | `curated-v3` | 优先扩写：补事件经过、叙事功能、相关章节 |
| P0 | event | [[events/刘姥姥一进荣国府.md]] | 24 | 25 | 1 | 11 | 9 | `curated-v3` | 优先扩写：补事件经过、叙事功能、相关章节 |
| P0 | event | [[events/宝玉出家.md]] | 24 | 25 | 1 | 11 | 11 | `curated-v3` | 优先扩写：补事件经过、叙事功能、相关章节 |
| P0 | event | [[events/甄士隐梦太虚.md]] | 23 | 25 | 2 | 10 | 9 | `curated-v3` | 优先扩写：补事件经过、叙事功能、相关章节 |
| P0 | location | [[locations/蘅芜苑.md]] | 23 | 25 | 2 | 26 | 16 | `curated-v2` | 优先扩写：补空间功能、居住者/事件、章节抓手 |
| P0 | location | [[locations/稻香村.md]] | 23 | 25 | 2 | 24 | 16 | `curated-v2` | 优先扩写：补空间功能、居住者/事件、章节抓手 |
| P0 | location | [[locations/太虚幻境.md]] | 23 | 25 | 2 | 21 | 15 | `curated-v2` | 优先扩写：补空间功能、居住者/事件、章节抓手 |
| P0 | location | [[locations/秋爽斋.md]] | 21 | 25 | 4 | 18 | 10 | `curated-v3` | 优先扩写：补空间功能、居住者/事件、章节抓手 |
| P0 | location | [[locations/铁槛寺.md]] | 24 | 25 | 1 | 13 | 17 | `curated-v2` | 优先扩写：补空间功能、居住者/事件、章节抓手 |
| P0 | location | [[locations/梨香院.md]] | 21 | 25 | 4 | 11 | 14 | `curated-v2` | 优先扩写：补空间功能、居住者/事件、章节抓手 |
| P0 | motif | [[motifs-symbols/风月宝鉴.md]] | 18 | 25 | 7 | 7 | 7 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | motif | [[motifs-symbols/石头.md]] | 19 | 25 | 6 | 7 | 8 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | motif | [[motifs-symbols/芙蓉.md]] | 22 | 25 | 3 | 6 | 10 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | motif | [[motifs-symbols/海棠.md]] | 19 | 25 | 6 | 4 | 8 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | motif | [[motifs-symbols/金锁.md]] | 19 | 25 | 6 | 2 | 8 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | output | [[outputs/海棠诗社图文对照.md]] | 49 | 60 | 11 | 2 | 40 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | poem | [[poetry/葬花吟.md]] | 26 | 30 | 4 | 20 | 12 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | poem | [[poetry/芙蓉女儿诔.md]] | 27 | 30 | 3 | 15 | 13 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | poem | [[poetry/螃蟹咏.md]] | 21 | 30 | 9 | 13 | 8 | `curated-v3` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | redology | [[redology/主要争议.md]] | 34 | 45 | 11 | 50 | 27 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | redology | [[redology/前八十回与后四十回.md]] | 44 | 45 | 1 | 33 | 16 | `curated-v3` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | redology | [[redology/四春与李纨的制度性命运研究综述.md]] | 32 | 45 | 13 | 32 | 20 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | redology | [[redology/脂砚斋批语.md]] | 36 | 45 | 9 | 24 | 11 | `curated-v3` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | redology | [[redology/贾府被抄与家族终局研究综述.md]] | 42 | 45 | 3 | 24 | 23 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | redology | [[redology/甄士隐贾雨村与真假结构研究综述.md]] | 27 | 45 | 18 | 19 | 12 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P0 | redology | [[redology/香菱的薄命与诗学研究综述.md]] | 27 | 45 | 18 | 12 | 11 | `curated-v2` | 优先扩写：补定义/文本抓手/研究或赏析层 |
| P1 | background | [[background/佛道思想.md]] | 41 | 50 | 9 | 1 | 13 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | background | [[background/服饰饮食.md]] | 42 | 50 | 8 | 0 | 15 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/邢夫人.md]] | 19 | 25 | 6 | 25 | 8 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/秦钟.md]] | 20 | 25 | 5 | 22 | 9 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/尤二姐.md]] | 19 | 25 | 6 | 19 | 8 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/薛宝琴.md]] | 19 | 25 | 6 | 18 | 8 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/贾蓉.md]] | 24 | 25 | 1 | 18 | 10 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/贾瑞.md]] | 13 | 25 | 12 | 17 | 12 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/邢岫烟.md]] | 18 | 25 | 7 | 17 | 7 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/尤三姐.md]] | 18 | 25 | 7 | 16 | 7 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/金荣.md]] | 15 | 25 | 10 | 14 | 11 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/贾环.md]] | 21 | 25 | 4 | 14 | 10 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/柳湘莲.md]] | 19 | 25 | 6 | 13 | 8 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/小红.md]] | 19 | 25 | 6 | 12 | 8 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/赵姨娘.md]] | 20 | 25 | 5 | 12 | 9 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/一僧一道.md]] | 12 | 25 | 13 | 11 | 14 | `curated-v2` | 待人工判断：神话/设定角色，可短页保留或并入概念线 |
| P1 | character | [[characters/贾蔷.md]] | 15 | 25 | 10 | 11 | 3 | `curated-v1` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/夏金桂.md]] | 17 | 25 | 8 | 11 | 4 | `curated-v1` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/傻大姐.md]] | 13 | 25 | 12 | 8 | 3 | `curated-v1` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/跛足道人.md]] | 13 | 25 | 12 | 8 | 9 | `curated-v2` | 待人工判断：神话/设定角色，可短页保留或并入概念线 |
| P1 | character | [[characters/茗烟.md]] | 15 | 25 | 10 | 7 | 10 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/绛珠仙子.md]] | 12 | 25 | 13 | 6 | 10 | `curated-v2` | 待人工判断：神话/设定角色，可短页保留或并入概念线 |
| P1 | character | [[characters/冯渊.md]] | 14 | 25 | 11 | 6 | 10 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/璜大奶奶.md]] | 14 | 25 | 11 | 6 | 5 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/秋桐.md]] | 15 | 25 | 10 | 6 | 3 | `curated-v1` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/贾敏.md]] | 15 | 25 | 10 | 6 | 16 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/神瑛侍者.md]] | 12 | 25 | 13 | 5 | 9 | `curated-v2` | 待人工判断：神话/设定角色，可短页保留或并入概念线 |
| P1 | character | [[characters/甄宝玉.md]] | 13 | 25 | 12 | 5 | 6 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/冷子兴.md]] | 14 | 25 | 11 | 5 | 9 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/秦业.md]] | 14 | 25 | 11 | 5 | 5 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/李嬷嬷.md]] | 15 | 25 | 10 | 5 | 12 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/林如海.md]] | 15 | 25 | 10 | 5 | 13 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/空空道人.md]] | 12 | 25 | 13 | 4 | 6 | `curated-v2` | 待人工判断：神话/设定角色，可短页保留或并入概念线 |
| P1 | character | [[characters/娇杏.md]] | 14 | 25 | 11 | 4 | 11 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/茜雪.md]] | 14 | 25 | 11 | 4 | 7 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/板儿.md]] | 15 | 25 | 10 | 4 | 10 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/玉爱.md]] | 15 | 25 | 10 | 4 | 9 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/王仁.md]] | 15 | 25 | 10 | 4 | 13 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/香怜.md]] | 15 | 25 | 10 | 4 | 8 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/警幻仙姑.md]] | 12 | 25 | 13 | 3 | 10 | `curated-v2` | 待人工判断：神话/设定角色，可短页保留或并入概念线 |
| P1 | character | [[characters/乌进孝.md]] | 13 | 25 | 12 | 3 | 6 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | character | [[characters/王子腾.md]] | 14 | 25 | 11 | 3 | 9 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/雪雁.md]] | 14 | 25 | 11 | 3 | 11 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/焦大.md]] | 15 | 25 | 10 | 3 | 12 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/张太医.md]] | 13 | 25 | 12 | 2 | 7 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | character | [[characters/李贵.md]] | 13 | 25 | 12 | 2 | 7 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | character | [[characters/金寡妇.md]] | 13 | 25 | 12 | 2 | 8 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | character | [[characters/孙绍祖.md]] | 14 | 25 | 11 | 2 | 7 | `curated-v1` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/狗儿.md]] | 14 | 25 | 11 | 2 | 9 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/周琼.md]] | 15 | 25 | 10 | 2 | 6 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/封氏.md]] | 15 | 25 | 10 | 2 | 8 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/门子.md]] | 15 | 25 | 10 | 2 | 11 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/入画.md]] | 13 | 25 | 12 | 1 | 7 | `curated-v1` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | character | [[characters/碧痕.md]] | 14 | 25 | 11 | 0 | 4 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | character | [[characters/秋纹.md]] | 14 | 25 | 11 | 0 | 4 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | concept | [[concepts/意淫.md]] | 23 | 30 | 7 | 18 | 11 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | concept | [[concepts/还泪.md]] | 27 | 30 | 3 | 10 | 13 | `curated-v3` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | concept | [[concepts/大观园诗社.md]] | 29 | 30 | 1 | 10 | 8 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | concept | [[concepts/索隐派.md]] | 29 | 30 | 1 | 10 | 6 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | concept | [[concepts/家塾.md]] | 28 | 30 | 2 | 8 | 8 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/英莲被拐.md]] | 21 | 25 | 4 | 9 | 8 | `curated-v3` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/焦大醉骂.md]] | 23 | 25 | 2 | 9 | 8 | `curated-v3` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/宝黛初见.md]] | 23 | 25 | 2 | 8 | 7 | `curated-v3` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/平儿理妆.md]] | 10 | 25 | 15 | 7 | 9 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/司棋被逐.md]] | 16 | 25 | 9 | 7 | 5 | `curated-v1` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/周瑞家的送宫花.md]] | 23 | 25 | 2 | 7 | 7 | `curated-v3` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/宝玉摔玉.md]] | 23 | 25 | 2 | 7 | 7 | `curated-v3` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/宝钗看玉.md]] | 23 | 25 | 2 | 7 | 7 | `curated-v3` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/秦可卿病重.md]] | 23 | 25 | 2 | 7 | 8 | `curated-v3` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/顽童闹学堂.md]] | 23 | 25 | 2 | 7 | 7 | `curated-v3` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/贾家复振.md]] | 11 | 25 | 14 | 6 | 5 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/贾母之死.md]] | 13 | 25 | 12 | 6 | 13 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/迎春之死.md]] | 13 | 25 | 12 | 6 | 18 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/石头入世.md]] | 20 | 25 | 5 | 6 | 7 | `curated-v3` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/黛玉进贾府.md]] | 20 | 25 | 5 | 6 | 7 | `curated-v3` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/元春之死.md]] | 10 | 25 | 15 | 5 | 4 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/夏金桂自焚.md]] | 10 | 25 | 15 | 5 | 8 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/宝玉再入学.md]] | 10 | 25 | 15 | 5 | 5 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/宝玉失玉.md]] | 10 | 25 | 15 | 5 | 5 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/宝玉疯癫.md]] | 10 | 25 | 15 | 5 | 5 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/绣春囊事件.md]] | 10 | 25 | 15 | 5 | 12 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/金钏投井.md]] | 10 | 25 | 15 | 5 | 3 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/凤姐之死.md]] | 11 | 25 | 14 | 5 | 5 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/甄士隐出家.md]] | 11 | 25 | 14 | 5 | 8 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/龄官划蔷.md]] | 11 | 25 | 14 | 5 | 9 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/黛玉葬花.md]] | 12 | 25 | 13 | 5 | 12 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/惜春出家.md]] | 13 | 25 | 12 | 5 | 16 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/贾母散财.md]] | 13 | 25 | 12 | 5 | 13 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/探春远嫁.md]] | 14 | 25 | 11 | 5 | 13 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/金玉良缘线索出现.md]] | 23 | 25 | 2 | 5 | 7 | `curated-v3` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | event | [[events/凤姐遭祸.md]] | 10 | 25 | 15 | 4 | 5 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/凹晶馆联诗.md]] | 10 | 25 | 15 | 4 | 5 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/尤二姐吞金.md]] | 10 | 25 | 15 | 4 | 10 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/开夜宴异兆发悲音.md]] | 10 | 25 | 15 | 4 | 8 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/香菱病入膏肓.md]] | 10 | 25 | 15 | 4 | 10 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/黛玉风雨词.md]] | 10 | 25 | 15 | 4 | 4 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/宝玉初试云雨情.md]] | 11 | 25 | 14 | 4 | 11 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/宝玉题对额.md]] | 11 | 25 | 14 | 4 | 9 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/尤二姐私通.md]] | 11 | 25 | 14 | 4 | 14 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/秦钟夭逝.md]] | 11 | 25 | 14 | 4 | 11 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/薛姨妈说媒.md]] | 11 | 25 | 14 | 4 | 6 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/晴雯撕扇.md]] | 12 | 25 | 13 | 4 | 11 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/柳湘莲出家.md]] | 12 | 25 | 13 | 4 | 12 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/贾雨村归结红楼梦.md]] | 12 | 25 | 13 | 4 | 9 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/王熙凤弄权铁槛寺.md]] | 13 | 25 | 12 | 4 | 4 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/凤姐借刀杀人.md]] | 10 | 25 | 15 | 3 | 5 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/夏金桂进门.md]] | 10 | 25 | 15 | 3 | 10 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/妙玉被劫.md]] | 10 | 25 | 15 | 3 | 4 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/宝玉第二次梦太虚.md]] | 10 | 25 | 15 | 3 | 6 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/宝玉醉归绛芸轩.md]] | 10 | 25 | 15 | 3 | 7 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/尤三姐自刎.md]] | 10 | 25 | 15 | 3 | 3 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/海棠花妖.md]] | 10 | 25 | 15 | 3 | 7 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/湘云醉眠芍药裀.md]] | 10 | 25 | 15 | 3 | 7 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/葫芦庙失火.md]] | 10 | 25 | 15 | 3 | 6 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/鸳鸯殉主.md]] | 10 | 25 | 15 | 3 | 5 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/黛玉丧母.md]] | 10 | 25 | 15 | 3 | 5 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/黛玉噩梦.md]] | 10 | 25 | 15 | 3 | 6 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/黛玉重建桃花社.md]] | 10 | 25 | 15 | 3 | 5 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/宝玉祭金钏.md]] | 11 | 25 | 14 | 3 | 9 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/宝玉秦钟入家塾.md]] | 11 | 25 | 14 | 3 | 11 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/张太医论病.md]] | 11 | 25 | 14 | 3 | 9 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/王熙凤接济刘姥姥.md]] | 11 | 25 | 14 | 3 | 8 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/甄士隐解说太虚.md]] | 11 | 25 | 14 | 3 | 8 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/芙蓉诔.md]] | 11 | 25 | 14 | 3 | 10 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/金寡妇讨说法.md]] | 11 | 25 | 14 | 3 | 12 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/金荣赔礼.md]] | 11 | 25 | 14 | 3 | 14 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/黛玉抚琴.md]] | 11 | 25 | 14 | 3 | 5 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/制灯谜贾政悲谶语.md]] | 12 | 25 | 13 | 3 | 3 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/惜春划清界限.md]] | 12 | 25 | 13 | 3 | 12 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/英莲改名香菱.md]] | 12 | 25 | 13 | 3 | 15 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/贾宝玉路谒北静王.md]] | 12 | 25 | 13 | 3 | 3 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/贾瑞起淫心.md]] | 12 | 25 | 13 | 3 | 8 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/凤姐闹宁国府.md]] | 10 | 25 | 15 | 2 | 5 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/刘姥姥醉卧怡红院.md]] | 10 | 25 | 15 | 2 | 4 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/妙玉走火入魔.md]] | 10 | 25 | 15 | 2 | 5 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/宝玉中举出家.md]] | 10 | 25 | 15 | 2 | 4 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/尤三姐思嫁柳湘莲.md]] | 10 | 25 | 15 | 2 | 3 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/掉包计.md]] | 10 | 25 | 15 | 2 | 7 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/贾雨村受资进京.md]] | 10 | 25 | 15 | 2 | 8 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/鸳鸯三宣牙牌令.md]] | 10 | 25 | 15 | 2 | 5 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/黛玉鬼哭.md]] | 10 | 25 | 15 | 2 | 5 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/冷子兴演说荣国府.md]] | 11 | 25 | 14 | 2 | 8 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/宝玉提亲.md]] | 11 | 25 | 14 | 2 | 4 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/宝玉送旧帕.md]] | 11 | 25 | 14 | 2 | 6 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/宝钗生日.md]] | 11 | 25 | 14 | 2 | 11 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/王熙凤正言弹妒意.md]] | 11 | 25 | 14 | 2 | 3 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/秦钟得趣馒头庵.md]] | 11 | 25 | 14 | 2 | 12 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/贾天祥正照风月鉴.md]] | 11 | 25 | 14 | 2 | 9 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/赵姨娘之死.md]] | 12 | 25 | 13 | 2 | 3 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | event | [[events/香菱换裙.md]] | 12 | 25 | 13 | 2 | 12 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | location | [[locations/扬州.md]] | 19 | 25 | 6 | 9 | 12 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | location | [[locations/芦雪庵.md]] | 21 | 25 | 4 | 9 | 9 | `curated-v3` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | location | [[locations/姑苏.md]] | 21 | 25 | 4 | 7 | 11 | `curated-v3` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | location | [[locations/贾家义学.md]] | 13 | 25 | 12 | 4 | 4 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | location | [[locations/葫芦庙.md]] | 24 | 25 | 1 | 4 | 12 | `curated-v3` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | location | [[locations/应天府.md]] | 13 | 25 | 12 | 3 | 4 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | location | [[locations/荣禧堂.md]] | 13 | 25 | 12 | 3 | 4 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | location | [[locations/绛芸轩.md]] | 12 | 25 | 13 | 2 | 4 | `curated-v2` | 批量骨架页候选：有明显行数缺口，但先排在 P1 |
| P1 | location | [[locations/青埂峰.md]] | 15 | 25 | 10 | 2 | 6 | `curated-v2` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | output | [[outputs/红楼梦速读指南.md]] | 59 | 60 | 1 | 10 | 33 | `curated-v3` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | poem | [[poetry/满纸荒唐言.md]] | 27 | 30 | 3 | 5 | 12 | `curated-v3` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | poem | [[poetry/开篇诗.md]] | 28 | 30 | 2 | 4 | 12 | `curated-v3` | 二线补强：等 P0 风格稳定后再处理 |
| P1 | redology | [[redology/护官符与官场秩序研究综述.md]] | 44 | 45 | 1 | 6 | 31 | `curated-v1` | 二线补强：等 P0 风格稳定后再处理 |
| P2 | character | [[characters/周瑞家的.md]] | 16 | 25 | 9 | 6 | 13 | `curated-v2` | 保留短页候选：低入链，先不批量扩写 |
| P2 | character | [[characters/麝月.md]] | 16 | 25 | 9 | 6 | 6 | `curated-v2` | 保留短页候选：低入链，先不批量扩写 |
| P2 | character | [[characters/司棋.md]] | 17 | 25 | 8 | 6 | 14 | `curated-v2` | 保留短页候选：低入链，先不批量扩写 |
| P2 | character | [[characters/潘又安.md]] | 17 | 25 | 8 | 6 | 11 | `curated-v2` | 保留短页候选：低入链，先不批量扩写 |
| P2 | character | [[characters/蒋玉菡.md]] | 21 | 25 | 4 | 6 | 8 | `curated-v2` | 保留短页候选：低入链，先不批量扩写 |
| P2 | character | [[characters/薛蝌.md]] | 17 | 25 | 8 | 5 | 14 | `curated-v2` | 保留短页候选：低入链，先不批量扩写 |
| P2 | character | [[characters/甄应嘉.md]] | 16 | 25 | 9 | 4 | 10 | `curated-v2` | 保留短页候选：低入链，先不批量扩写 |
| P2 | character | [[characters/龄官.md]] | 16 | 25 | 9 | 4 | 9 | `curated-v1` | 保留短页候选：低入链，先不批量扩写 |
| P2 | character | [[characters/智能儿.md]] | 17 | 25 | 8 | 4 | 13 | `curated-v2` | 保留短页候选：低入链，先不批量扩写 |
| P2 | character | [[characters/贾代儒.md]] | 16 | 25 | 9 | 3 | 9 | `curated-v1` | 保留短页候选：低入链，先不批量扩写 |
| P2 | character | [[characters/芳官.md]] | 17 | 25 | 8 | 3 | 6 | `curated-v2` | 保留短页候选：低入链，先不批量扩写 |
| P2 | event | [[events/贾雨村断案.md]] | 14 | 25 | 11 | 4 | 5 | `curated-v1` | 保留短页候选：低入链，先不批量扩写 |
| P2 | event | [[events/贾雨村攀附贾府.md]] | 15 | 25 | 10 | 4 | 5 | `curated-v1` | 保留短页候选：低入链，先不批量扩写 |
| P2 | event | [[events/宝玉结识秦钟.md]] | 23 | 25 | 2 | 4 | 7 | `curated-v3` | 保留短页候选：低入链，先不批量扩写 |
| P2 | event | [[events/贾雨村参贾府.md]] | 14 | 25 | 11 | 3 | 5 | `curated-v1` | 保留短页候选：低入链，先不批量扩写 |
| P2 | event | [[events/冯渊之死.md]] | 14 | 25 | 11 | 2 | 10 | `curated-v2` | 保留短页候选：低入链，先不批量扩写 |
| P2 | event | [[events/柳湘莲故事.md]] | 16 | 25 | 9 | 2 | 9 | `curated-v2` | 保留短页候选：低入链，先不批量扩写 |

## 7. 不在本阶段做的事

- 不改正文页。
- 不为清 WARN 灌水式扩写。
- 不批量合并页面。
- 不调整页面模板或质量阈值。

## 8. 验证口径

Phase 3A 完成后应满足：

- 健康检查仍然 `ERROR: 0`；
- `wikilinks` 仍全部可解析；
- 本报告作为维护/审查 Markdown，不计入成品 Wiki Markdown 765 的正文口径；
- 除本报告和必要的维护脚本登记外，不应修改正文页。
