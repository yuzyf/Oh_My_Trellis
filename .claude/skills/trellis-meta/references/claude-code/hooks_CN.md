<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/claude-code/hooks.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# Hooks 参考（Hooks Reference）

Claude Code hook 系统：生命周期事件上的自动上下文注入与质量强制。

---

## 概述（Overview）

Hooks 在特定生命周期点运行脚本，无需用户操作即可注入上下文或强制质量门禁。

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           HOOK LIFECYCLE                                 │
│                                                                          │
│  Session starts ──► SessionStart hook ──► Inject workflow context       │
│                                                                          │
│  Task() called ──► PreToolUse:Task hook ──► Inject specs from JSONL     │
│                                                                          │
│  Agent stops ──► SubagentStop hook ──► Ralph Loop verification          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 配置（Configuration）

### `.claude/settings.json`

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.py\"",
            "timeout": 10
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Task",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/inject-subagent-context.py\"",
            "timeout": 30
          }
        ]
      }
    ],
    "SubagentStop": [
      {
        "matcher": "check",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/ralph-loop.py\"",
            "timeout": 300
          }
        ]
      }
    ]
  }
}
```

---

## SessionStart Hook

### 目的（Purpose）

Claude Code 会话开始时注入初始上下文。

### 脚本：`session-start.py`

**注入内容：**
- 来自 `.trellis/.developer` 的开发者身份
- Git 状态与最近提交
- 当前任务（若会话作用域解析器找到）
- `workflow.md` 内容
- 全部 `spec/*/index.md` 文件
- 启动说明

**输出格式：**
```json
{
  "result": "continue",
  "message": "# Session Context\n\n## Developer\ntaosu\n\n## Git Status\n..."
}
```

---

## PreToolUse:Task Hook

### 目的（Purpose）

调用 subagent 时注入相关 specs。

### 脚本：`inject-subagent-context.py`

**触发：** 调用 `Task(subagent_type="...")` 时。

**流程：**
1. 从工具输入读取 `subagent_type`
2. 通过会话作用域解析器查找活动任务
3. 从任务目录加载 `{subagent_type}.jsonl`
4. 阅读 JSONL 列出的每个文件
5. 用上下文构建增强 prompt
6. 用当前阶段更新 `task.json`

**输出格式：**
```json
{
  "result": "continue",
  "updatedInput": {
    "prompt": "# Implement Agent Task\n\n## Context\n...\n\n## Your Task\n..."
  }
}
```

### JSONL 格式（JSONL Format）

```jsonl
{"file": ".trellis/spec/cli/backend/index.md", "reason": "Backend guidelines"}
{"file": "src/services/auth.ts", "reason": "Existing pattern"}
{"file": ".trellis/tasks/01-31-add-login/prd.md", "reason": "Requirements"}
```

---

## SubagentStop Hook

### 目的（Purpose）

通过 Ralph Loop 做质量强制。

### 脚本：`ralph-loop.py`

**触发：** Check Agent 尝试停止时。

**流程：**
1. 从 `worktree.yaml` 读取验证命令
2. 执行每条命令（pnpm lint、pnpm typecheck 等）
3. 全部通过 → 允许停止
4. 任一失败 → 阻塞停止，agent 继续

→ 细节见 [ralph-loop.md](./ralph-loop.md)。

---

## Hook 脚本位置（Hook Scripts Location）

```
.claude/hooks/
├── session-start.py           # SessionStart handler
├── inject-subagent-context.py # PreToolUse:Task handler
└── ralph-loop.py              # SubagentStop:check handler
```

---

## 环境变量（Environment Variables）

Hook 脚本中可用：

| Variable | Description |
|----------|-------------|
| `CLAUDE_PROJECT_DIR` | 项目根目录 |
| `HOOK_EVENT` | 事件类型（SessionStart、PreToolUse 等） |
| `TOOL_NAME` | 被调用的工具（PreToolUse） |
| `TOOL_INPUT` | 工具输入的 JSON 字符串 |
| `SUBAGENT_TYPE` | Agent 类型（SubagentStop） |

---

## Hook 响应格式（Hook Response Format）

### Continue（允许操作）

```json
{
  "result": "continue",
  "message": "Optional message to inject"
}
```

### Continue with modified input（带修改后的输入继续）

```json
{
  "result": "continue",
  "updatedInput": {
    "prompt": "Modified prompt..."
  }
}
```

### Block（阻止操作）

```json
{
  "result": "block",
  "message": "Reason for blocking"
}
```

---

## 调试 Hooks（Debugging Hooks）

### 查看 hook 输出

```bash
# Check if hooks are configured
cat .claude/settings.json | grep -A 20 '"hooks"'

# Test session-start manually
python3 .claude/hooks/session-start.py

# Test inject-context (needs TOOL_INPUT env var)
TOOL_INPUT='{"subagent_type":"implement","prompt":"test"}' \
  python3 .claude/hooks/inject-subagent-context.py
```

### 常见问题（Common Issues）

| Issue | Cause | Solution |
|-------|-------|----------|
| Hook not running | Wrong matcher | Check settings.json matcher |
| Timeout | Script too slow | Increase timeout or optimize |
| No context injected | Missing session active task | Run `task.py start` with session identity |
| JSONL not found | Wrong task directory | Check `task.py current --source` |
