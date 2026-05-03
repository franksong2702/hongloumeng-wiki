---
title: 红楼梦 Wiki Agent 操作手册
created: 2026-05-02
updated: 2026-05-03
type: meta
book: 红楼梦
status: curated-v1
tags: [hongloumeng, meta, agent]
---

# 红楼梦 Wiki Agent 操作手册

> 这是给 Agent（AI assistant）的操作手册。完整的领域规范见 [[SCHEMA|红楼梦 Book Wiki Schema]]。
> 读者入口见 [[START_HERE|红楼梦阅读入口]]。

## 1. 结构总览

本 Wiki 位于 `/Users/xuefusong/syncthings/Obsidian/Obsidian Vault/02_Learn/08_book-wikis/红楼梦/`。

| 目录 | 文件数 | 职责 | 典型结构 |
|------|------:|------|----------|
| `chapters/` | 120 | 120回章节导读 | 概要 + 出场人物 + 关键事件 + 伏笔 |
| `texts/simplified/` | 120 | 简体原文（只读转换层） | 原文 + block anchors |
| `characters/` | 105 | 人物页 | 人物小传 + 关键关系 + 关键章节 + 相关页面 |
| `events/` | 120 | 事件页 | 事件经过 + 叙事功能 + 相关回目 + 相关概念 |
| `concepts/` | 38 | 主题概念 | 概念说明 + 阅读视角 + 关键章节 |
| `locations/` | 21 | 地点空间 | 空间说明 + 居住者/功能 + 相关章节 |
| `poetry/` | 12 | 诗词曲文 | 文本位置 + 赏析 + 人物/主题关系 |
| `redology/` | 52 | 红学研究 | 学术定位 + 代表著作 + 核心论点 + 红学史地位 |
| `background/` | 7 | 文化背景 | 制度介绍 + 小说对应 + 阅读视角 |
| `families/` | 5 | 四大家族 | 谱系 + 关键人物 + 家族关系 |
| `motifs-symbols/` | 6 | 意象物象 | 意象功能 + 叙事功能 + 关键章节 |
| `maps/` | 7 | 图谱（含SVG） | 空间图 + 关系图 + 路线图 |
| `timelines/` | 3 | 时间线 | 事件按时间排序 |
| `queries/` | 8 | 索引/导航 | 按类别分组的全量链接表 |
| `outputs/` | 12 | 输出产品 | 导览 + 手册 + 阅读路线 |
| `images/` | 26 | AI 插图 | 人物肖像16 + 场景图9 + 四季图1 |
| `templates/` | 2 | 页面模板 | chapter-template, character-template |

**总文件数：644**

## 2. 当前状态快照

| 指标 | 值 |
|------|---|
| 总 Markdown 文件 | 644 |
| 总字符页行数 | ~4500（93页） |
| 断链 | 0（19个已在本轮回圈修复） |
| 占位符 | 0 |
| 薄页（<25行） | 0（事件页已全部扩写至25-35行） |
| 剩余薄页 | 14个神话人物/极次要角色（有合理原因） |
| 最后健康检查 | 2026-05-01 |

## 3. 页面质量标准

### 3.1 各 type 的最小结构要求

**每个页面创建或扩写时，必须包含以下 section：**

| type | 必须包含的 section | 最小行数 |
|------|---------------------|---------|
| character | 人物小传 + 关键关系 + 关键章节（表格）+ 相关页面 | 25-30 |
| event | 事件经过 + 叙事功能 + 相关回目 + 相关概念 | 25-30 |
| concept | 概念说明 + 阅读视角 + 关键章节 + 相关页面 | 30+ |
| location | 空间说明 + 功能/居住者 + 相关章节 + 相关页面 | 25+ |
| poem | 文本位置 + 赏析 + 人物/主题关系 + 相关章节 | 30+ |
| redology | 学术定位 + 代表著作 + 核心论点 + 红学史地位 | 45+ |
| background | 制度介绍 + 小说对应 + 关键章节 + 相关页面 | 50+ |
| output | 有引导性的导语 + 结构化内容（表格/ prose 为主）| 60+ |

