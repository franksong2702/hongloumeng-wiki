# 红楼梦 Wiki

> 一座可以住进去的房子，不是一个骨架。

这是《红楼梦》的 Obsidian Wiki，包含 120 回全文（繁简双版本）、105 个人物页、120 个事件页、38 个概念页、52 个红学专题综述，以及 26 张 AI 插图。

- 在线阅读：[红楼梦 Wiki](https://franksong2702.github.io/hongloumeng-wiki/)
- 当前版本：v2.0.1

## 快速开始

- [START_HERE.md](START_HERE.md) — 按你是谁来分入口（第一次读 / 读过想重读 / 研究红学 / 快速查找）
- [index.md](index.md) — 全量索引
- [SCHEMA.md](SCHEMA.md) — 编译规则
- [ROADMAP.md](ROADMAP.md) — 研究路线图
- [outputs/红楼梦编译总评.md](outputs/红楼梦编译总评.md) — 完成情况与质量评估

## 内容概览

| 模块 | 数量 | 说明 |
|------|------|------|
| 章节导读 | 120 回 | 每回含概要、人物、事件、概念、伏笔、阅读重点 |
| 原文 | 120 × 2 | 繁体 + 简体双版本，繁简互链 |
| 人物 | 105 | 核心人物、管理权力、丫鬟群像、外部视角、旁系、红学家/批书人 |
| 事件 | 120 | 按叙事功能分组，含事件经过、章节、叙事作用 |
| 概念 | 38 | 情、空、梦、真假、薄命、礼法、婚姻、护官符等 |
| 地点 | 21 | 大观园、荣国府、宁国府、太虚幻境等 |
| 诗词 | 12 | 判词、曲文、葬花吟、芙蓉女儿诔、好了歌等 |
| 红学专题 | 52 | 28 篇综述 + 22 个红学家/批书人页 |
| 背景 | 7 | 清代家族制度、丫鬟制度、园林文化、科举仕途等 |
| 图谱 | 6 | 人物关系、贾府结构、大观园空间、SVG 平面图等 |
| 时间线 | 3 | 全书、贾府兴衰、宝黛钗关系 |
| 家族 | 5 | 贾、史、王、薛、甄四大家族 + 甄家 |
| 意象 | 6 | 石头、通灵宝玉、金锁、风月宝鉴、海棠、芙蓉 |
| AI 插图 | 26 | 传统工笔画 + 淡彩水彩风格 |
| 输出产品 | 13 | 速读指南、人物手册、主题导读、大观园空间手册等 |
| **总计** | **765** | Markdown 文件 |

## 目录结构

```
红楼梦/
├── START_HERE.md              # 阅读入口（按读者画像）
├── README.md                  # 本文件
├── index.md                   # 全量索引
├── SCHEMA.md                  # 编译规则与格式标准
├── ROADMAP.md                 # 研究路线图
├── log.md                     # 维护日志
├── AGENTS.md                  # Agent 维护手册
│
├── chapters/                  # 120 回章节导读
├── texts/
│   ├── traditional/           # 120 回繁体原文
│   └── simplified/            # 120 回简体原文
├── characters/                # 105 个人物页
├── events/                    # 120 个事件页
├── concepts/                  # 38 个概念页
├── locations/                 # 21 个地点页
├── poetry/                    # 12 首诗词
├── redology/                  # 52 个红学专题
├── background/                # 7 个背景知识页
├── maps/                      # 6 张图谱
├── timelines/                 # 3 条时间线
├── families/                  # 5 个家族页
├── motifs-symbols/            # 6 个意象/物象页
├── queries/                   # 各类索引（人物、事件、概念、诗词等）
├── outputs/                   # 13 个输出产品
└── images/                    # 26 张 AI 插图
```

## 阅读建议

**第一次读**：花 5 分钟读 [outputs/红楼梦速读指南.md](outputs/红楼梦速读指南.md)，然后从 [chapters/第001回.md](chapters/第001回.md) 开始，每回导读 10-15 分钟。

**读过想重读**：从 [outputs/红楼梦主题导读.md](outputs/红楼梦主题导读.md) 进入，选一个主题追着概念走；或者从 [outputs/红楼梦人物手册.md](outputs/红楼梦人物手册.md) 找到想深读的人物。

**研究红学**：从 [outputs/红学争议导览.md](outputs/红学争议导览.md) 开始，按版本→作者→真假→宝黛钗→秦可卿→王熙凤→贾府败落的顺序进入专题综述。

## 在 Obsidian 中使用

这个 Wiki 完全基于 Obsidian 构建，双链、反向链接、大纲面板等原生功能均可使用。

### 方法一：Git 克隆（推荐）

```bash
git clone https://github.com/franksong2702/hongloumeng-wiki.git
```

然后在 Obsidian 中 **Open folder as vault**，选择克隆下来的目录即可。

### 方法二：下载 ZIP

1. 点击本页面右上角 **Code → Download ZIP**
2. 解压到任意位置
3. 在 Obsidian 中 **Open folder as vault**，选择解压后的目录

### 依赖

- Obsidian 1.4+（需支持 wikilinks）
- 本 Wiki 不依赖任何第三方插件，核心功能全部原生可用
- 如需使用 Dataview 查询，可在 Obsidian 社区插件中安装 Dataview（可选，不影响阅读）

## 质量状态

- 完整路径 wikilink 检查：0 broken links
- 薄页/空泛页：已清零
- 占位句/模板句：已清零
- 繁简双版本原文：已入库
- Wiki 原文层自包含（不依赖外部 Raw 目录）

## 许可

原文来自 [Wikisource](https://zh.wikisource.org/wiki/%E7%B4%85%E6%A8%93%E5%A4%A2)，属公有领域。
Wiki 结构、编译产物、AI 插图按 CC BY 4.0 共享。
