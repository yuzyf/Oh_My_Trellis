> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

---
name: gitnexus-impact-analysis
description: "在用户想知道改动会破坏什么，或在改代码前需要安全分析时使用。示例：\"Is it safe to change X?\"、\"What depends on this?\"、\"What will break?\""
---

# 用 GitNexus 做影响分析（Impact Analysis）

## 何时使用

- 「改这个函数安全吗？」
- 「我改 X 会破坏什么？」
- 「给我看爆炸半径」
- 「谁在用这段代码？」
- 做非平凡代码改动之前
- 提交之前——理解你的改动影响什么

## 工作流

```
1. impact({target: "X", direction: "upstream"})  → 谁依赖它
2. READ gitnexus://repo/{name}/processes                   → 检查受影响的执行流
3. detect_changes()                               → 把当前 git 改动映射到受影响流
4. 评估风险并报告给用户
```

> 若提示 "Index is stale" → 在终端运行 `node .gitnexus/run.cjs analyze`。

## 清单

```
- [ ] impact({target, direction: "upstream"}) 找依赖方
- [ ] 先审 d=1 项（这些 WILL BREAK）
- [ ] 检查高置信度（>0.8）依赖
- [ ] READ processes 检查受影响执行流
- [ ] detect_changes() 做提交前检查
- [ ] 评估风险等级并报告用户
```

## 理解输出

| 深度 | 风险等级       | 含义                  |
| ----- | ---------------- | ------------------------ |
| d=1   | **WILL BREAK**   | 直接调用方/导入方 |
| d=2   | LIKELY AFFECTED  | 间接依赖    |
| d=3   | MAY NEED TESTING | 传递影响       |

## 风险评估

| 受影响                       | 风险     |
| ------------------------------ | -------- |
| <5 个符号，少量进程      | LOW      |
| 5-15 个符号，2-5 个进程    | MEDIUM   |
| >15 个符号或很多进程  | HIGH     |
| 关键路径（auth、payments） | CRITICAL |

## 工具

**impact** — 符号爆炸半径的主工具：

```
impact({
  target: "validateUser",
  direction: "upstream",
  minConfidence: 0.8,
  maxDepth: 3
})

→ d=1 (WILL BREAK):
  - loginHandler (src/auth/login.ts:42) [CALLS, 100%]
  - apiMiddleware (src/api/middleware.ts:15) [CALLS, 100%]

→ d=2 (LIKELY AFFECTED):
  - authRouter (src/routes/auth.ts:22) [CALLS, 95%]
```

**detect_changes** — 基于 git-diff 的影响分析：

```
detect_changes({scope: "staged"})

→ Changed: 5 symbols in 3 files
→ Affected: LoginFlow, TokenRefresh, APIMiddlewarePipeline
→ Risk: MEDIUM
```

## 示例：「改 validateUser 会破坏什么？」

```
1. impact({target: "validateUser", direction: "upstream"})
   → d=1: loginHandler, apiMiddleware (WILL BREAK)
   → d=2: authRouter, sessionManager (LIKELY AFFECTED)

2. READ gitnexus://repo/my-app/processes
   → LoginFlow and TokenRefresh touch validateUser

3. Risk: 2 direct callers, 2 processes = MEDIUM
```
