<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/core/files.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# Trellis 文件参考（Trellis File Reference）

`.trellis/` 目录中全部文件的完整参考。

---

## 目录结构（Directory Structure）

```
.trellis/
├── .developer              # Developer identity (gitignored)
├── .runtime/               # Session-scoped runtime state (gitignored)
├── .current-task           # Legacy ignored pointer; not an active-task source
├── .ralph-state.json       # Ralph Loop state (gitignored)
├── .template-hashes.json   # Template version tracking
├── .version                # Installed Trellis version
├── .gitignore              # Git ignore rules
├── workflow.md             # Main workflow documentation
├── worktree.yaml           # Multi-session configuration
│
├── workspace/              # Developer workspaces
├── tasks/                  # Task tracking
├── spec/                   # Coding guidelines
└── scripts/                # Automation scripts
```

---

## 根文件（Root Files）

### `.developer`

**用途**：存储当前开发者身份。

**创建者**：`init_developer.py`

**格式**：纯文本，单行开发者名。

```
taosu
```

**Gitignored**：是——每台机器有自己的身份。

---

### `.runtime/sessions/<session-key>.json`

**用途**：为一个 AI session/window 存储活跃任务状态。

**创建者**：`task.py start <task-dir>`

**格式**：JSON 运行时上下文。

```json
{
  "current_task": ".trellis/tasks/01-31-add-login-taosu",
  "current_run": null,
  "platform": "claude",
  "last_seen_at": "2026-04-27T00:00:00Z"
}
```

**Gitignored**：是——每个 session/window 有自己的活跃任务。

**使用者**：
- Hooks 经 `common.active_task` 解析
- Scripts 用它做活跃任务操作

### `.current-task`

**用途**：旧版 Trellis 遗留的被忽略指针。

**活跃任务行为**：不作为回退读写。当前 Trellis 仅使用 `.runtime/sessions/<session-key>.json`。

---

### `.ralph-state.json`

**用途**：跟踪 Ralph Loop 迭代状态。

**创建者**：`ralph-loop.py`（仅 Claude Code）

**格式**：JSON

```json
{
  "task": ".trellis/tasks/01-31-add-login",
  "iteration": 2,
  "started_at": "2026-01-31T10:30:00"
}
```

**Gitignored**：是——运行时状态。

**字段**：
| Field | Type | Description |
|-------|------|-------------|
| `task` | string | 任务目录路径 |
| `iteration` | number | 当前迭代（1-5） |
| `started_at` | ISO date | 循环开始时间 |

---

### `.template-hashes.json`

**用途**：为 `trellis update` 跟踪模板文件版本。

**创建者**：`trellis init` 或 `trellis update`

**格式**：文件路径到 SHA-256 hash 的 JSON 对象。

```json
{
  ".trellis/workflow.md": "028891d1fe839a266...",
  ".claude/hooks/session-start.py": "0a9899e80f6bfe15...",
  ".claude/commands/start.md": "d1276dcbff880299..."
}
```

**使用者**：
- `trellis update` - 检测哪些文件被修改
- 决定文件可自动更新还是需要冲突解决

**行为**：
- 文件 hash 与模板一致 → 可安全更新
- 文件 hash 不同 → 用户已改，需要手动合并

---

### `.version`

**用途**：跟踪已安装的 Trellis CLI 版本。

**创建者**：`trellis init` 或 `trellis update`

**格式**：纯文本，semver 版本字符串。

```
0.3.0-beta.5
```

**使用者**：
- `trellis update` - 判断是否需要更新
- 版本不匹配检测

---

### `.gitignore`

**用途**：定义要从 git 排除的文件。

**默认内容**：
```gitignore
# Developer identity (local only)
.developer

# Legacy current task pointer
.current-task

# Session runtime state
.runtime/

# Ralph Loop state
.ralph-state.json

# Agent runtime files
.agents/
.agent-log
.agent-runner.sh
.session-id

# Task directory runtime files
.plan-log

# Atomic update temp files
*.tmp
.backup-*
*.new

# Python cache
**/__pycache__/
**/*.pyc
```

---

### `workflow.md`

**用途**：面向开发者与 AI 的主 workflow 文档。

**创建者**：`trellis init`

**内容小节**：
1. Quick Start 指南
2. Workflow 总览
3. 会话开始流程
4. 开发流程
5. 会话结束
6. 文件说明
7. 最佳实践

**注入者**：`session-start.py` hook（Claude Code）

**对 Cursor**：会话开始时手动阅读。

---

### `worktree.yaml`

**用途**：配置 Multi-Session 与 Ralph Loop。

**创建者**：`trellis init`

**格式**：YAML

```yaml
worktree_dir: ../worktrees
copy:
  - .trellis/.developer
  - .env
post_create:
  - npm install
verify:
  - pnpm lint
  - pnpm typecheck
```

→ 详见 `claude-code/worktree-config.md`。

---

## 运行时文件（Runtime Files, Gitignored）

### `.agents/`

**用途**：Multi-Session 的 agent registry。

**位置**：`.trellis/workspace/{developer}/.agents/`

**内容**：跟踪运行中 agents 的 `registry.json`。

---

### `.session-id`

**用途**：存储用于 resume 的 Claude Code session ID。

**创建者**：Multi-Session `start.py`

**格式**：UUID 字符串。

---

### `.agent-log`

**用途**：Agent 执行日志。

**创建者**：Multi-Session 脚本。

---

### `.plan-log`

**用途**：Plan Agent 执行日志。

**位置**：任务目录。

---

## 目录（Directories）

### `workspace/`

带 journals 与 indexes 的开发者 workspaces。

→ 见 `core/workspace.md`

### `tasks/`

带 PRDs 与 session 文件的任务目录。

→ 见 `core/tasks.md`

### `spec/`

编码指南与规格。

→ 见 `core/specs.md`

### `scripts/`

自动化脚本。

→ 见 `core/scripts.md` 与 `claude-code/scripts.md`

---

## 模板文件（Template Files）

这些文件由 `trellis update` 管理：

| File | Purpose |
|------|---------|
| `.trellis/workflow.md` | Workflow 文档 |
| `.trellis/worktree.yaml` | Multi-session 配置 |
| `.trellis/.gitignore` | Git ignore 规则 |
| `.claude/hooks/*.py` | Hook 脚本 |
| `.claude/commands/*.md` | Slash commands |
| `.claude/agents/*.md` | Agent 定义 |
| `.cursor/commands/*.md` | Cursor commands（镜像） |

**更新行为**：
1. 与 `.template-hashes.json` 比较文件 hash
2. 若未改 → 自动更新
3. 若已改 → 创建 `.new` 文件供手动合并
4. 成功更新后刷新 hashes

---

## 文件生命周期（File Lifecycle）

### 由 `trellis init` 创建

```
.trellis/
├── .template-hashes.json
├── .version
├── .gitignore
├── workflow.md
├── worktree.yaml
├── spec/
│   ├── frontend/
│   ├── backend/
│   └── guides/
└── scripts/
```

### 运行时创建

```
.trellis/
├── .developer           # init_developer.py
├── .runtime/sessions/   # task.py start
├── .current-task        # legacy ignored file, not active-task source
├── .ralph-state.json    # ralph-loop.py
├── workspace/{dev}/     # init_developer.py
│   ├── index.md
│   ├── journal-1.md
│   └── .agents/
└── tasks/{task}/        # task.py create
    ├── task.json
    ├── prd.md
    └── *.jsonl
```

### 清理

```
# After task completion
.trellis/tasks/{task}/ → .trellis/tasks/archive/YYYY-MM/

# After worktree removal
.agents/registry.json entries removed
```
