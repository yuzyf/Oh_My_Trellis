<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/claude-code/multi-session.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# Multi-Session 参考（Multi-Session Reference）

用 Git worktrees 实现并行隔离会话的文档。

---

## 概述（Overview）

Multi-Session 用 Git worktrees 实现**并行、隔离的开发会话**。每个会话在自己的目录与分支上运行。

**关键区分**：
- **Multi-Agent** = 当前目录中的多个 agents（dispatch → implement → check）
- **Multi-Session** = 独立 worktrees 中的并行会话（本文）

---

## 何时使用 Multi-Session（When to Use Multi-Session）

| Scenario | Use Multi-Session? |
|----------|-------------------|
| 当前分支上的常规任务 | No - 用 Multi-Agent |
| 长任务，还想并行做其它事 | Yes |
| 多个独立任务并行 | Yes |
| 任务需要干净隔离环境 | Yes |
| 快速修复或小改动 | No |

---

## 架构（Architecture）

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         MAIN REPOSITORY                                     │
│                         (your current directory)                            │
│                                                                             │
│  /trellis:parallel → Configure task → start.py                             │
│                                           │                                 │
│                                           │ Creates worktree               │
│                                           │ Starts agent                   │
│                                           ▼                                 │
└───────────────────────────────────────────┼─────────────────────────────────┘
                                            │
              ┌─────────────────────────────┼─────────────────────────────────┐
              │                             │                                 │
              ▼                             ▼                                 ▼
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│ WORKTREE 1           │  │ WORKTREE 2           │  │ WORKTREE 3           │
│ feature/add-login    │  │ feature/user-profile │  │ fix/api-bug          │
│                      │  │                      │  │                      │
│ ┌──────────────────┐ │  │ ┌──────────────────┐ │  │ ┌──────────────────┐ │
│ │ Dispatch Agent   │ │  │ │ Dispatch Agent   │ │  │ │ Dispatch Agent   │ │
│ │       ↓          │ │  │ │       ↓          │ │  │ │       ↓          │ │
│ │ Implement Agent  │ │  │ │ Implement Agent  │ │  │ │ Implement Agent  │ │
│ │       ↓          │ │  │ │       ↓          │ │  │ │       ↓          │ │
│ │ Check Agent      │ │  │ │ Check Agent      │ │  │ │ Check Agent      │ │
│ │       ↓          │ │  │ │       ↓          │ │  │ │       ↓          │ │
│ │ create_pr.py     │ │  │ │ create_pr.py     │ │  │ │ create_pr.py     │ │
│ └──────────────────┘ │  │ └──────────────────┘ │  │ └──────────────────┘ │
│                      │  │                      │  │                      │
│ Session: abc123      │  │ Session: def456      │  │ Session: ghi789      │
│ PID: 12345           │  │ PID: 12346           │  │ PID: 12347           │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘

Location: ../worktrees/  (default)
```

---

## Git Worktree

### 什么是 Worktree？（What is a Worktree?）

Git worktrees 允许一个仓库有多个工作目录：

```
/project/                              # Main repo (main branch)
/project/../worktrees/                 # Default: ../worktrees
├── feature/add-login/                # Worktree 1 (own branch)
├── feature/user-profile/             # Worktree 2 (own branch)
└── fix/api-bug/                      # Worktree 3 (own branch)
```

### 收益（Benefits）

| Benefit | Description |
|---------|-------------|
| **True isolation** | 每会话独立文件系统 |
| **Own branch** | 每个 worktree 在自己的分支上 |
| **Parallel execution** | 多个 agents 同时工作 |
| **Clean state** | 干净起步，互不干扰 |
| **Session persistence** | 各自有 `.session-id` 可恢复 |
| **Easy cleanup** | 删除 worktree = 清掉一切 |

---

## 配置（Configuration）

### worktree.yaml

位置：`.trellis/worktree.yaml`

```yaml
# Where worktrees are created (relative to project)
# Default: ../worktrees
worktree_dir: ../worktrees

# Files to copy to each worktree (default: [])
copy:
  - .trellis/.developer      # Developer identity
  - .env                      # Environment variables
  - .env.local                # Local overrides

# Commands after worktree creation (default: [])
post_create:
  - npm install               # Install dependencies
  # - pnpm install --frozen-lockfile

# Verification commands for Ralph Loop (default: [])
verify:
  - pnpm lint
  - pnpm typecheck