**禁止的句式**（见 SCHEMA）：
- "作为关键事件入口保留"
- "推动人物关系变化"
- "通过相关章节可以追踪"
- "本回未单列"
- "待补 / TODO / 暂无"

### 3.2 Frontmatter 要求

每个页面必须包含：

```yaml
---
title: 页面标题
created: YYYY-MM-DD
updated: YYYY-MM-DD        # 每次修改必须更新
type: chapter|character|family|location|event|concept|motif|poem|background|redology|timeline|map|query|output|template
book: 红楼梦
status: compiled-v1|curated-v1|curated-v2|curated-v3
tags: [hongloumeng, ...]
---
```

### 3.3 Status 含义速查

| status | 含义 | 何时升级 |
|--------|------|----------|
| `compiled-v1` | 结构化骨架，可读但可能缺判断 | 新编译的页面 |
| `curated-v1` | 已去空壳，有基本解释 | 骨架→有内容 |
| `curated-v2` | 有具体文本判断、章节抓手 | 扩写时有分析性内容 |
| `curated-v3` | 核心页，已按阶段/关系/主题重组 | 顶级人物、核心事件 |

## 4. 链接规则

### 4.1 全路径 wikilink（首选）

所有跨目录链接使用完整路径：

```
[[02_Learn/08_book-wikis/红楼梦/characters/贾宝玉.md|贾宝玉]]
[[02_Learn/08_book-wikis/红楼梦/concepts/空.md|空]]
[[02_Learn/08_book-wikis/红楼梦/chapters/第001回.md|第001回]]
```

**禁止**在正文中使用 bare `[[name]]` 链接，因为 Obsidian 可能解析到错误的文件（例如 `[[蔡元培]]` 同时存在于 characters/ 和 redology/）。

**例外**：同一目录内的页面可以用 bare link（如 characters/ 内互相引用）。

### 4.2 表格中的 wikilink

**已知陷阱**：Markdown 表格中 `|` 是列分隔符。wikilink 的别名分隔符 `|` 会冲突。

**当前策略**：统一使用转义 `[[path\|label]]`。但注意：
- 这在一些 Obsidian 版本中能正确渲染 wikilink
- 在另一些版本中，转义后的链接不可点击
- 如果遇到渲染问题，**将表格改为列表**（用 `- ` 前缀 + 全路径 link），更可靠

### 4.3 Block anchor 命名

```
^hlm-{回数}-{主题短名}
```

例如：
- `^hlm-003-baodai-chujian`（宝黛初见）
- `^hlm-005-taixu-dream`（太虚幻境）
- `^hlm-074-chaoyuan-daguanyuan`（抄检大观园）

链接格式：`[[texts/simplified/第003回.md#^hlm-003-baodai-chujian|第003回原文：宝黛初见]]`

## 5. 批量操作规则

### 5.1 扩写薄页（<25行 → 25-35行）

**步骤**：
1. 读取文件
2. 保留 frontmatter，更新 `updated` 为当前日期，`status` 设为 `curated-v2`
3. 保留已有 `## 相关回目` 或 `## 章节` section
4. 添加标准 section：
   - `## 事件经过` 或 `## 人物小传`（2-3句）
   - `## 叙事功能` 或 `## 关键关系`（2-3句）
   - `## 相关概念`（2个概念链接，全路径）
5. 写作语言：中文（简体），文学分析语气
6. 链接：概念用全路径 `[[...concepts/...|...]]`

### 5.2 创建新页面

1. 检查是否已有类似页面（避免重复，如 鸳鸯拒婚 vs 鸳鸯抗婚）
2. 从模板复制（`templates/`）或参照同类型成熟页面
3. 确保 frontmatter 完整（含 `created`、`updated`、`status`）
4. 添加至少 2 个入链（从相关人物/事件/概念页链入）

