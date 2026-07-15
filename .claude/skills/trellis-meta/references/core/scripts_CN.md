<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/core/scripts.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 核心脚本（Core Scripts）

用于 Trellis 自动化的平台无关 Python 脚本。

---

## 总览（Overview）

这些脚本在所有平台工作——它们只读写文件，不依赖 Claude Code 的 hook 系统。

```
.trellis/scripts/
├── common/                 # Shared utilities
│   ├── paths.py
│   ├── developer.py
│   ├── task_utils.py
│   ├── phase.py
│   └── git_context.py
│
├── init_developer.py       # Initialize developer
├── get_developer.py        # Get developer name
├── get_context.py          # Get session runtime
├── task.py                 # Task management CLI
└── add_session.py          # Record session
```

---

## 开发者脚本（Developer Scripts）

### `init_developer.py`

初始化开发者身份。

```bash
python3 .trellis/scripts/init_developer.py <name>
```

**创建：**
- `.trellis/.developer`
- `.trellis/workspace/<name>/`
- `.trellis/workspace/<name>/index.md`
- `.trellis/workspace/<name>/journal-1.md`

---

### `get_developer.py`

获取当前开发者名。

```bash
python3 .trellis/scripts/get_developer.py
# Output: taosu
```

**退出码：**
- `0` - 成功
- `1` - 未初始化

---

## 上下文脚本（Context Scripts）

### `get_context.py`

获取供 AI 消费的会话运行时。

```bash
python3 .trellis/scripts/get_context.py
```

**输出包括：**
- 开发者身份
- Git 状态与最近提交
- 当前任务（如有）
- Workspace 摘要

---

### `add_session.py`

将会话条目记入 journal。

```bash
python3 .trellis/scripts/add_session.py "Session summary"
```

**动作：**
1. 追加到当前 journal
2. 更新 index markers
3. 需要时轮转 journal

---

## 任务脚本（Task Scripts）

### `task.py`

任务管理 CLI。

#### 创建任务

```bash
python3 .trellis/scripts/task.py create "Task name" --slug task-slug
```

**选项：**
- `--slug` - URL-safe 标识符
- `--assignee` - 开发者名（默认：当前）
- `--type` - Dev type: frontend, backend, fullstack

#### 列出任务

```bash
python3 .trellis/scripts/task.py list
```

**输出：**
```
Active Tasks:
  01-31-add-login-taosu (active)
  01-30-fix-api-cursor-agent (paused)
```

#### 开始任务

```bash
python3 .trellis/scripts/task.py start <task-dir>
```

在 `.trellis/.runtime/sessions/<session-key>.json` 中设置活跃任务。
若无 session 身份或 `TRELLIS_CONTEXT_ID`，该命令失败，且不会创建 `.trellis/.current-task`。

#### 结束任务

```bash
python3 .trellis/scripts/task.py finish
```

仅清除当前 session 运行时中的活跃任务。

#### 初始化上下文

```bash
python3 .trellis/scripts/task.py init-context <task-dir> <dev-type>
```

**Dev types：** `frontend`、`backend`、`fullstack`

创建带有适当 spec 引用的 JSONL 文件。

#### 设置分支

```bash
python3 .trellis/scripts/task.py set-branch <task-dir> <branch-name>
```

更新 task.json 中的 `branch` 字段。

#### 归档任务

```bash
python3 .trellis/scripts/task.py archive <task-dir>
```

将任务移到 `.trellis/tasks/archive/YYYY-MM/`。

#### 列出归档

```bash
python3 .trellis/scripts/task.py list-archive [month]
```

---

## 公共工具（Common Utilities）

### `common/paths.py`

路径常量与工具。

```python
from common.paths import (
    TRELLIS_DIR,      # .trellis/
    WORKSPACE_DIR,    # .trellis/workspace/
    TASKS_DIR,        # .trellis/tasks/
    SPEC_DIR,         # .trellis/spec/
)
```

### `common/developer.py`

开发者管理。

```python
from common.developer import (
    get_developer,     # Get current developer name
    get_workspace_dir, # Get developer's workspace directory
)
```

### `common/task_utils.py`

任务查找函数。

```python
from common.task_utils import (
    get_current_task,  # Get active task directory
    load_task_json,    # Load task.json
    save_task_json,    # Save task.json
)
```

### `common/phase.py`

阶段跟踪。

```python
from common.phase import (
    get_current_phase,  # Get current phase number
    advance_phase,      # Move to next phase
)
```

### `common/git_context.py`

Git 上下文生成。

```python
from common.git_context import (
    get_git_status,     # Get git status
    get_recent_commits, # Get recent commit messages
    get_branch_name,    # Get current branch
)
```

---

## 用法示例（Usage Examples）

### 初始化新开发者

```bash
cd /path/to/project
python3 .trellis/scripts/init_developer.py john-doe
```

### 创建并开始任务

```bash
# Create task
python3 .trellis/scripts/task.py create "Add user login" --slug add-login

# Initialize context for fullstack work
python3 .trellis/scripts/task.py init-context \
  .trellis/tasks/01-31-add-login-john-doe fullstack

# Start task
python3 .trellis/scripts/task.py start \
  .trellis/tasks/01-31-add-login-john-doe
```

### 记录会话

```bash
python3 .trellis/scripts/add_session.py "Implemented login form, pending API integration"
```

### 归档已完成任务

```bash
python3 .trellis/scripts/task.py archive \
  .trellis/tasks/01-31-add-login-john-doe
```
