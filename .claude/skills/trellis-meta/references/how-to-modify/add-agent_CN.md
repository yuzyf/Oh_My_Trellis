<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/how-to-modify/add-agent.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# How To: 添加 Agent

添加如 `my-agent` 这样的新 agent 类型。

**Platform**：仅 Claude Code

---

## 要修改的文件（Files to Modify）

| File | Action | Required |
|------|--------|----------|
| `.claude/agents/my-agent.md` | Create | Yes |
| `.claude/hooks/inject-subagent-context.py` | Modify | Yes |
| `.trellis/tasks/{template}/my-agent.jsonl` | Create | Yes |
| `trellis-local/SKILL.md` | Update | Yes |
| `.claude/agents/dispatch.md` | Modify | If adding to pipeline |

---

## Step 1: 创建 Agent 定义

创建 `.claude/agents/my-agent.md`：

```markdown
---
name: my-agent
description: |
  What this agent specializes in.
  When it should be used.
tools: Read, Write, Edit, Bash, Glob, Grep
model: opus
---

# My Agent

## Core Responsibilities

1. Primary responsibility
2. Secondary responsibility
3. ...

## Workflow

1. First step
2. Second step
3. ...

## Forbidden Operations

- Thing 1 (why it's forbidden)
- Thing 2 (why it's forbidden)
- git commit (unless explicitly allowed)

## Output Format

What the agent should produce.
```

### Agent 定义字段

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Agent 标识符 |
| `description` | Yes | Agent 做什么 |
| `tools` | Yes | 允许的工具 |
| `model` | No | 使用的模型（opus、sonnet） |

---

## Step 2: 更新 Hook

编辑 `.claude/hooks/inject-subagent-context.py`：

### 添加常量

```python
# Near other agent constants
AGENT_MY_AGENT = "my-agent"

# Add to list
AGENTS_ALL = (..., AGENT_MY_AGENT)
```

### 添加上下文函数

```python
def get_my_agent_context(repo_root: str, task_dir: str) -> list:
    """Get context for my-agent."""
    context_files = []

    # Load from JSONL
    jsonl_path = os.path.join(task_dir, "my-agent.jsonl")
    if os.path.exists(jsonl_path):
        context_files.extend(load_jsonl_context(jsonl_path))

    # Add any additional files
    # context_files.append({"file": "...", "reason": "..."})

    return context_files
```

### 加入主 switch

```python
elif subagent_type == AGENT_MY_AGENT:
    context = get_my_agent_context(repo_root, task_dir)
    new_prompt = build_agent_prompt(
        agent_name="My Agent",
        original_prompt=original_prompt,
        context=context
    )
```

---

## Step 3: 创建 JSONL 模板

为任务目录创建上下文模板。

**选项 A**：加入 `task.py init-context`：

```python
def init_my_agent_context(task_dir, dev_type):
    jsonl_path = os.path.join(task_dir, "my-agent.jsonl")
    with open(jsonl_path, "w") as f:
        # Add relevant specs
        f.write(json.dumps({
            "file": ".trellis/spec/guides/index.md",
            "reason": "Thinking guides"
        }) + "\n")
```

**选项 B**：手动创建模板：

```jsonl
{"file": ".trellis/spec/guides/index.md", "reason": "Thinking guides"}
{"file": ".trellis/tasks/{task}/prd.md", "reason": "Requirements"}
```

---

## Step 4: 加入流水线（可选）

若 agent 应成为标准 workflow 的一部分：

### 更新 task.json 模板

```json
"next_action": [
  {"phase": 1, "action": "implement"},
  {"phase": 2, "action": "my-agent"},  // Add here
  {"phase": 3, "action": "check"},
  {"phase": 4, "action": "finish"}
]
```

### 更新 dispatch.md

为新阶段添加处理：

```markdown
## Phase Handling

...

### my-agent Phase
- Call `Task(subagent_type="my-agent")`
- Wait for completion
- Proceed to next phase
```

---

## Step 5: 在 trellis-local 中记录

更新 `.claude/skills/trellis-local/SKILL.md`：

```markdown
## Agents

### Added Agents

#### my-agent
- **File**: `.claude/agents/my-agent.md`
- **Platform**: [CC]
- **Purpose**: What it does
- **Tools**: Read, Write, Edit, Bash, Glob, Grep
- **Added**: 2026-01-31
- **Reason**: Why it was added

### Hooks Changed

#### inject-subagent-context.py
- **Change**: Added support for `my-agent` type
- **Lines modified**: XX-YY
- **Date**: 2026-01-31
```

---

## 测试（Testing）

1. 创建带 my-agent.jsonl 的任务
2. 设为当前任务：`task.py start <task-dir>`
3. 调用 agent：`Task(subagent_type="my-agent", prompt="Test")`
4. 验证上下文注入生效
5. 验证 agent 行为符合定义

---

## 检查清单（Checklist）

- [ ] Agent 定义已创建并有正确 frontmatter
- [ ] Hook 已加入 agent 常量
- [ ] Hook 已加入上下文函数
- [ ] Hook 已加入主 switch 分支
- [ ] JSONL 模板已创建
- [ ] 需要时已加入流水线
- [ ] 已在 trellis-local 记录
- [ ] 已测试 agent
