<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/how-to-modify/modify-hook.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# How To: 修改 Hook

改 hook 行为以调整上下文注入或校验。

**Platform**：仅 Claude Code

---

## 要修改的文件（Files to Modify）

| File | Action | Required |
|------|--------|----------|
| `.claude/hooks/{hook}.py` | Modify | Yes |
| `.claude/settings.json` | Modify | If changing matcher/timeout |
| `trellis-local/SKILL.md` | Update | Yes |

---

## Hook 类型（Hook Types）

| Hook | File | Purpose |
|------|------|---------|
| SessionStart | `session-start.py` | 注入初始上下文 |
| PreToolUse:Task | `inject-subagent-context.py` | 注入 agent 上下文 |
| SubagentStop:check | `ralph-loop.py` | 质量强制 |

---

## Step 1: 理解 Hook 结构

### 输入（stdin）

Hooks 接收 JSON 输入：

```json
{
  "hook_event": "PreToolUse",
  "tool_name": "Task",
  "tool_input": {
    "subagent_type": "implement",
    "prompt": "..."
  }
}
```

### 输出（stdout）

Hooks 输出 JSON：

```json
{
  "result": "continue",
  "message": "Optional message to inject",
  "updatedInput": {
    "prompt": "Modified prompt..."
  }
}
```

### Result 类型

| Result | Effect |
|--------|--------|
| `continue` | 允许操作，可选修改 |
| `block` | 阻止操作 |

---

## Step 2: 修改 Hook 逻辑

### 示例：给 Session Start 加上下文

编辑 `.claude/hooks/session-start.py`：

```python
def get_additional_context():
    """Add custom context."""
    context = []

    # Add custom file
    custom_path = os.path.join(repo_root, ".trellis/custom.md")
    if os.path.exists(custom_path):
        with open(custom_path) as f:
            context.append(f"## Custom Context\n{f.read()}")

    return "\n".join(context)

# In main():
additional = get_additional_context()
message = f"{existing_message}\n\n{additional}"
```

### 示例：添加 Agent 校验

编辑 `.claude/hooks/inject-subagent-context.py`：

```python
def validate_agent_input(subagent_type, prompt):
    """Validate agent invocation."""
    if subagent_type == "implement":
        if "git commit" in prompt.lower():
            return False, "Implement agent cannot commit"
    return True, None

# In main():
valid, error = validate_agent_input(subagent_type, prompt)
if not valid:
    output = {"result": "block", "message": error}
    print(json.dumps(output))
    return
```

### 示例：添加 Verify 命令

编辑 `.claude/hooks/ralph-loop.py`：

```python
# Add to verify commands list
ADDITIONAL_COMMANDS = ["pnpm test:unit"]

def get_verify_commands():
    commands = read_worktree_yaml_verify()
    commands.extend(ADDITIONAL_COMMANDS)
    return commands
```

---

## Step 3: 修改 Settings（如需）

编辑 `.claude/settings.json`：

### 改超时

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Task",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ...",
            "timeout": 60  // Increase from 30
          }
        ]
      }
    ]
  }
}
```

### 改 Matcher

```json
{
  "hooks": {
    "SubagentStop": [
      {
        "matcher": "check|my-agent",  // Add new agent
        "hooks": [...]
      }
    ]
  }
}
```

---

## Step 4: 在 trellis-local 中记录

更新 `.claude/skills/trellis-local/SKILL.md`：

```markdown
## Hooks Changed

#### session-start.py
- **Hook Event**: SessionStart
- **Change**: Added custom context injection
- **Lines modified**: 45-60
- **Date**: 2026-01-31
- **Reason**: Need to inject project-specific context

#### inject-subagent-context.py
- **Hook Event**: PreToolUse:Task
- **Change**: Added validation for implement agent
- **Lines modified**: 120-135
- **Date**: 2026-01-31
- **Reason**: Prevent accidental git commits
```

---

## 测试（Testing）

### 手动测试

```bash
# Test session-start
python3 .claude/hooks/session-start.py

# Test inject-subagent-context
echo '{"tool_input":{"subagent_type":"implement","prompt":"test"}}' | \
  python3 .claude/hooks/inject-subagent-context.py

# Test ralph-loop
echo '{"subagent_type":"check","output":"test"}' | \
  python3 .claude/hooks/ralph-loop.py
```

### 集成测试

1. 开启新的 Claude Code 会话
2. 验证 session-start 输出
3. 调用 subagent
4. 验证上下文注入
5. 验证 Ralph Loop（针对 check agent）

---

## 常见修改（Common Modifications）

### 向 Session Context 添加文件

```python
# session-start.py
files_to_inject = [
    ".trellis/workflow.md",
    ".trellis/custom-context.md",  # Add this
]
```

### 跳过某些 Agent 的注入

```python
# inject-subagent-context.py
SKIP_INJECTION = ["research"]

if subagent_type in SKIP_INJECTION:
    print(json.dumps({"result": "continue"}))
    return
```

### 添加自定义校验

```python
# ralph-loop.py
def custom_check():
    """Custom verification logic."""
    # Check something
    return True, None

# In verify():
ok, error = custom_check()
if not ok:
    return False, error
```

---

## 检查清单（Checklist）

- [ ] Hook 逻辑已修改
- [ ] 需要时已更新 settings
- [ ] 手动测试通过
- [ ] 集成测试通过
- [ ] 已在 trellis-local 记录
