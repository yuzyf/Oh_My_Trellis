<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/claude-code/scripts.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# Claude Code 脚本（Claude Code Scripts）

依赖 Claude Code CLI 与 hook 系统的脚本。

---

## 概述（Overview）

这些脚本需要：
- `claude` CLI 命令
- 用于上下文注入的 hook 系统
- 用于会话持久化的 `--resume`

```
.trellis/scripts/
├── common/
│   ├── worktree.py         # Worktree utilities
│   └── registry.py         # Agent registry
│
└── multi_agent/            # Multi-Session scripts
    ├── plan.py             # Launch Plan agent
    ├── start.py            # Start worktree agent
    ├── status.py           # Monitor agents
    ├── create_pr.py        # Create pull request
    └── cleanup.py          # Cleanup worktree
```

---

## Multi-Session 脚本（Multi-Session Scripts）

### `multi_agent/plan.py`

启动 Plan Agent 创建任务配置。

```bash
python3 .trellis/scripts/multi_agent/plan.py \
  --name <task-name> \
  --type <dev-type> \
  --requirement "<requirement text>"
```

**选项：**
- `--name` - 任务 slug
- `--type` - `frontend`、`backend`、`fullstack`
- `--requirement` - 任务描述

**动作：**
1. 创建任务目录
2. 通过 `claude` 启动 Plan Agent
3. Plan Agent 可 REJECT 不清晰需求
4. 创建 `prd.md`、`task.json`、JSONL 文件

---

### `multi_agent/start.py`

在新 worktree 中启动 agent。

```bash
python3 .trellis/scripts/multi_agent/start.py <task-dir>
```

**动作：**
1. 从 `task.json` 读取分支名
2. 创建 git worktree：
   ```bash
   git worktree add -b <branch> ../worktrees/<branch>
   ```
3. 按 `worktree.yaml` 的 copy 列表复制文件
4. 把任务目录复制到 worktree
5. 运行 `post_create` 命令
6. 设置会话作用域活动任务
7. 启动 Claude Dispatch Agent：
   ```bash
   claude -p --agent dispatch \
     --session-id <uuid> \
     --dangerously-skip-permissions \
     --output-format stream-json \
     "Start the pipeline"
   ```
8. 注册到 `registry.json`

---

### `multi_agent/status.py`

监控运行中的会话。

```bash
# Overview of all sessions
python3 .trellis/scripts/multi_agent/status.py

# Detailed view
python3 .trellis/scripts/multi_agent/status.py --detail <task-name>

# Watch mode (auto-refresh)
python3 .trellis/scripts/multi_agent/status.py --watch <task-name>

# View logs
python3 .trellis/scripts/multi_agent/status.py --log <task-name>

# Show registry
python3 .trellis/scripts/multi_agent/status.py --registry
```

**输出：**
```
Active Sessions:
┌──────────────┬──────────┬────────────────┬──────────┬───────────┐
│ Task         │ Status   │ Phase          │ Elapsed  │ Files     │
├──────────────┼──────────┼────────────────┼──────────┼───────────┤
│ add-login    │ Running  │ 2/4 (check)    │ 15m 32s  │ 5 changed │
│ fix-api      │ Stopped  │ 1/4 (implement)│ 8m 15s   │ 2 changed │
└──────────────┴──────────┴────────────────┴──────────┴───────────┘
```

---

### `multi_agent/create_pr.py`

从 worktree 变更创建 pull request。

```bash
python3 .trellis/scripts/multi_agent/create_pr.py [--dry-run]
```

**动作：**
1. 暂存变更：`git add -A`
2. 排除 workspace：`git reset .trellis/workspace/`
3. 按 conventional 格式提交
4. 推送到远端
5. 用 `gh pr create --draft` 创建 Draft PR
6. 用 `pr_url` 更新 task.json

---

### `multi_agent/cleanup.py`

清理已完成的 worktrees。

```bash
# Specific worktree
python3 .trellis/scripts/multi_agent/cleanup.py <branch-name>

# All merged worktrees
python3 .trellis/scripts/multi_agent/cleanup.py --merged

# All worktrees (with confirmation)
python3 .trellis/scripts/multi_agent/cleanup.py --all
```

**动作：**
1. 把任务归档到 `.trellis/tasks/archive/YYYY-MM/`
2. 从 registry 移除
3. 移除 worktree：`git worktree remove <path>`
4. 可选删除分支

---

## 公共工具（Common Utilities）

### `common/worktree.py`

Worktree 管理工具。

```python
from common.worktree import (
    read_worktree_config,  # Read worktree.yaml
    get_worktree_path,     # Get path for branch
    create_worktree,       # Create new worktree
    remove_worktree,       # Remove worktree
)
```

### `common/registry.py`

跟踪运行中会话的 agent registry。

```python
from common.registry import (
    registry_add_agent,       # Add agent to registry
    registry_remove_by_id,    # Remove by agent ID
    registry_remove_by_worktree,  # Remove by path
    registry_search_agent,    # Search by pattern
    registry_list_agents,     # List all agents
)
```

**Registry 文件：** `.trellis/workspace/<developer>/.agents/registry.json`

```json
{
  "agents": [
    {
      "id": "feature-add-login",
      "worktree_path": "/abs/path/to/worktrees/feature/add-login",
      "pid": 12345,
      "started_at": "2026-01-31T10:30:00",
      "task_dir": ".trellis/tasks/01-31-add-login-taosu"
    }
  ]
}
```

---

## Claude CLI 用法（Claude CLI Usage）

### Agent 模式（Agent Mode）

```bash
claude --agent dispatch "Start the pipeline"
```

### 打印模式（非交互）（Print Mode）

```bash
claude -p "Do something"
```

### 会话恢复（Session Resume）

```bash
claude --resume <session-id>
```

### 自动化模式（Automation Mode）

```bash
claude --dangerously-skip-permissions -p "..."
```

### JSON 输出（JSON Output）

```bash
claude --output-format stream-json -p "..."
```

---

## 恢复已停止会话（Resuming Stopped Sessions）

```bash
# Find session info
python3 .trellis/scripts/multi_agent/status.py --detail <task-name>

# Resume in worktree
cd ../worktrees/feature/task-name
claude --resume <session-id>
```
