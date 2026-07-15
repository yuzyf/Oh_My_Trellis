<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/local-architecture/workflow.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 本地工作流系统（Local Workflow System）

`.trellis/workflow.md` 是用户项目内 Trellis 工作流的事实来源。AI 不需要看 Trellis 源码就能理解当前项目应如何推进任务；这份文件就够了。

## 文件职责（File Responsibilities）

`.trellis/workflow.md` 有三项职责：

1. **解释工作流阶段**：Plan、Execute、Finish。
2. **定义 skill 路由**：用户表达某类意图时，AI 应使用哪个 skill 或 agent。
3. **提供 workflow-state 提示块**：hook 可把当前状态对应的提示块注入对话。

## 当前阶段模型（Current Phase Model）

```text
Phase 1: Plan    -> clarify what to build, produce prd.md and required research
Phase 2: Execute -> implement against the PRD and specs, then check
Phase 3: Finish  -> final verification, preserve lessons, and wrap up
```

每个阶段包含编号步骤，例如 `1.3 Configure context`。这些编号不是 `task.json` 里的运行时字段，而是供 AI 与人阅读的工作流结构。

## Skill 路由（Skill Routing）

`workflow.md` 按平台能力区分路由：

- 支持 sub-agent 的平台：实现默认派发 `trellis-implement`，检查派发 `trellis-check`。
- 不支持 sub-agent 的平台：主会话阅读如 `trellis-before-dev` 等 skill，然后直接执行。

修改本地 AI 行为时，先更新 `workflow.md` 中的路由描述，再检查对应的平台 skill、command 或 agent 文件是否需要同步。

## Workflow-State 提示块（Workflow-State Prompt Blocks）

`workflow.md` 底部可包含如下状态块：

```text
[workflow-state:no_task]
...
[/workflow-state:no_task]
```

Hook 根据当前任务状态选择正确的块并注入对话。常见状态包括：

| State | Meaning |
| --- | --- |
| `no_task` | 当前会话没有活动任务。 |
| `planning` | 任务仍在需求、调研或上下文配置阶段。 |
| `in_progress` | 任务已进入实现与检查。 |
| `completed` | 任务完成，等待收尾或归档。 |

若用户要改「没有任务时是否创建任务」「何时可跳过任务创建」「是否必须用 sub-agent」等策略，编辑这些状态块及其上方的路由表。

## 本地修改模式（Local Modification Patterns）

常见改动：

| Goal | Edit point |
| --- | --- |
| 增加一个阶段 | 更新 Phase Index、阶段正文、路由与状态块。 |
| 修改任务创建策略 | 更新 `no_task` 状态块与 Phase 1 描述。 |
| 修改默认实现/检查路径 | 更新 Phase 2 与 skill 路由。 |
| 修改收尾流程 | 更新 Phase 3 与 `finish-work` 相关描述。注意当前拆分：Phase 3.4 = AI 驱动的代码提交（分批、经用户确认），Phase 3.5 = `/finish-work`（归档 + 记录会话）。若工作树有未提交改动，`/finish-work` 会拒绝运行。 |
| 修改平台差异 | 更新按平台分组的路由描述。 |

编辑后让 AI 重读 `.trellis/workflow.md`；不要假定旧对话里的流程仍然有效。

## 与平台文件的关系（Relationship To Platform Files）

`workflow.md` 是本地工作流的语义中心，但各平台也可有自己的入口文件：

- skills，例如 `trellis-brainstorm` 与 `trellis-check`。
- commands/prompts/workflows，例如 continue 与 finish-work。
- hooks，例如 session-start 或 workflow-state 注入。

若只改 `workflow.md`，平台入口文件可能仍是旧表述。当用户要改「AI 实际会做什么」时，也要检查相关平台目录。
