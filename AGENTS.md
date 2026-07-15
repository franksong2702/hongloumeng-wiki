---
title: 红楼梦 Wiki Agent 操作手册
created: 2026-05-02
updated: 2026-07-14
type: meta
book: 红楼梦
status: active
tags: [hongloumeng, meta, agent, maintenance]
---

# 红楼梦 Wiki Agent 操作手册

> 本手册只保留当前可执行规则。动态数量以[[02_Learn/08_book-wikis/红楼梦/WIKI_STATUS.md|自动状态页]]为唯一快照；历史维护过程见[[02_Learn/08_book-wikis/红楼梦/WIKI_MAINTENANCE_REVIEW.md|维护收尾报告]]。

## 1. 工作边界

1. 所有命令从 Wiki 根目录 `02_Learn/08_book-wikis/红楼梦/` 运行，不写机器相关绝对路径。
2. 先读[[02_Learn/08_book-wikis/红楼梦/SCHEMA.md|Schema]]、[[02_Learn/08_book-wikis/红楼梦/MAINTENANCE.md|维护机制]]和[[02_Learn/08_book-wikis/红楼梦/log.md|发布日志]]，再开始修改。
3. `raw/` 是可选的本地采集证据层：如存在则只读，不移动、不覆盖，也不把它当成发布站依赖。
4. `_mkdocs_build/` 是可再生构建产物，不手工编辑。
5. 当前 Vault 副本不一定是 Git 仓库。只有 `git rev-parse --show-toplevel` 成功后，才把 Git 状态、提交或部署当作当前环境事实。

## 2. 目录职责

| 目录 | 职责 |
|---|---|
| `chapters/` | 120 回差异化章节导读 |
| `texts/traditional/` | 可发布、可公开复核的繁体原文层 |
| `texts/simplified/` | 简体阅读层与稳定 block anchor |
| `characters/` | 人物小传、关系、命运线、主要事件线 |
| `events/` | 事件说明、因果、人物、叙事作用与原文锚点 |
| `concepts/` | 主题概念与文本证据事件 |
| `locations/` | 空间定位、人物关系、事件现场与推荐回读 |
| `poetry/` | 诗词位置、赏析、人物命运与主题关系 |
| `redology/` | 版本、作者、研究综述、精读与红学家 |
| `background/` | 制度、文化、宗教与历史背景 |
| `families/` | 家族谱系、姻亲与权力网络 |
| `motifs-symbols/` | 意象、象征物与叙事功能 |
| `maps/`、`timelines/` | 图谱、路线与时间结构 |
| `queries/` | 分类索引与导航 |
| `outputs/` | 可独立阅读的导览、手册与专题产品 |
| `scripts/` | 只读检查、状态生成与静态站构建 |
| `raw/` | 本地可选原始采集文件，不进入发布站 |

## 3. 标准工作流

### 修改前

```bash
python3 scripts/wiki_health_check.py --strict
python3 scripts/generate_wiki_status.py --check
```

如果严格健康检查已经是 `ERROR 0 / WARN 0`，不要为了“继续优化”而做全库扩写；先把用户目标收窄为一个文档、一个页面类型或一条阅读链路。

### 修改中

1. 保持改动范围单一：内容、链接、元数据、脚本或站点机制不要无关混批。
2. 修改页面时更新 `updated`；新页面补齐完整 frontmatter。
3. 新建事件前搜索同义节点，避免重复事件。
4. 新增研究判断时区分原文事实、研究观点与 Wiki 判断。
5. 新增页面至少建立两个语义明确的入链，不为了增加链接数量制造空泛反链。

### 修改后

```bash
python3 scripts/wiki_health_check.py --strict
python3 scripts/generate_wiki_status.py
python3 scripts/generate_wiki_status.py --check
python3 scripts/external_link_check.py --strict
python3 scripts/mkdocs_build_check.py
```

涉及人物事件线时，再运行：

```bash
python3 scripts/character_event_line_review.py
python3 scripts/character_event_reverse_link_check.py
```

读者可见内容、主要阅读路径或站点机制发生变化时，必须在同一批次更新 `log.md`。

## 4. 页面质量规则

| 页面类型 | 最低内容结构 |
|---|---|
| `character` | 人物小传、关键关系、命运线、关键章节；重要人物增加主要事件线 |
| `event` | 事件说明、相关回目、叙事作用、人物关系、精确原文锚点 |
| `concept` | 概念说明、阅读视角、关键章节、文本证据事件或相关页面 |
| `location` | 空间定位、人物互动、关键事件现场、推荐回读 |
| `poem` | 文本位置、赏析、人物/主题关系、可回读章节 |
| `redology` | 核心问题、证据分层、观点分歧、来源与原文抓手 |
| `background` | 制度背景、小说对应、关键章节与阅读视角 |
| `output` | 明确读者任务、经过筛选的路线和可进入的成熟子页面 |

机械行数只是下限，不代表文学判断已经可靠。禁止用通用套话凑过阈值。

## 5. 链接规则

1. 跨目录链接首选 Vault 完整路径，例如：

   ```md
   [[02_Learn/08_book-wikis/红楼梦/characters/贾宝玉.md|贾宝玉]]
   ```

2. 同目录短链接只在不存在同名歧义时使用。
3. Markdown 表格中不要放带 `|alias` 的 wikilink；优先改为列表，或使用不带别名的文件链接。
4. 事件页必须链接到简体原文的稳定 block anchor：

   ```md
   [[02_Learn/08_book-wikis/红楼梦/texts/simplified/第008回.md#^hlm-008-baochai-kan-yu|第008回原文：宝钗看玉]]
   ```

5. 不使用行号链接替代语义锚点。

## 6. 来源规则

1. `texts/traditional/` 的 `sources:` 必须至少包含一个公开 URL；当前使用对应回目的 Wikisource 页面。
2. `sources:` 中的本地 Markdown 路径必须真实存在；严格健康检查会验证。
3. `raw/` 只保存采集证据，不作为发布页必须存在的链接目标。
4. 研究页外部来源的 404/410 必须替换或删除；403、429、TLS、超时等进入人工复核，不直接判死链。
5. 外部材料不能替代原文；研究结论必须能回到章节、事件或原文锚点。

## 7. 不允许的操作

- 不批量重写 120 回原文正文。
- 不在没有事实抓手时创建新人物、事件或概念页。
- 不把历史统计复制到多个根目录文档。
- 不把健康检查归零解释为“文学内容已经完美”。
- 不在非 Git Vault 中声称某文件已提交、某分支干净或 GitHub Pages 已部署。
- 不编辑 `_mkdocs_build/` 代替修改源文件。

## 8. 完成报告

每次维护至少留下：

```text
改动范围: <文件或专题>
验证命令: <原样命令>
返回结果: <exit code 与关键统计>
证据路径: <状态页、日志或报告>
未验证项: <如有，明确说明>
```
