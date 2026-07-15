---
title: 红楼梦 Wiki 当前状态
created: 2026-07-12
updated: 2026-07-15
type: meta
book: 红楼梦
status: generated
tags: [hongloumeng, maintenance, generated]
---

# 红楼梦 Wiki 当前状态

> 本页由 `scripts/generate_wiki_status.py` 生成。数量变化后必须重新生成；Vault 与发布仓库统一使用 `log.md` 最新发布日期，只有日志不可用时才回退到 Git 日期，GitHub Actions 会拒绝不一致的状态页。

## 管理口径

| 口径 | 数量 |
|---|---:|
| 成品 Wiki Markdown | 831 |
| 维护/审查 Markdown | 4 |

`raw/` 是本地可选的采集证据，不属于公共发布仓库或静态站依赖，因此不纳入这张可复现的发布状态表；本地管理时可与成品数分开统计。

## 读者内容

| 模块 | Markdown |
|---|---:|
| 章节导读 | 120 |
| 简体原文 | 120 |
| 繁体原文 | 120 |
| 人物 | 106 |
| 事件 | 181 |
| 概念 | 38 |
| 地点 | 21 |
| 诗词 | 12 |
| 红学与研究 | 53 |
| 背景 | 7 |
| 图谱 | 6 |
| 时间线 | 3 |
| 家族 | 5 |
| 意象 | 6 |
| 查询索引 | 9 |
| 输出产品 | 14 |

## 质量闸门

- 严格健康检查：`python3 scripts/wiki_health_check.py --strict`
- 状态页一致性：`python3 scripts/generate_wiki_status.py --check`
- 外部来源检查：`python3 scripts/external_link_check.py --strict`
- 静态站构建：`python3 scripts/mkdocs_build_check.py`

## 阅读入口

- [[02_Learn/08_book-wikis/红楼梦/index.md|站点首页]]
- [[02_Learn/08_book-wikis/红楼梦/START_HERE.md|完整阅读入口]]
- [[02_Learn/08_book-wikis/红楼梦/log.md|发布日志]]
- [[02_Learn/08_book-wikis/红楼梦/redology/证据使用规范.md|证据使用规范]]