```

### 任务配置（Task Configuration）

每个会话需要已配置的任务：

```json
// task.json
{
  "branch": "feature/add-login",     // Required for worktree
  "base_branch": "main",
  "worktree_path": null,             // Set by start.py
  "current_phase": 0,
  "next_action": [
    {"phase": 1, "action": "implement"},
    {"phase": 2, "action": "check"},
    {"phase": 3, "action": "finish"},
    {"phase": 4, "action": "create-pr"}
  ]
}
```

---

## 脚本（Scripts）

### start.py - 启动会话（Start Session）

创建 worktree 并启动 agent。

```bash
python3 .trellis/scripts/multi_agent/start.py <task-dir>
```

**Actions**:
1. 从 `task.json` 读取分支名
2. 创建 git worktree：
   ```bash
   git worktree add -b <branch> ../trellis-worktrees/<branch>
   ```
3. 按 `worktree.yaml` 的 copy 列表复制文件
4. 把任务目录复制到 worktree
5. 运行 `post_create` hooks
6. 为 worktree 运行设置会话作用域活动任务
7. 启动 Claude Dispatch Agent：
   ```bash
   claude -p --agent dispatch \
     --session-id <uuid> \
     --dangerously-skip-permissions \
     --output-format stream-json \
     --verbose "Start the pipeline"
   ```
8. 注册到 `registry.json`

**Example**:
```bash
python3 .trellis/scripts/multi_agent/start.py .trellis/tasks/01-31-add-login-taosu
# Output: Started agent in ../trellis-worktrees/feature/add-login
```

---

### status.py - 监控会话（Monitor Sessions）

查看全部运行中会话。

```bash
# Overview
python3 .trellis/scripts/multi_agent/status.py

# Detailed view
python3 .trellis/scripts/multi_agent/status.py --detail <task-name>

# Watch mode
python3 .trellis/scripts/multi_agent/status.py --watch <task-name>

# View logs
python3 .trellis/scripts/multi_agent/status.py --log <task-name>

# Show registry
python3 .trellis/scripts/multi_agent/status.py --registry
```

**Output**:
```
Active Sessions:
┌──────────────┬──────────┬────────────────┬──────────┬───────────┐
│ Task         │ Status   │ Phase          │ Elapsed  │ Files     │
├──────────────┼──────────┼────────────────┼──────────┼───────────┤
│ add-login    │ Running  │ 2/4 (check)    │ 15m 32s  │ 5 changed │
│ fix-api      │ Stopped  │ 1/4 (implement)│ 8m 15s   │ 2 changed │
└──────────────┴──────────┴────────────────┴──────────┴───────────┘

Resume stopped sessions:
  cd ../trellis-worktrees/feature/fix-api && claude --resume <session-id>
```

---

### create_pr.py - 创建 PR（Create PR）

从 worktree 变更创建 PR。

```bash
python3 .trellis/scripts/multi_agent/create_pr.py [--dry-run]
```

**Actions**:
1. 暂存变更：`git add -A`
2. 排除：`git reset .trellis/workspace/`
3. 提交：`feat(<scope>): <task-name>`
4. 推送到远端
5. 创建 Draft PR：`gh pr create --draft`
6. 更新 task.json：`status: "completed"`、`pr_url`

---

### cleanup.py - 移除 Worktrees（Remove Worktrees）

完成后清理。

```bash
# Specific worktree
python3 .trellis/scripts/multi_agent/cleanup.py <branch-name>

# All merged worktrees
python3 .trellis/scripts/multi_agent/cleanup.py --merged

# All worktrees (with confirmation)
python3 .trellis/scripts/multi_agent/cleanup.py --all
```

**Actions**:
1. 把任务归档到 `.trellis/tasks/archive/YYYY-MM/`
2. 从 registry 移除
3. 移除 worktree：`git worktree remove <path>`
4. 可选删除分支

---

### plan.py - 自动配置任务（Auto-Configure Task）

启动 Plan Agent 创建任务配置。

```bash
python3 .trellis/scripts/multi_agent/plan.py \
  --name <task-slug> \
  --type <backend|frontend|fullstack> \
  --requirement "<description>"
