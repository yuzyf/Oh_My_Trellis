<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/local-architecture/task-system.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 本地任务系统（Local Task System）

Trellis 任务系统全部存放在用户项目的 `.trellis/tasks/` 下。每个任务是一个目录，包含需求、上下文、调研、状态与关系信息。

## 任务目录结构（Task Directory Structure）

```text
.trellis/tasks/
├── 04-28-example-task/
│   ├── task.json
│   ├── prd.md
│   ├── design.md
│   ├── implement.md
│   ├── implement.jsonl
│   ├── check.jsonl
│   └── research/
└── archive/
    └── 2026-04/
```

| File | Purpose |
| --- | --- |
| `task.json` | 任务元数据：状态、负责人、优先级、分支、父子任务等字段。 |
| `prd.md` | 需求、约束与验收标准。轻量任务可以只有 PRD。 |
| `design.md` | 复杂任务的技术设计：边界、契约、数据流、兼容性、权衡。 |
| `implement.md` | 复杂任务的执行计划：有序清单、验证命令、评审门禁、回滚点。 |
| `implement.jsonl` | implement agent 必须先读的 spec/调研文件列表。 |
| `check.jsonl` | check agent 必须先读的 spec/调研文件列表。 |
| `research/` | 调研产物。复杂结论不应只留在聊天里。 |

## `task.json`

`task.json` 记录任务状态与元数据。常见字段：

| Field | Meaning |
| --- | --- |
| `id` / `name` / `title` | 任务身份与标题。 |
| `status` | 状态，如 `planning`、`in_progress`、`review` 或 `completed`。 |
| `priority` | `P0`、`P1`、`P2`、`P3`。 |
| `creator` / `assignee` | 创建者与负责人。 |
| `package` | monorepo 中的目标包；可为空。 |
| `branch` / `base_branch` | 工作分支与 PR 目标分支。 |
| `children` / `parent` | 父子任务关系。 |
| `commit` / `pr_url` | 完成后的 commit 与 PR 信息。 |
| `meta` | 扩展字段。 |

## 父子任务树（Parent / Child Task Trees）

父子任务关系用于工作结构。父任务把相关交付物归到同一组源需求下；它不是依赖调度器，也不能替代子任务自己的规划产物。

当请求有多个可独立验收的交付物时使用父任务。父任务拥有：

- 源需求与面向用户的范围。
- 子任务地图及其责任边界。
- 跨子任务的验收标准与最终集成评审。

子任务用于可独立走完规划、实现、检查与归档的交付物。若一个子任务依赖另一个，把依赖写进子任务的 `prd.md` / `implement.md`；不要靠树中位置暗示顺序。

创建新子任务：

```bash
python3 ./.trellis/scripts/task.py create "<child title>" --slug <child-slug> --parent <parent-dir>
```

关联或解除已有任务：

```bash
python3 ./.trellis/scripts/task.py add-subtask <parent-dir> <child-dir>
python3 ./.trellis/scripts/task.py remove-subtask <parent-dir> <child-dir>
```

父任务上的 `children` 是历史列表。子任务归档后，Trellis 仍在父任务中保留该子任务名，这样像 `[2/3 done]` 的进度在已完成子任务进入 `archive/` 后仍有意义。

AI 不应把阶段编号当作任务状态。任务进度主要由 `status`、产物是否存在（`prd.md`，可选 `design.md` / `implement.md`）、sub-agent 模式下是否配置了 JSONL 上下文，以及 `workflow.md` 中的阶段描述共同决定。

## 活动任务（Active Task）

用户看到的是「当前任务」，但 Trellis 按会话存储活动任务状态。

```text
.trellis/.runtime/sessions/<context-key>.json
```

`task.py start` 把任务路径写入当前会话的运行时会话文件。`task.py current --source` 显示当前任务及其来源。不同 AI 窗口可指向不同任务，而不会互相覆盖。

若平台或 shell 环境没有稳定的会话身份，`task.py start` 可能无法设置活动任务。AI 应阅读错误、检查平台 hook/会话环境，不要回退到共享的全局指针。

## JSONL 上下文（JSONL Context）

`implement.jsonl` 与 `check.jsonl` 是子智能体应先读的上下文清单。它们不替代 `implement.md`；`implement.md` 是人可读的执行计划。

格式：

```jsonl
{"file": ".trellis/spec/cli/backend/index.md", "reason": "Backend conventions"}
{"file": ".trellis/tasks/04-28-example/research/api.md", "reason": "API research"}
```

规则：

- 纳入 spec 与调研文件。
- 不要纳入即将修改的代码文件。
- 不要把聊天里的临时结论当作唯一上下文。
- 种子行没有 `file` 字段；它们只提示 AI 填入真实条目。

## 常用命令（Common Commands）

```bash
python3 ./.trellis/scripts/task.py create "<title>" --slug <slug>
python3 ./.trellis/scripts/task.py start <task>
python3 ./.trellis/scripts/task.py current --source
python3 ./.trellis/scripts/task.py add-context <task> implement <file> <reason>
python3 ./.trellis/scripts/task.py validate <task>
python3 ./.trellis/scripts/task.py finish
python3 ./.trellis/scripts/task.py archive <task>
```

修改任务系统时，AI 应优先用脚本命令维护结构。仅当脚本覆盖不到时，才直接编辑 JSON/Markdown。

## 本地可定制点（Local Customization Points）

| Need | Edit location |
| --- | --- |
| 修改默认任务模板 | `.trellis/scripts/common/task_store.py` 与任务创建说明。 |
| 修改状态语义 | `.trellis/workflow.md`、workflow-state hook 逻辑与任务使用约定。 |
| 增加任务生命周期动作 | `.trellis/config.yaml` 中的 `hooks.after_*`。 |
| 修改上下文规则 | `.trellis/workflow.md` 中的规划产物指引，以及相关平台 agent/hook 说明。 |
| 修改归档策略 | `.trellis/scripts/common/task_store.py` / `task_utils.py`。 |

这些都是用户项目中的本地文件。除非用户要贡献上游，否则不要默认去改 Trellis CLI 源码。
