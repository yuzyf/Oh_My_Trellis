<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/customize-local/change-context-loading.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 修改本地上下文加载（Change Local Context Loading）

上下文加载决定 AI 何时读取 workflow、task、spec、research、workspace 与 git status。当用户说「AI 不知道当前任务」「agent 没读 specs」或「上下文太多/太少」时读本页。

## 先读这些文件（Read These Files First）

1. `.trellis/workflow.md`
2. `.trellis/scripts/get_context.py`
3. `.trellis/scripts/common/session_context.py`
4. `.trellis/scripts/common/task_context.py`
5. `.trellis/scripts/common/active_task.py`
6. 当前平台 hooks 或 agent 文件
7. 当前任务的 `implement.jsonl` / `check.jsonl`

## 上下文来源（Context Sources）

| Source | Purpose |
| --- | --- |
| `.trellis/workflow.md` | 工作流与下一步提示。 |
| `.trellis/tasks/<task>/prd.md` | 当前任务需求。 |
| `.trellis/tasks/<task>/design.md` | 复杂任务的技术设计。 |
| `.trellis/tasks/<task>/implement.md` | 复杂任务的执行计划。 |
| `.trellis/tasks/<task>/implement.jsonl` | 实现前要读的 spec/research。 |
| `.trellis/tasks/<task>/check.jsonl` | 检查时要读的 spec/research。 |
| `.trellis/spec/` | 项目 specs。 |
| `.trellis/workspace/` | 会话记录。 |
| git status | 当前工作树变更。 |

## 常见需求与修改点（Common Needs And Edit Points）

| Need | Edit point |
| --- | --- |
| 新会话注入更多/更少信息 | `session_context.py` 或平台 `session-start` hook。 |
| 改每次用户输入的提示 | `.trellis/workflow.md` 中的 `[workflow-state:STATUS]` 块。`inject-workflow-state` hook 只做解析，原样读取该块。 |
| Agent 没读 specs | 任务 JSONL、agent prelude、`inject-subagent-context` hook。 |
| 活跃任务丢失 | `active_task.py` 与平台 session 身份传播。 |
| 改 JSONL 校验规则 | `task_context.py`。 |

## JSONL 规则（JSONL Rules）

`implement.jsonl` / `check.jsonl` 是关键的上下文加载接口：

```jsonl
{"file": ".trellis/spec/backend/index.md", "reason": "Backend conventions"}
{"file": ".trellis/tasks/04-28-x/research/api.md", "reason": "API research"}
```

只收录 spec/research 文件。不要把将要修改的代码文件放进这些清单；实现时 agents 自己会读代码。

## 修改会话上下文（Change Session Context）

若用户希望每次新会话都能看到更多项目状态，编辑：

- `.trellis/scripts/common/session_context.py`
- 对应平台的 `session-start` hook

上下文不能无限膨胀。优先注入索引与路径，让 AI 按需再读，而不是把整份 docs 都塞进去。

## 修改子 Agent 上下文（Change Sub-Agent Context）

平台分两类：

- **Hook push**：hook 在 agent 启动前注入内容。
- **Agent pull**：agent 文件要求启动后读取 task/JSONL。

改行为时先判断平台属于哪一类，不要在错误层改。

## 注意（Notes）

- 活跃任务是 session 级状态，不是全局单例。
- 不要用手改 `.trellis/.runtime/sessions/` 来“修复”业务状态。
- 改上下文后用 `task.py current --source` 与 `task.py validate` 做验证。
