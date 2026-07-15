> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.claude/skills/gitnexus/gitnexus-guide/SKILL.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

---
name: gitnexus-guide
description: "GitNexus 总览与路由指南：何时用哪个 GitNexus skill，以及核心工具/资源速查。在用户提到 GitNexus、代码智能图谱，或不确定该用 exploring / debugging / impact / refactoring 中哪一个时使用。"
---

# GitNexus 指南（Guide）

GitNexus 为仓库构建本地代码智能图谱（符号、调用、进程、簇），供探索、调试、影响分析与安全重构使用。

## 先决条件

1. 仓库已用 GitNexus 分析（见 `gitnexus-cli`）
2. MCP / 资源可读：`gitnexus://repo/{name}/context`
3. 若索引过期：`node .gitnexus/run.cjs analyze`

## 按意图选 Skill

| 用户意图 | 使用 skill |
| --- | --- |
| 索引 / 状态 / wiki / 清理 | `gitnexus-cli` |
| 理解区域如何工作 | `gitnexus-exploring` |
| 追踪 bug / 错误来源 | `gitnexus-debugging` |
| 改之前评估爆炸半径 | `gitnexus-impact-analysis` |
| 安全重命名 / 抽取 / 拆分 | `gitnexus-refactoring` |

## 工具速查

| 工具 | 给你什么 |
| ---------------- | ------------------------------------------------------------------------ |
| `query`          | 按进程分组的代码智能——与某概念相关的执行流 |
| `context`        | 符号 360° 视图——分类引用、参与的进程  |
| `impact`         | 符号爆炸半径——深度 1/2/3 会断什么及置信度         |
| `detect_changes` | 基于 git-diff 的影响——当前改动影响什么                    |
| `rename`         | 多文件协调重命名，编辑带置信度标签               |
| `cypher`         | 原始图查询（先读 `gitnexus://repo/{name}/schema`）           |
| `list_repos`     | 发现已索引仓库                                                   |

## 资源速查

轻量读取（约 100-500 tokens）用于导航：

| 资源                                       | 内容                                   |
| ---------------------------------------------- | ----------------------------------------- |
| `gitnexus://repo/{name}/context`               | 统计、过期检查                    |
| `gitnexus://repo/{name}/clusters`              | 全部功能区域与内聚分 |
| `gitnexus://repo/{name}/cluster/{clusterName}` | 区域成员                              |
| `gitnexus://repo/{name}/processes`             | 全部执行流                       |
| `gitnexus://repo/{name}/process/{processName}` | 逐步轨迹                        |
| `gitnexus://repo/{name}/schema`                | 供 Cypher 使用的图 schema                   |

## 图 Schema

**节点：** File, Function, Class, Interface, Method, Community, Process  
**边（经 CodeRelation.type）：** CALLS, IMPORTS, EXTENDS, IMPLEMENTS, DEFINES, MEMBER_OF, STEP_IN_PROCESS

```cypher
MATCH (caller)-[:CodeRelation {type: 'CALLS'}]->(f:Function {name: "myFunc"})
RETURN caller.name, caller.filePath
```