### 5.3 Agent 批量操作自检

Agent 每次批量操作后，**必须**确认：
- 所有新建页面 frontmatter 完整
- 所有修改页面 `updated` 日期已更新
- 没有引入 bare wikilinks（全路径优先）
- 没有引入 English-Chinese 混合（如 "also" 混入中文）
- 链接目标存在

## 6. 健康检查流程

**每次批量操作后运行**。

### Step 1: 断链检查

```bash
# 查找所有 wikilink 目标，验证文件存在
# 注意：跳过 00_Raw/（raw文件）和 simple name links（如 [[红楼梦]]）
# 重点检查：带路径的 [[path/name|label]] 链接
```

检查范围：所有章节页、人物页、事件页、概念页、红学页。

### Step 2: 占位符检查

搜索模式（排除 log.md、ROADMAP.md、templates/、00_Raw/）：
- `待补` / `待补充` / `待扩展` / `待完成`
- `TODO` / `todo`
- `暂无` / `占位` / `placeholder`
- `[[...待建]]`
- 空 section：`## 标题` 后只有空行

### Step 3: 薄页检查

```bash
# 找出所有 <25 行的非 Raw 页面
# 排除：chapters/（120回导读不需要扩写）、texts/simplified/（原文）、templates/
```

### Step 4: 过期数据检查

检查以下文件中计数是否与实际一致：
- `START_HERE.md` — 所有计数（人物、事件、概念、总文件、图片）
- `index.md` — 所有计数
- `outputs/红楼梦编译总评.md` — 表格中的文件数
- `ROADMAP.md` — 快照表格
- `queries/人物索引.md` — "收录 X 个条目"
- `queries/事件索引.md` — "收录 X 个事件"
- `queries/概念索引.md` — "收录 X 个概念"
- `outputs/红楼梦速读指南.md` — "X个全部人物/事件/概念"

### Step 5: 重复检查

搜索可能重复的事件/人物：
- 同名变体：鸳鸯拒婚 vs 鸳鸯抗婚
- 同一事件不同表述

## 7. 已知陷阱

### 陷阱 1: `\|` 转义歧义

**现象**：SCHEMA 规定表格中用 `\|` 转义，70+ 文件已应用。但 Obsidian 不同版本对 `\|` 的渲染行为不一致。

**应对**：如果 Obsidian 无法渲染表格中的 wikilink，将表格改为列表格式。

### 陷阱 2: bare `[[name]]` 链接歧义

**现象**：12 个文件使用 bare `[[红楼梦]]`、`[[蔡元培]]`、`[[脂批]]` 等。Obsidian 可能解析到 `redology/` 而非 `characters/`。

**应对**：正文一律用全路径。同一目录内可例外。

### 陷阱 3: 过期计数扩散

**现象**：人物数从 91→92→93→105，事件从 32→117→116→120，概念从 37→36→38，总文件从 627→626→629→644。多处引用不同步。

**应对**：新增/删除/合并页面后，**立即**更新 START_HERE、index、编译总评、ROADMAP、相关索引页中的计数。

### 陷阱 4: 事件页重复

**现象**：鸳鸯拒婚（v3, 49行）vs 鸳鸯抗婚（14行薄页）→ 同一事件两个页面。

**应对**：创建事件页前先搜索是否存在同名变体。保留质量更高的页面，删除或重定向重复项，更新所有引用。

### 陷阱 5: English 混入中文

**现象**：Agent 扩写时偶尔在中文段落中插入英文单词（如 "also" → `潘又安闻知司棋死讯后，also 以死相随。`）。

**应对**：批量操作后用 grep 搜索常见英文单词（also, the, is, are, this, that, for, to 等），确保中文 prose 中无英文。

### 陷阱 6: status 与内容不匹配

**现象**：`curated-v3` 的页面实际只有 `curated-v1` 的内容；`curated-v1` 的页面实际已是 `curated-v2`。

