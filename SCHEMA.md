---
title: 红楼梦 Book Wiki Schema
created: 2026-04-27
updated: 2026-07-14
type: schema
book: 红楼梦
version: v2.2.1
tags: [book-wiki, schema, 红楼梦]
status: meta
---

# 红楼梦 Book Wiki Schema

## 1. 版本

当前版本：**v2.2.1**

| 版本 | 说明 |
|---|---|
| v1.0.0 | 120 回摘要与人物、事件、概念、地点的初始导航骨架 |
| v2.0.0 | 研究型页面、繁简原文、图谱与核心专题形成 |
| v2.1.0 | 前 10 回阅读提示与静态站阅读体验增强 |
| v2.2.0 | 读者首页、自动状态页、关键回目编辑层、证据分层与外链闸门 |
| v2.2.1 | 根目录治理文档对齐、公开原文来源修复、非 Git 状态页稳定性与来源路径检查 |
| v3.0.0 | 仅用于重大领域模型或阅读架构变化 |

遵循 SemVer：修复现有行为更新 patch，新增兼容能力更新 minor，重大不兼容架构变化才更新 major。

## 2. Domain

本 Wiki 只服务于《红楼梦》的阅读、原文定位、人物关系、事件因果、空间、主题、诗词、背景知识和红学问题。不要把通用文章 Wiki 的目录或字段机械搬入本项目。

## 3. 目录职责

| 目录 | 职责 |
|---|---|
| `chapters/` | 章节概要、人物、事件、概念、伏笔、本回辨识与原文回读 |
| `texts/traditional/` | 可发布的繁体原文，每回保留公开来源 URL |
| `texts/simplified/` | 简体阅读层、阅读提示与稳定 block anchor |
| `characters/` | 人物小传、关系、命运、章节与主要事件线 |
| `events/` | 事件经过、回目定位、人物、叙事作用和精确原文锚点 |
| `concepts/` | 主题概念、阅读视角、关键章节和文本证据事件 |
| `locations/` | 空间定位、人物互动、事件现场与推荐回读 |
| `families/` | 家族谱系、姻亲与权力网络 |
| `motifs-symbols/` | 意象、象征物与叙事功能 |
| `poetry/` | 诗词位置、文本分析、人物命运与主题关系 |
| `background/` | 制度、文化、宗教和历史背景 |
| `redology/` | 版本、作者、脂批、红学家、争议综述与精读 |
| `timelines/` | 全书、家族和人物关系的时间结构 |
| `maps/` | 人物、家族、空间与路线图谱 |
| `queries/` | 分类索引、原文索引与导航 |
| `outputs/` | 面向明确读者任务的导览、手册和专题产品 |
| `templates/` | 新页面模板，不作为成品内容 |
| `scripts/` | 只读检查、状态生成与静态站构建 |
| `raw/` | 本地可选采集证据；只读，不进入发布站 |

## 4. 来源层级

### 4.1 发布原文层

- `texts/traditional/` 是发布仓库可独立使用的繁体原文层。
- 每回 `sources:` 至少包含对应 Wikisource 页面的公开 URL。
- `texts/simplified/` 从繁体层转换而来，承担简体阅读和语义锚点；不反向覆盖繁体文本。

### 4.2 本地采集层

- `raw/` 如存在，只保存最初采集文件和来源元数据。
- Raw 文件不可改写、移动或用作发布页面必须存在的链接目标。
- 发布仓库、GitHub Pages 和状态页数量不依赖 `raw/`。

### 4.3 研究来源

- 外部论文、书目、机构文章和权威媒体材料写入实际吸收观点页面的 `sources:`。
- 内部 Wiki 页面可以作为对读路径，但不能冒充外部学术来源。
- `sources:` 中的本地路径必须真实存在，严格健康检查会验证。

## 5. Frontmatter

通用成品页面：

```yaml
---
title: 页面标题
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: character
book: 红楼梦
status: curated-v2
tags: [hongloumeng]
sources: []
---
```

### 5.1 type

| 类别 | 允许值 |
|---|---|
| 章节与原文 | `chapter`, `source-text` |
| 内容实体 | `character`, `event`, `concept`, `location`, `family`, `motif`, `poem`, `background` |
| 研究与导航 | `redology`, `redology-scholar`, `timeline`, `map`, `query`, `output` |
| 根目录治理 | `guide`, `index`, `schema`, `roadmap`, `meta`, `changelog` |
| 维护文档 | `maintenance-guide`, `maintenance-report`, `maintenance-review` |
| 模板与本地采集 | `template`, `raw` |

