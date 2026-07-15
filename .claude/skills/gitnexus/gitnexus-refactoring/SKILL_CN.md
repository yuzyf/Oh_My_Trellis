> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

---
name: gitnexus-refactoring
description: "在用户想安全地重命名、抽取、拆分、移动或重组代码时使用。示例：\"Rename this function\"、\"Extract this into a module\"、\"Refactor this class\"、\"Move this to a separate file\""
---

# 用 GitNexus 重构（Refactoring with GitNexus）

## 何时使用

- 「安全重命名这个函数」
- 「抽成一个模块」
- 「拆分这个 service」
- 「移到新文件」
- 任何涉及重命名、抽取、拆分或重组代码的任务

## 工作流

```
1. impact({target: "X", direction: "upstream"})  → 映射全部依赖方
2. query({query: "X"})                            → 找涉及 X 的执行流
3. context({name: "X"})                           → 看全部入边/出边引用
4. 规划更新顺序：interfaces → implementations → callers → tests
```

> 若提示 "Index is stale" → 在终端运行 `node .gitnexus/run.cjs analyze`。

## 清单

### 重命名符号

```
- [ ] rename({symbol_name: "oldName", new_name: "newName", dry_run: true}) — 预览全部编辑
- [ ] 审阅 graph 编辑（高置信）与 ast_search 编辑（仔细审）
- [ ] 满意后：rename({..., dry_run: false}) — 应用编辑
- [ ] detect_changes() — 确认只有预期文件变更
- [ ] 对受影响进程跑测试
```

### 抽取模块

```
- [ ] context({name: target}) — 看全部入边/出边引用
- [ ] impact({target, direction: "upstream"}) — 找全部外部调用方
- [ ] 定义新模块接口
- [ ] 抽取代码，更新 imports
- [ ] detect_changes() — 确认影响范围
- [ ] 对受影响进程跑测试
```

### 拆分函数/服务

```
- [ ] context({name: target}) — 理解全部被调用方
- [ ] 按职责给被调用方分组
- [ ] impact({target, direction: "upstream"}) — 映射需要更新的调用方
- [ ] 创建新函数/服务
- [ ] 更新调用方
- [ ] detect_changes() — 确认影响范围
- [ ] 对受影响进程跑测试
```

## 工具

**rename** — 自动化多文件重命名：

```
rename({symbol_name: "validateUser", new_name: "authenticateUser", dry_run: true})
→ 12 edits across 8 files
→ 10 graph edits (high confidence), 2 ast_search edits (review)
→ Changes: [{file_path, edits: [{line, old_text, new_text, confidence}]}]
```

**impact** — 先映射全部依赖方：

```
impact({target: "validateUser", direction: "upstream"})
→ d=1: loginHandler, apiMiddleware, testUtils
→ Affected Processes: LoginFlow, TokenRefresh
```

**detect_changes** — 重构后验证你的改动：

```
detect_changes({scope: "all"})
→ Changed: 8 files, 12 symbols
→ Affected processes: LoginFlow, TokenRefresh
→ Risk: MEDIUM
```

**cypher** — 自定义引用查询：

```cypher
MATCH (caller)-[:CodeRelation {type: 'CALLS'}]->(f:Function {name: "validateUser"})
RETURN caller.name, caller.filePath ORDER BY caller.filePath
```

## 风险规则

| 风险因素         | 缓解                                |
| ------------------- | ----------------------------------------- |
| 很多调用方（>5）   | 用 rename 做自动更新 |
| 跨区域引用     | 之后用 detect_changes 验证范围  |
| 字符串/动态引用 | 用 query 找它们               |
| 外部/公开 API | 正确做版本与弃用            |

## 示例：把 `validateUser` 重命名为 `authenticateUser`

```
1. rename({symbol_name: "validateUser", new_name: "authenticateUser", dry_run: true})
   → 12 edits: 10 graph (safe), 2 ast_search (review)
   → Files: validator.ts, login.ts, middleware.ts, config.json...

2. Review ast_search edits (config.json: dynamic reference!)

3. rename({symbol_name: "validateUser", new_name: "authenticateUser", dry_run: false})
   → Applied 12 edits across 8 files

4. detect_changes({scope: "all"})
   → Affected: LoginFlow, TokenRefresh
   → Risk: MEDIUM — run tests for these flows
```
