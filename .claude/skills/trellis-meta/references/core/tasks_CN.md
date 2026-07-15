<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/core/tasks.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 任务系统（Task System）

用分阶段执行跟踪工作项。

---

## 目录结构（Directory Structure）

```
.trellis/tasks/
├── {MM-DD-slug}/               # Active task directories
│   ├── task.json               # Metadata, phases, branch
│   ├── prd.md                  # Requirements document
│   ├── design.md               # Technical design for complex tasks
│   ├── implement.md            # Execution plan for complex tasks
│   ├── implement.jsonl         # Context for implement phase
│   ├── check.jsonl             # Context for check phase
│   └── debug.jsonl             # Context for debug phase
│
└── archive/                    # Completed tasks
    └── {YYYY-MM}/
        └── {task-dir}/
```

---

## 任务目录命名（Task Directory Naming）

格式：`{MM-DD}-{slug}`

示例：
- `01-31-add-login`
- `02-01-fix-api-bug`

---

## task.json

任务元数据与 workflow 配置。

```json
{
  "id": "add-login",
  "name": "add-login",
  "title": "Add user login",
  "description": "",
  "status": "planning",
  "dev_type": null,
  "scope": null,
  "priority": "P2",
  "creator": "taosu",
  "assignee": "taosu",
  "createdAt": "2026-01-31",
  "completedAt": null,
  "branch": null,
  "base_branch": "main",
  "worktree_path": null,
  "current_phase": 0,
  "next_action": [
    {"phase": 1, "action": "implement"},
    {"phase": 2, "action": "check"},
    {"phase": 3, "action": "finish"},
    {"phase": 4, "action": "create-pr"}
  ],
  "commit": null,
  "pr_url": null,
  "subtasks": [],
  "children": [],
  "parent": null,
  "relatedFiles": [],
  "notes": "",
  "meta": {}
}
```

### 字段（Fields）

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Slug 标识符 |
| `name` | string | 与 id 相同的 slug |
| `title` | string | 人类可读任务标题 |
| `description` | string | 任务描述 |
| `status` | string | `planning`、`in_progress`、`completed`、`rejected` |
| `dev_type` | string\|null | `frontend`、`backend`、`fullstack`、`test`、`docs` |
| `scope` | string\|null | PR 标题用 scope |
| `priority` | string | `P0`、`P1`、`P2`、`P3` |
| `creator` | string | 创建任务的开发者 |
| `assignee` | string | 被指派的开发者 |
| `createdAt` | string | 创建日期（YYYY-MM-DD） |
| `completedAt` | string\|null | 完成日期 |
| `branch` | string\|null | Git 分支名 |
| `base_branch` | string | 合并目标分支 |
| `worktree_path` | string\|null | Git worktree 路径（multi-agent） |
| `current_phase` | number | 当前 workflow 阶段 |
| `next_action` | array | Workflow 阶段列表 |
| `commit` | string\|null | Commit hash |
| `pr_url` | string\|null | Pull request URL |
| `subtasks` | array | 已弃用（旧 bootstrap 格式） |
| `children` | string[] | 子任务目录名 |
| `parent` | string\|null | 父任务目录名 |
| `relatedFiles` | string[] | 相关文件路径 |
| `notes` | string | 自由文本备注 |
| `meta` | object | 集成用可扩展元数据（如 `linear_id`、`jira_ticket`） |

---

## prd.md

任务需求文档。

```markdown
# Add User Login

## Goal
Implement user authentication with email/password.

## Requirements
- Login form with email and password fields
- Form validation
- API endpoint for authentication

## Acceptance Criteria
- [ ] User can log in with valid credentials
- [ ] Error shown for invalid credentials

## Research References
- Link to relevant research/spec notes
```

---

## JSONL 上下文文件（JSONL Context Files）

列出每个阶段要注入为上下文的文件。

### 格式（Format）

```jsonl
{"file": ".trellis/spec/cli/backend/index.md", "reason": "Backend guidelines"}
{"file": "src/services/auth.ts", "reason": "Existing auth service"}
{"file": ".trellis/tasks/01-31-add-login/prd.md", "reason": "Requirements"}
```

### 文件（Files）