`poetry` 是旧字段，不再新增；诗词页统一使用 `poem`。

### 5.2 status

内容成熟度：

| status | 含义 |
|---|---|
| `draft` | 临时草稿或模板，不作为成熟读者入口 |
| `compiled-v1` | 已有结构化内容，仍需人工精修 |
| `curated-v1` | 已去空壳，有基本解释 |
| `curated-v2` | 有具体文本判断、章节抓手或命运线 |
| `curated-v3` | 核心页，已按阶段、关系、主题或证据重组 |
| `curated-v4` | 站点级入口或经过完整读者任务重构的页面 |

原文与治理状态：

| status | 含义 |
|---|---|
| `raw-import` | 忠实导入的繁体原文 |
| `converted-v1` | 从繁体原文转换的简体阅读层 |
| `meta` | 稳定规范或元数据文档 |
| `active` | 当前维护机制或现行架构 |
| `generated` | 脚本生成，禁止手工维护动态字段 |
| `final` | 已完成的收尾文档，不再持续充当当前状态源 |
| `historical-snapshot` | 历史输入或阶段快照，不代表当前基线 |

## 6. 各类型最低要求

1. `chapter`：概要、出场人物、关键事件、相关概念、阅读重点；关键回目增加本回辨识和原文回读。
2. `character`：人物小传、关键关系、命运线、关键章节；核心人物增加主要事件线和关系阅读。
3. `event`：事件说明、相关回目、叙事作用、人物关系、阅读抓手和精确原文锚点。
4. `concept`：概念说明、阅读视角、关键章节、相关概念；高价值概念增加文本证据事件。
5. `location`：空间定位、人物互动、关键事件现场、推荐回读和继续阅读。
6. `poem`：文本位置、赏析、人物/主题关系、可回读章节。
7. `redology`：核心问题、观点分歧、原文事实、研究来源、Wiki 判断和对读入口。
8. `background`：制度文化背景、小说对应、关键章节和阅读视角。
9. `output`：明确读者任务、筛选后的路线和成熟子页面；不能只是链接仓库。

## 7. 证据分层

研究综述和精读页统一使用[[02_Learn/08_book-wikis/红楼梦/redology/证据使用规范.md|证据使用规范]]：

1. **原文事实**：至少一个 `texts/simplified/第xxx回.md#^hlm-*` 精确锚点。
2. **研究观点**：`sources:` 至少一条可识别的外部文章、论文或著作。
3. **Wiki 判断**：本站归纳必须明确标识，不冒充原文或学界定论。
4. **异说边界**：版本、作者、后四十回与伦理争议不得抹平不同证据层次。

## 8. 链接规则

### 8.1 跨目录链接

优先使用 Vault 完整路径：

```md
[[02_Learn/08_book-wikis/红楼梦/characters/林黛玉.md|林黛玉]]
[[02_Learn/08_book-wikis/红楼梦/events/宝玉挨打.md|宝玉挨打]]
```

同目录短链接只在没有同名歧义时使用。

### 8.2 表格链接

Markdown 表格中禁止带 `|alias` 的 Wikilink。需要别名时改用列表；表格必须保留时，使用不带别名的完整文件链接。

### 8.3 原文锚点

- block id 统一为 `^hlm-回数-主题短名`。
- 锚点必须位于真实正文段落，不放在 frontmatter 或阅读提示中。
- 事件页必须至少提供一个简体原文精确锚点。
- 不使用 `#L33` 一类易漂移行号作为长期定位。
- 多页面指向同一正文现场时可以共用语义锚点。

## 9. 禁止的维护方式

- 创建只有标题和通用说明的空壳页。
- 用“推动人物关系变化”“通过相关章节可以追踪”等套话凑行数。
- 为清指标批量回填没有叙事意义的反链。
- 把后四十回情节无标识地混入前八十回人物判断。
- 在多个根目录文档手工复制当前数量。
- 让发布页面依赖本地未发布的 `raw/`。
- 手工编辑 `_mkdocs_build/` 代替源文件。

## 10. 批量更新后的检查

```bash
python3 scripts/wiki_health_check.py --strict
python3 scripts/generate_wiki_status.py
python3 scripts/generate_wiki_status.py --check
python3 scripts/external_link_check.py --strict
python3 scripts/mkdocs_build_check.py
```

涉及人物事件线时追加：

```bash
python3 scripts/character_event_line_review.py
python3 scripts/character_event_reverse_link_check.py
```

读者可见内容或站点机制变化必须同步更新 `log.md`。
