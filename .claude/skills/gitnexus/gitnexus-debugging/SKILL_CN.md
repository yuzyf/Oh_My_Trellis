> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.claude/skills/gitnexus/gitnexus-debugging/SKILL.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

---
name: gitnexus-debugging
description: "在用户调试 bug、追踪错误，或询问某事为何失败时使用。示例：\"Why is X failing?\"、\"Where does this error come from?\"、\"Trace this bug\""
---

# 用 GitNexus 调试（Debugging with GitNexus）

## 何时使用

- 「这个函数为什么失败？」
- 「追踪这个错误从哪来」
- 「谁调用了这个方法？」
- 「这个 endpoint 返回了意外结果」
- 任何需要沿调用图往上游/下游追踪的调试任务

## 工作流

```
1. context({name: "suspectFunction"})  → 看调用方与被调用方
2. query({query: "error-related concept"}) → 找相关执行流
3. READ gitnexus://repo/{name}/process/{name} → 逐步追踪
4. impact({target: "suspectFunction", direction: "upstream"}) → 谁依赖它
```

> 若提示 "Index is stale" → 在终端运行 `node .gitnexus/run.cjs analyze`。

## 清单

```
- [ ] context() 看目标符号的入边/出边引用
- [ ] query() 找相关执行流
- [ ] 读取 process 资源做逐步追踪
- [ ] impact() 映射依赖面
- [ ] 用发现到的调用链缩小根因
```

## 工具

**context** — 某个符号的 360° 视图：

```
context({name: "validateUser"})
→ Incoming: loginHandler CALLS, apiMiddleware CALLS
→ Outgoing: checkToken CALLS, db.query CALLS
→ Processes: LoginFlow, TokenRefresh
```

**query** — 按概念找执行流：

```
query({query: "login validation error"})
→ 相关进程与符号簇
```

**impact** — 上游依赖（谁会受影响）：

```
impact({target: "validateUser", direction: "upstream"})
→ d=1 调用方会直接断
```

## 示例：「validateUser 为什么失败？」

```
1. context({name: "validateUser"})
   → 调用方：loginHandler, apiMiddleware
   → 被调用：checkToken, userRepo.find

2. query({query: "user validation"})
   → LoginFlow 包含 validateUser 作为步骤 3

3. READ process/LoginFlow
   → 逐步：parseRequest → loadUser → validateUser → issueToken

4. 在 validateUser 与其被调用方处读源码；对照测试与错误日志
```