| File | Phase | Purpose |
|------|-------|---------|
| `implement.jsonl` | implement | 开发 specs、要遵循的模式 |
| `check.jsonl` | check | 质量标准、审查 specs |
| `debug.jsonl` | debug | 调试上下文、错误报告 |

---

## Session 作用域的活跃任务（Session-Scoped Active Task）

### `.trellis/.runtime/sessions/<session-key>.json`

为一个 AI session/window 存储活跃任务。

```json
{
  "current_task": ".trellis/tasks/01-31-add-login"
}
```

### 设置活跃任务

```bash
python3 .trellis/scripts/task.py start <task-dir>
```

### 清除当前任务

```bash
python3 .trellis/scripts/task.py finish
```

---

## Task CLI

### 创建任务

```bash
python3 .trellis/scripts/task.py create "Task name" --slug task-slug
python3 .trellis/scripts/task.py create "Child task" --slug child --parent <parent-dir>
```

选项：`--assignee <name>`、`--priority P0|P1|P2|P3`、`--description "text"`、`--parent <dir>`

### 列出任务

```bash
python3 .trellis/scripts/task.py list
python3 .trellis/scripts/task.py list --mine
python3 .trellis/scripts/task.py list --status planning
```

带 `parent` 的任务会缩进显示在父任务下。
父任务显示子任务进度：`(planning) [2/3 done]`。

### 开始任务

```bash
python3 .trellis/scripts/task.py start <task-dir>
```

### 结束（清除当前任务）

```bash
python3 .trellis/scripts/task.py finish
```

### 初始化上下文

```bash
python3 .trellis/scripts/task.py init-context <task-dir> <dev-type>
```

Dev types：`frontend`、`backend`、`fullstack`、`test`、`docs`

### 添加子任务

```bash
python3 .trellis/scripts/task.py add-subtask <parent-dir> <child-dir>
```

把已有任务链接为另一任务的子任务。若子任务已有父任务则报错。

### 移除子任务

```bash
python3 .trellis/scripts/task.py remove-subtask <parent-dir> <child-dir>
```

移除两个任务之间的父子链接。

### 归档任务

```bash
python3 .trellis/scripts/task.py archive <task-dir>
```

归档子任务时，会自动从父任务的 `children` 列表移除。
归档父任务时，会清除所有子任务中的 `parent` 字段。

### 其他命令

```bash
python3 .trellis/scripts/task.py set-branch <dir> <branch>
python3 .trellis/scripts/task.py set-base-branch <dir> <branch>
python3 .trellis/scripts/task.py set-scope <dir> <scope>
python3 .trellis/scripts/task.py add-context <dir> <jsonl> <path> [reason]
python3 .trellis/scripts/task.py validate <dir>
python3 .trellis/scripts/task.py list-context <dir>
python3 .trellis/scripts/task.py list-archive [month]
python3 .trellis/scripts/task.py create-pr [dir] [--dry-run]
```

---

## get_context.py

显示含任务信息的会话运行时。

```bash
python3 .trellis/scripts/get_context.py                      # Default text (full context)
python3 .trellis/scripts/get_context.py --json                # Default JSON
python3 .trellis/scripts/get_context.py --mode record         # Record text (my tasks focus)
python3 .trellis/scripts/get_context.py --mode record --json  # Record JSON
```

`--mode` 控制内容范围，`--json` 控制输出格式。可组合。

---

## Workflow 阶段（Workflow Phases）

标准阶段推进：

```
1. implement  →  Write code
2. check      →  Review and fix
3. finish     →  Final verification
4. create-pr  →  Create pull request (Multi-Agent only)
```

### 自定义阶段（Custom Phases）

修改 task.json 中的 `next_action`：

```json
"next_action": [
  {"phase": 1, "action": "research"},
  {"phase": 2, "action": "implement"},
  {"phase": 3, "action": "check"}
]
```

---

## 最佳实践（Best Practices）

1. **Session 本地聚焦** - 在每个 AI session/window 中使用 `task.py start`
2. **清晰的 PRDs** - 写具体、可测试的需求
3. **相关上下文** - JSONL 只收录需要的文件
4. **归档已完成** - 保持任务目录干净
5. **使用 subtasks** - 把复杂任务拆成可并行的子任务
