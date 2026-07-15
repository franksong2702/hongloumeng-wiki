---
title: 红楼梦 Wiki
created: 2026-04-27
updated: 2026-07-15
type: guide
book: 红楼梦
version: v2.2.1
status: curated-v3
tags: [hongloumeng, book-wiki, readme]
---

# 红楼梦 Wiki

> 一座可以住进去的房子，不是一个骨架。

这是《红楼梦》的 Obsidian Wiki，包含 120 回繁简原文、人物、事件、概念、红学研究、图谱与 AI 插图。当前数量以 [WIKI_STATUS.md](WIKI_STATUS.md) 为唯一快照。

- 在线阅读：[红楼梦 Wiki](https://franksong2702.github.io/hongloumeng-wiki/)
- 当前版本：v2.2.1

## 快速开始

- [START_HERE.md](START_HERE.md) — 按第一次读、重读、研究和快速查找组织的完整入口
- [index.md](index.md) — 站点首页
- [outputs/红楼梦速读指南.md](outputs/红楼梦速读指南.md) — 低门槛阅读路线
- [outputs/人物关系阅读指南.md](outputs/人物关系阅读指南.md) — 沿人物、事件与地点重读
- [SCHEMA.md](SCHEMA.md) — 内容模型与编译规范
- [MAINTENANCE.md](MAINTENANCE.md) — 当前维护与发布闸门
- [ROADMAP.md](ROADMAP.md) — 下一阶段研究路线

## 内容概览

| 模块 | 数量 | 说明 |
|---|---:|---|
| 章节导读 | 120 | 每回含概要、人物、事件、概念、伏笔与阅读重点 |
| 原文 | 120 × 2 | 繁体公开来源 + 简体阅读锚点，繁简互链 |
| 人物 | 106 | 小传、关系、命运、章节与主要事件线 |
| 事件 | 181 | 事件经过、因果、人物、叙事作用与精确原文锚点 |
| 概念 | 38 | 情、空、梦、真假、薄命、礼法、婚姻、权力等 |
| 地点 | 21 | 空间定位、人物互动、事件现场与推荐回读 |
| 诗词 | 12 | 判词、曲文、葬花吟、芙蓉女儿诔、好了歌等 |
| 红学与研究 | 53 | 研究综述、精读、红学家与证据使用规范 |
| 背景 | 7 | 家族、奴仆、婚姻、园林、科举、佛道与衣食文化 |
| 图谱 | 6 | 人物关系、贾府结构、大观园空间与路线图 |
| 时间线 | 3 | 全书、贾府兴衰、宝黛钗关系 |
| 家族 | 5 | 贾、史、王、薛、甄家 |
| 意象 | 6 | 石头、通灵宝玉、金锁、风月宝鉴、海棠、芙蓉 |
| AI 插图 | 26 | 人物肖像、四季图与叙事场景 |
| 输出产品 | 14 | 速读、人物、主题、关系、空间、研究与精读产品 |
| **总计** | **831** | 成品 Wiki Markdown，不含 `raw/` |

动态数量由 [WIKI_STATUS.md](WIKI_STATUS.md) 自动生成并由 CI 核对。`raw/` 如存在，
只属于本地编辑 Vault 的采集证据，不在公共 README 中维护其数量，也不属于公共仓库
或静态站依赖；从 GitHub 克隆的读者无需该目录即可完整阅读。

## 目录结构

```text
红楼梦/
├── README.md                  # 项目说明
├── START_HERE.md              # 按读者任务组织的入口
├── index.md                   # 站点首页
├── SCHEMA.md                  # 内容模型与规范
├── ROADMAP.md                 # 研究路线图
├── AGENTS.md                  # Agent 操作手册
├── MAINTENANCE.md             # 维护 SOP
├── WIKI_STATUS.md             # 自动状态页
├── log.md                     # 读者发布日志
│
├── chapters/                  # 120 回导读
├── texts/traditional/         # 120 回繁体原文
├── texts/simplified/          # 120 回简体原文与锚点
├── characters/                # 人物
├── events/                    # 事件
├── concepts/                  # 概念
├── locations/                 # 地点
├── poetry/                    # 诗词
├── redology/                  # 红学与研究
├── background/                # 制度文化背景
├── families/                  # 家族
├── motifs-symbols/            # 意象物象
├── maps/                      # 图谱
├── timelines/                 # 时间线
├── queries/                   # 索引
├── outputs/                   # 输出产品
├── images/                    # AI 插图
├── scripts/                   # 检查与构建
└── raw/                       # 本地可选采集证据，公共仓库不依赖
```

## 阅读建议

**第一次读**：先看 [红楼梦速读指南](outputs/红楼梦速读指南.md)，再从 [第001回导读](chapters/第001回.md) 开始。章节页可以进入原文、人物和关键事件。

**读过想重读**：从 [主题导读](outputs/红楼梦主题导读.md)、[人物手册](outputs/红楼梦人物手册.md) 或 [人物关系阅读指南](outputs/人物关系阅读指南.md) 选择一条线。

**研究红学**：从 [红学争议导览](outputs/红学争议导览.md) 开始，先区分版本、作者、脂批和后四十回，再进入具体专题。

## 在 Obsidian 中使用

### Git 克隆

```bash
git clone https://github.com/franksong2702/hongloumeng-wiki.git
```

在 Obsidian 中选择 **Open folder as vault**，打开克隆目录即可。

### 下载 ZIP

1. 在 GitHub 选择 **Code → Download ZIP**；
2. 解压；
3. 在 Obsidian 中打开解压目录。

### 依赖

- Obsidian 1.4+；
- 核心阅读不依赖第三方插件；
- 静态站由 MkDocs Material 构建；
- Dataview 不是阅读所必需。

## 质量闸门

发布前依次运行：

```bash
python3 scripts/wiki_health_check.py --strict
python3 scripts/generate_wiki_status.py --check
python3 scripts/external_link_check.py --strict
python3 scripts/mkdocs_build_check.py
```

这些命令验证结构、来源路径、链接、锚点、数量、版本、外链和静态站构建；它们不能替代文学判断和红学事实核查。

## 许可

原文来自 [Wikisource](https://zh.wikisource.org/wiki/%E7%B4%85%E6%A8%93%E5%A4%A2)，属公有领域。Wiki 结构、编译产物与 AI 插图按 CC BY 4.0 共享。
