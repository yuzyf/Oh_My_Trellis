<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/how-to-modify/add-phase.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# How To: 添加 Workflow 阶段

在任务 workflow 流水线中增加新阶段。

**Platform**：仅 Claude Code

---

## 要修改的文件（Files to Modify）

| File | Action | Required |
|------|--------|----------|
| Task `task.json` | Modify | Yes |
| `.claude/agents/dispatch.md` | Modify | Yes |
| `.claude/agents/{new-agent}.md` | Create | If new agent |
| `inject-subagent-context.py` | Modify | If new agent |
| `trellis-local/SKILL.md` | Update | Yes |

---

## 标准阶段（Standard Phases）

默认 workflow：

```
implement → check → finish → create-pr
```

---

## Step 1: 更新 task.json

修改 task.json 中的 `next_action` 数组：

### 在 Implement 之后加阶段

```json
{
  "next_action": [
    {"phase": 1, "action": "implement"},
    {"phase": 2, "action": "review"},      // New phase
    {"phase": 3, "action": "check"},
    {"phase": 4, "action": "finish"},
    {"phase": 5, "action": "create-pr"}
  ]
}
```

### 在 Implement 之前加阶段

```json
{
  "next_action": [
    {"phase": 1, "action": "design"},      // New phase
    {"phase": 2, "action": "implement"},
    {"phase": 3, "action": "check"},
    {"phase": 4, "action": "finish"}
  ]
}
```

---

## Step 2: 更新 Dispatch Agent

编辑 `.claude/agents/dispatch.md`：

### 添加阶段处理

```markdown
## Phase Handling

### implement Phase
...existing...

### review Phase (NEW)
- Purpose: Review implementation before check
- Call: `Task(subagent_type="review")`
- Next: Proceed to check phase

### check Phase
...existing...
```

### 更新 Workflow 描述

```markdown
## Workflow

1. Read task.json for next_action
2. Execute phases in order:
   - implement: Write code
   - review: Review implementation (NEW)
   - check: Quality verification
   - finish: Final review
   - create-pr: Create pull request
```

---

## Step 3: 创建 Agent（若新建）

若该阶段使用新 agent，创建 agent 定义。

→ 详见 `add-agent.md`。

快速版：

```markdown
---
name: review
description: Review implementation before check phase.
tools: Read, Glob, Grep
---

# Review Agent

## Core Responsibilities
1. Review code changes
2. Check against requirements
3. Identify issues before check phase

## Forbidden Operations
- Writing code (that's implement's job)
- Git operations
```

---

## Step 4: 更新 Hook（若新 agent）

若使用新 agent，更新 `inject-subagent-context.py`：

```python
AGENT_REVIEW = "review"
AGENTS_ALL = (..., AGENT_REVIEW)

def get_review_context(repo_root, task_dir):
    # Load review.jsonl
    ...

elif subagent_type == AGENT_REVIEW:
    context = get_review_context(repo_root, task_dir)
    ...
```

---

## Step 5: 更新任务模板

更新 `task.py` 中默认 task.json 创建：

```python
default_next_action = [
    {"phase": 1, "action": "implement"},
    {"phase": 2, "action": "review"},     # Add new phase
    {"phase": 3, "action": "check"},
    {"phase": 4, "action": "finish"},
]
```

---

## Step 6: 在 trellis-local 中记录

```markdown
## Workflow Changes

### Added review Phase
- **Position**: After implement, before check
- **Agent**: review
- **Purpose**: Review implementation quality
- **Date**: 2026-01-31
- **Reason**: Catch issues before check phase
```

---

## 常见阶段模式（Common Phase Patterns）

### Design → Implement → Check

```json
"next_action": [
  {"phase": 1, "action": "design"},
  {"phase": 2, "action": "implement"},
  {"phase": 3, "action": "check"}
]
```

### Implement → Test → Check

```json
"next_action": [
  {"phase": 1, "action": "implement"},
  {"phase": 2, "action": "test"},
  {"phase": 3, "action": "check"}
]
```

### Research → Implement → Check

```json
"next_action": [
  {"phase": 1, "action": "research"},
  {"phase": 2, "action": "implement"},
  {"phase": 3, "action": "check"}
]
```

---

## 测试（Testing）

1. 创建 next_action 含新阶段的任务
2. 设为当前任务
3. 运行 dispatch agent
4. 验证阶段按序执行
5. 验证新阶段工作正确

---

## 检查清单（Checklist）

- [ ] task.json 已更新新阶段
- [ ] dispatch.md 已更新阶段处理
- [ ] 需要时已创建 agent
- [ ] 需要时已更新 hook
- [ ] 任务模板已更新
- [ ] 已在 trellis-local 记录
- [ ] 已测试 workflow