**应对**：每次扩写后根据实际内容调整 status，不保守也不拔高。

## 8. 待办与下一步

### 近期待办

| 优先级 | 任务 | 涉及范围 | 状态 |
|--------|------|----------|------|
| P1 | 重构 START_HERE.md — 按读者 Profile 组织入口 | 1 个文件 | ✅ 已完成 |
| P1 | 修正 START_HERE.md 中所有过期计数 | 1 个文件 | ✅ 已完成 |
| P2 | 重构 红楼梦主题导读.md — 从链接列表升级为有引导的专题分析 | 1 个文件 | ✅ 已完成 |
| P2 | 修复 bare wikilinks | ~80 个文件 | ✅ 已完成（跨目录 bare link 已修复：characters/ 17文件、events/ 20文件、outputs/ 1文件、families/ 5文件49个link；同目录内保留 bare link） |
| P3 | 5 个地点薄页扩写（绛芸轩、应天府、荣禧堂、贾家义学、青埂峰）| 5 个文件 | ✅ 已完成（17→30-33行） |
| P3 | 整体重编译 v2（编译总评 + 主题导读 + 速读指南统一更新）| 3-5 个文件 | ✅ 已完成（编译总评更新，主题导读升级，索引计数同步） |
| P1 | 断链修复（137→0）+ 新建10个缺失页面 | 全局 + 10个新文件 | ✅ 已完成（.png.md双后缀、entities/→characters/、缺失concepts/events/characters页面） |
| P2 | Frontmatter 补全（29个文件缺status） | 29 个文件 | ✅ 已完成（concepts/ 17、events/ 7、characters/ 4、index.md、SCHEMA.md） |
| P2 | compiled-v1 → curated-v1 升级 | 5 个文件 | ✅ 已完成（maps/ 2、timelines/ 3） |
| P3 | queries/ 索引页同步新条目 | 3 个索引页 | ✅ 已完成 |

### 完成标志

当以下全部达成时，基础质量阶段视为完成：
- [x] 断链 0
- [x] 占位符 0
- [x] 薄页 0（神话人物除外）
- [x] 所有计数同步（START_HERE、index、ROADMAP、编译总评、queries索引已统一）
- [x] 所有 bare wikilinks 修复（跨目录已修复；同目录内按规则保留 bare link）
- [x] START_HERE.md 按读者 Profile 重构
- [x] 所有 frontmatter 字段完整（title/type/book/status/tags）
- [x] 无 compiled-v1 状态（已升级为 curated-v1，templates 除外）

## 9. 文件变更日志
最近重大变更（详见 `log.md`）：

| 日期 | 变更 |
|------|------|
| 2026-05-02 | P2+P3完成：重构主题导读.md（链接列表→7大专题分析）；扩写5个地点薄页（17→30-33行）；修复~80个跨目录bare wikilinks（characters/ 17文件、events/ 20文件、families/ 5文件、outputs/ 1文件）；整体重编译v2（编译总评、索引计数同步） |
| 2026-05-02 | 重构 START_HERE.md 按读者 Profile（第一次读/重读/研究/查找）分入口 |
| 2026-05-02 | 创建 AGENTS.md（结构总览、质量标准、链接规则、批量操作规则、健康检查流程、已知陷阱） |
| 2026-05-02 | 批量扩写76个薄事件页（12-15→25-35行）；删除鸳鸯抗婚重复页；修复19个断链；修正编译总评/索引过期数据；修复潘又安英文混入 |
| 2026-05-01 | 10个红学家页扩写（24→49-61行）；28个薄人物页扩写（12-14→30-44行）；删除concepts/通灵宝玉，统一至motifs-symbols/；新增3张AI插图（贾母、袭人、香菱） |
| 2026-05-03 | P1断链修复（137→0）：修复图片链接双后缀、entities/→characters/、新建10页面；P3 frontmatter补全29文件+5个compiled-v1升级；计数同步（characters 105、events 120、concepts 38、total 644） |
