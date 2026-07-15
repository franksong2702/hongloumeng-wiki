---
title: 红楼梦 Wiki 维护机制
created: 2026-07-08
updated: 2026-07-14
type: maintenance-guide
book: 红楼梦
status: active
tags: [hongloumeng, maintenance, health-check, obsidian]
---

# 红楼梦 Wiki 维护机制

> 这是当前维护 SOP。动态数量只看[[02_Learn/08_book-wikis/红楼梦/WIKI_STATUS.md|自动状态页]]；2026-07-08 至 2026-07-12 的阶段过程保存在[[02_Learn/08_book-wikis/红楼梦/WIKI_MAINTENANCE_REVIEW.md|维护收尾报告]]。

## 1. 维护原则

1. **先验证，后修改**：先确认当前错误类型，再决定是否动正文。
2. **一次只处理一个问题面**：内容、元数据、链接、脚本和站点机制分批处理。
3. **动态事实只有一个来源**：数量写入 `WIKI_STATUS.md`，其他文档只链接，不手抄。
4. **结构健康不等于文学正确**：脚本负责发现机械问题，人物判断、红学争议和文本解释仍需人工复核。
5. **发布内容必须可复核**：原文有公开来源，事件有正文锚点，研究页区分三层证据。

## 2. 两种运行环境

### Obsidian Vault 副本

当前 Wiki 可能位于不带 `.git` 的 iCloud Vault 中。此时：

- 可以运行全部内容与构建检查；
- `generate_wiki_status.py` 使用 `log.md` 最新发布日期，保证跨天可重复；
- 不报告分支、提交、工作区或部署状态；
- 不执行 GitHub Pages 部署。

### 发布仓库

只有以下命令成功时，才进入 Git 工作流：

```bash
git rev-parse --show-toplevel
```

在发布仓库中，状态页日期取待提交状态或最新提交日期；读者内容发生变化时必须同步更新 `log.md`，再提交和部署。

## 3. 统计口径

| 口径 | 定义 |
|---|---|
| 成品 Wiki Markdown | 发布与阅读网络中的 Markdown；排除 `raw/`、维护报告和脚本目录 |
| raw Markdown | `raw/` 下本地可选的采集证据 |
| 成品 + raw | 本地管理口径，不代表发布仓库文件数 |
| 维护/审查 Markdown | 维护机制、阶段报告与收尾报告 |

具体数量不在此维护，见[[02_Learn/08_book-wikis/红楼梦/WIKI_STATUS.md|自动状态页]]。

## 4. 四个发布闸门

在 Wiki 根目录运行。

### 4.1 源 Wiki 严格健康检查

```bash
python3 scripts/wiki_health_check.py --strict
```

覆盖：

- frontmatter 必填字段；
- `sources:` 本地路径与繁体原文公开来源；
- Wikilink、Markdown 本地链接和表格链接；
- 章节—事件定位；
- 原文锚点落点、唯一性、引用和事件覆盖；
- 占位句、薄页、关键章节编辑层；
- 研究页证据分层；
- 地点与人物关系阅读面；
- 动态数量、版本一致性、发布日志和人物事件线治理快照。

### 4.2 状态页一致性

修改动态数量或发布批次后：

```bash
python3 scripts/generate_wiki_status.py
python3 scripts/generate_wiki_status.py --check
```

第一条显式生成，第二条只读核对。不要手工修改自动状态页中的数量。

### 4.3 外部来源检查

```bash
python3 scripts/external_link_check.py --strict
```

- 404/410 是明确失效，严格模式失败；
- 403、429、TLS、5xx 和超时列为 REVIEW，需要人工判断；
- 外链检查通过不代表来源学术质量已经可靠。

### 4.4 静态站严格构建

```bash
python3 scripts/mkdocs_build_check.py
```

该命令重建 `_mkdocs_build/`，转换 Wikilink、图片、block anchor 与导航，然后执行 `mkdocs build --strict`。构建产物可随时再生，不进入内容编辑。

## 5. 标准维护流程

```text
1. 运行严格健康检查与状态页核对
2. 明确本批唯一目标和文件范围
3. 修改内容并更新 frontmatter.updated
4. 若影响读者内容、阅读路径或站点机制，更新 log.md
5. 重新生成 WIKI_STATUS.md
6. 运行四个发布闸门
7. 涉及人物事件线时运行两个人物线脚本
8. 记录结果和未验证项
```

人物线专项命令：

```bash
python3 scripts/character_event_line_review.py
python3 scripts/character_event_reverse_link_check.py
```

## 6. 来源与 Raw 边界

- `texts/traditional/` 是可发布的繁体原文层，每回 `sources:` 指向公开 Wikisource 页面。
- `texts/simplified/` 是简体阅读与锚点层，不覆盖繁体原文。
- `raw/` 如存在，只作为本地采集证据，保持只读；发布仓库和静态站不能依赖它。
- `sources:` 中引用本地 Wiki 页面时使用真实 Vault 路径；引用公开材料时使用 URL。
- 任何新增研究来源都要落到实际吸收观点的页面，而不是只写在总综述里。

## 7. 常见失败与处理

| 失败 | 处理 |
|---|---|
| `frontmatter_source_local_missing` | 修正或删除不存在的本地来源路径 |
| `traditional_source_external_missing` | 为繁体原文补公开来源 URL |
| `wikilink_broken` | 修正目标，不创建空壳页绕过错误 |
| `source_anchor_reference_missing` | 修正锚点名或把锚点放回真实正文段落 |
| `event_source_anchor_missing` | 为事件补对应回目的精确正文锚点 |
| `self_description_*` | 更新自动状态页或删除重复手写数量 |
| `version_mismatch` | 对齐 README、SCHEMA 与 index 版本 |
| `release_log_*` | 在同一发布批次更新 `log.md` |
| MkDocs strict failure | 修改源文件或转换脚本，不手改构建产物 |

## 8. 内容维护策略

当四个闸门均通过时，后续只做目标明确的小切片：

- 一批关键回目的人工精编；
- 一条人物—事件—原文—概念阅读链；
- 一组外部来源的人工复核；
- 一个红学判断的事实与观点分层；
- 一个明确的站点可用性问题。

不再使用“全库扩写”“统一文风”“为清指标补链接”作为维护任务。

## 9. 完成证据模板

```text
改动范围: <文件 / 页面类型 / 阅读链>
验证命令: <原样命令>
返回结果: <exit code / ERROR / WARN / 关键统计>
证据路径: <日志、状态页或审查笔记>
环境边界: <Vault 副本 / Git 发布仓库>
未验证项: <如无则写无>
```