```

**Plan Agent**:
1. 评估需求（可 REJECT）
2. 调用 Research Agent
3. 创建 `prd.md`
4. 配置 `task.json`
5. 初始化 JSONL 文件

---

## 会话注册表（Session Registry）

跟踪全部运行中会话。

**Location**: `.trellis/workspace/<developer>/.agents/registry.json`

```json
{
  "agents": [
    {
      "id": "feature-add-login",
      "worktree_path": "/abs/path/to/trellis-worktrees/feature/add-login",
      "pid": 12345,
      "started_at": "2026-01-31T10:30:00",
      "task_dir": ".trellis/tasks/01-31-add-login-taosu"
    }
  ]
}
```

**API** (`common/registry.py`):
```python
registry_add_agent(agent_id, worktree_path, pid, task_dir)
registry_remove_by_id(agent_id)
registry_remove_by_worktree(worktree_path)
registry_search_agent(pattern)
registry_list_agents()
```

---

## 完整工作流（Complete Workflow）

### 1. 配置任务（Configure Task）

```bash
# Create task
python3 .trellis/scripts/task.py create "Add login" --slug add-login

# Configure
python3 .trellis/scripts/task.py init-context <task-dir> fullstack
python3 .trellis/scripts/task.py set-branch <task-dir> feature/add-login

# Write prd.md
# ...
```

### 2. 启动会话（Start Session）

```bash
python3 .trellis/scripts/multi_agent/start.py <task-dir>
```

### 3. 监控（Monitor）

```bash
python3 .trellis/scripts/multi_agent/status.py --watch add-login
```

### 4. 完成后（After Completion）

```bash
# PR auto-created
# Review on GitHub, merge

# Cleanup
python3 .trellis/scripts/multi_agent/cleanup.py feature/add-login
```

---

## 并行执行（Parallel Execution）

启动多个会话：

```bash
# Session 1
python3 .trellis/scripts/multi_agent/start.py .trellis/tasks/01-31-add-login

# Session 2 (immediately)
python3 .trellis/scripts/multi_agent/start.py .trellis/tasks/01-31-fix-api

# Session 3
python3 .trellis/scripts/multi_agent/start.py .trellis/tasks/01-31-update-docs

# Monitor all
python3 .trellis/scripts/multi_agent/status.py
```

各自独立运行：
- 自己的 worktree
- 自己的分支
- 自己的 Claude 进程
- 自己的 registry 条目

---

## 恢复会话（Resuming Sessions）

若会话停止：

```bash
# Find session info
python3 .trellis/scripts/multi_agent/status.py --detail <task-name>

# Resume
cd ../trellis-worktrees/feature/task-name
claude --resume <session-id>
```

---

## Ralph Loop

会话中面向 Check Agent 的质量强制。

**Mechanism**:
1. Check Agent 完成
2. SubagentStop hook 触发
3. `ralph-loop.py` 运行验证命令
4. 全部通过 → 允许停止
5. 任一失败 → 阻塞，继续 agent

**Constants**:
| Constant | Value | Description |
|----------|-------|-------------|
| `MAX_ITERATIONS` | 5 | 最大循环次数 |
| `STATE_TIMEOUT_MINUTES` | 30 | 状态超时 |
| Command timeout | 120s | 每条验证命令 |

**Configuration** (`worktree.yaml`):
```yaml
verify:
  - pnpm lint
  - pnpm typecheck
```

**State** (`.trellis/.ralph-state.json`):
```json
{
  "task": ".trellis/tasks/01-31-add-login",
  "iteration": 2,
  "started_at": "2026-01-31T10:30:00"
}
```

**Limits**: 最多 5 次迭代（`MAX_ITERATIONS`）、30 分钟超时（`STATE_TIMEOUT_MINUTES`）、每命令 120s

---

## 故障排查（Troubleshooting）

### 会话无法启动（Session Not Starting）

1. 检查 `worktree.yaml` 是否存在
2. 确认分支名不存在
3. 检查 `post_create` hooks
4. 查看 start.py 输出

### 会话卡住（Session Stuck）

1. 检查 Ralph Loop 迭代次数（最多 5）
2. 核对 `verify` 命令
3. 手动运行验证命令
4. 查看 `.trellis/.ralph-state.json`

### Worktree 问题（Worktree Issues）

```bash
# Force remove
git worktree remove --force <path>

# Prune stale
git worktree prune

# List all
git worktree list
```

### Registry 不同步（Registry Out of Sync）

```bash
# View
python3 .trellis/scripts/multi_agent/status.py --registry

# Manual edit
vim .trellis/workspace/<dev>/.agents/registry.json
```
