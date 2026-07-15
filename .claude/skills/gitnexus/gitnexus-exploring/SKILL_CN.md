> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.claude/skills/gitnexus/gitnexus-exploring/SKILL.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

---
name: gitnexus-exploring
description: "在用户探索代码库、理解某区域如何工作，或在编码前做摸底时使用。示例：\"How does X work?\"、\"Explain the auth flow\"、\"Show me the codebase structure\""
---

# 用 GitNexus 探索（Exploring with GitNexus）

## 何时使用

- 「X 怎么工作？」
- 「解释认证流程」
- 「代码库结构是什么样？」
- 「找到处理支付的代码」
- 在非平凡改动前建立心智模型

## 工作流

```
1. READ gitnexus://repo/{name}/context     → 总览与过期检查
2. READ gitnexus://repo/{name}/clusters    → 功能区域
3. query({query: "concept"})               → 与概念相关的执行流
4. context({name: "SymbolName"})           → 符号 360° 视图
5. READ process / cluster 资源做深挖
```

> 若提示 "Index is stale" → 在终端运行 `node .gitnexus/run.cjs analyze`。

## 清单

```
- [ ] 读 context 资源确认索引健康
- [ ] 读 clusters 理解功能区域
- [ ] query 找与任务相关的进程
- [ ] context 深入关键符号
- [ ] 需要时沿 process 轨迹逐步走
```

## 工具与资源

| 资源 / 工具 | 用途 |
| --- | --- |
| `gitnexus://repo/{name}/context` | 统计与过期 |
| `gitnexus://repo/{name}/clusters` | 功能区域与内聚分 |
| `gitnexus://repo/{name}/processes` | 执行流列表 |
| `query` | 按概念检索代码智能 |
| `context` | 符号入边/出边与所属进程 |
| `cypher` | 自定义图查询 |

## 示例：「认证怎么工作？」

```
1. READ context → 仓库已索引、未过期
2. READ clusters → 找到 Auth 相关 community
3. query({query: "authentication login"})
4. context({name: "loginHandler"})
5. READ process/LoginFlow 逐步追踪
```
