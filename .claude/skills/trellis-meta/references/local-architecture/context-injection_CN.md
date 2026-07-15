<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/local-architecture/context-injection.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 本地上下文注入系统（Local Context Injection System）

Trellis 上下文注入的目标，是让 AI 在正确时机读到正确文件，而不是依赖模型记忆。在用户项目里，注入由 `.trellis/` 脚本与平台 hooks、agents、skills 共同完成。

## 注入的上下文类型（Injected Context Types）

| Type | Source | Purpose |
| --- | --- | --- |
| session context | `.trellis/scripts/get_context.py` | 当前开发者、git 状态、活动任务、活动任务列表、journal、packages。 |
| workflow context | `.trellis/workflow.md` | 当前 Trellis 流程与下一步动作。 |
| spec context | `.trellis/spec/` + 任务 JSONL | 实现/检查时必须遵守的规范。 |
| task context | `.trellis/tasks/<task>/prd.md`、`design.md`、`implement.md`、`research/` | 当前任务的需求、设计、执行计划与调研。 |
| platform context | 平台 hooks/settings/agents | 让不同 AI 工具通过各自机制读取上述文件。 |

## session-start

支持 session-start 的平台会在会话开始、清空、压缩或收到类似事件时注入 Trellis 概览。注入内容通常包括：

- 工作流摘要。
- 当前任务状态。
- 活动任务列表。
- spec 索引路径。
- 开发者身份与 git 状态。

若用户觉得新会话里 AI 不知道当前任务，先检查该平台的 session-start hook 或等价机制是否已安装并在运行。

## workflow-state

workflow-state 是围绕每轮用户输入注入的轻量提示。它根据当前任务状态，从 `.trellis/workflow.md` 选择一块内容，例如 `no_task`、`planning`、`in_progress` 或 `completed`。

若用户要改「某一状态下 AI 下一步该做什么」，先编辑 `.trellis/workflow.md` 中对应的状态块。

## 子智能体上下文（sub-agent context）

Implement 与 check agent 需要任务上下文。Trellis 有两种加载模式：

1. **hook push**：agent 启动前，平台 hook 注入 jsonl 引用的文件，以及存在时的 `prd.md`、`design.md`、`implement.md`。
2. **agent pull**：agent 定义要求 agent 启动后自行读取活动任务、jsonl 上下文与任务产物。

两种模式下，任务目录中的 JSONL 都是 spec/调研上下文的清单。任务产物按此顺序单独读取：`prd.md` -> 若有则 `design.md` -> 若有则 `implement.md`。

## JSONL 阅读规则（JSONL Reading Rules）

`implement.jsonl` 与 `check.jsonl` 每行一个 JSON 对象：

```jsonl
{"file": ".trellis/spec/backend/index.md", "reason": "Backend rules"}
```

读取方应跳过没有 `file` 字段的种子行。配置 JSONL 时，AI 应只纳入 spec/调研文件，不要预先登记即将修改的代码文件。

## 活动任务与上下文键（Active Task And Context Key）

活动任务状态位于 `.trellis/.runtime/sessions/`，按会话隔离。Hook 会尝试从平台事件、环境变量、transcript 路径或 `TRELLIS_CONTEXT_ID` 解析上下文键。

若 shell 命令看不到同一上下文键，`task.py current --source` 可能报告没有活动任务。此时应检查平台是否把会话身份传入 shell，而不是手写一个全局当前任务文件。

## 本地可定制点（Local Customization Points）

| Need | Edit location |
| --- | --- |
| 修改 session-start 注入内容 | 平台的 `session-start` hook 或 plugin 文件。 |
| 修改每轮 workflow-state 规则 | `.trellis/workflow.md` 中的 `[workflow-state:STATUS]` 块。平台 workflow-state hook 会按原文解析这些块，不内嵌回退文案。 |
| 修改子智能体如何读上下文 | 平台 agent 定义、`inject-subagent-context` hook，或 agent prelude。 |
| 修改 JSONL 校验/展示 | `.trellis/scripts/common/task_context.py`。 |
| 修改活动任务解析 | `.trellis/scripts/common/active_task.py`。 |

修改上下文注入时，验证两件事：新会话能看到正确任务；子智能体能看到正确的任务产物/spec/调研。
