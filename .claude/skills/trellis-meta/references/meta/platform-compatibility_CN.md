<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/meta/platform-compatibility.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 平台兼容性参考（Platform Compatibility Reference）

跨不同 AI 编程平台说明 Trellis 功能可用性的详细指南。

---

## 概述（Overview）

Trellis 主要面向 **Claude Code** 设计，并对 **Cursor** 提供部分支持。对 **OpenCode** 的未来支持仍在考虑中。

关键差异在于 **hooks 支持**——Claude Code 的 hook 系统能自动注入上下文并强制质量门禁，其它平台则需要手工变通。

---

## 平台架构（Platform Architecture）

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TRELLIS FEATURE LAYERS                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    LAYER 3: AUTOMATION                              │ │
│  │  Hooks, Ralph Loop, Auto-injection, Multi-Session                  │ │
│  │  ─────────────────────────────────────────────────────────────────│ │
│  │  Platform: Claude Code ONLY                                        │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                    │                                     │
│  ┌────────────────────────────────▼───────────────────────────────────┐ │
│  │                    LAYER 2: AGENTS                                  │ │
│  │  Agent definitions, Task tool, Subagent invocation                 │ │
│  │  ─────────────────────────────────────────────────────────────────│ │
│  │  Platform: Claude Code (full), Cursor (manual)                     │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                    │                                     │
│  ┌────────────────────────────────▼───────────────────────────────────┐ │
│  │                    LAYER 1: PERSISTENCE                             │ │
│  │  Workspace, Tasks, Specs, Commands, JSONL files                    │ │
│  │  ─────────────────────────────────────────────────────────────────│ │
│  │  Platform: ALL (file-based, portable)                              │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 功能分层明细（Detailed Feature Breakdown）

### Layer 1: 持久化（所有平台）（Persistence）

这些功能在所有平台都能工作，因为它们基于文件。

| Feature | Location | Description |
|---------|----------|-------------|
| Workspace system | `.trellis/workspace/` | Journals、会话历史 |
| Task system | `.trellis/tasks/` | 任务跟踪与需求 |
| Spec system | `.trellis/spec/` | 编码指南 |
| Slash commands | `.claude/commands/` | 命令提示（在 Cursor 上手动阅读） |
| JSONL context | 任务目录中的 `*.jsonl` | 上下文文件列表 |
| Developer identity | `.trellis/.developer` | 谁在工作 |
| Current task | `.trellis/.runtime/sessions/` | 会话状态 |

**Cursor 变通**：会话开始时手动阅读这些文件。

### Layer 2: Agents（Claude Code 完整，Cursor 有限）

| Feature | Claude Code | Cursor |
|---------|-------------|--------|
| Agent definitions | 通过 `--agent` 标志自动加载 | 手动阅读 `.claude/agents/*.md` |
| Task tool | 完整 subagent 支持 | 无 Task tool |
| Context injection | 通过 hooks 自动 | 手动复制粘贴 |
| Agent restrictions | 由定义强制 | 仅靠约定遵守 |

**Cursor 变通**：
1. 手动阅读 agent 定义文件
2. 从 JSONL 文件复制相关上下文
3. 手动遵守 agent 限制

### Layer 3: 自动化（仅 Claude Code）（Automation）

| Feature | Dependency | Why Claude Code Only |
|---------|------------|---------------------|
| SessionStart hook | `.claude/settings.json` | Claude Code hook 系统 |
| PreToolUse hook | Hook system | 拦截工具调用 |
| SubagentStop hook | Hook system | 控制 agent 生命周期 |
| Auto context injection | PreToolUse:Task | Hooks 注入 JSONL 内容 |
| Ralph Loop | SubagentStop:check | 在验证通过前阻塞 agent |
| Multi-Session | claude CLI + hooks | `claude --resume`、worktree 脚本 |

**无变通**：这些功能从根本上需要 Claude Code 的 hook 系统。

---

## 使用的 Claude Code 功能（Claude Code Features Used）

### Hook 系统（Hook System）

```json
// .claude/settings.json
{
  "hooks": {
    "SessionStart": [...],
    "PreToolUse": [...],
    "SubagentStop": [...]
  }
}
```

Claude Code 在特定生命周期点执行这些 hooks。目前没有其它平台支持这一点。

### CLI 功能（CLI Features）

| Command | Purpose |
|---------|---------|
| `claude --agent <name>` | 加载 agent 定义 |
| `claude --resume <id>` | 恢复会话 |
| `claude -p` | 打印模式（非交互） |
| `claude --dangerously-skip-permissions` | 自动化模式 |
| `claude --output-format stream-json` | 机器可读输出 |

### Task 工具（Task Tool）

```javascript
Task(
  subagent_type: "implement",
  prompt: "...",
  model: "opus"
)
```

Claude Code 的 Task 工具会生成带隔离上下文的 subagents。PreToolUse hook 拦截该调用以注入 specs。

---

## Cursor 使用指南（Cursor Usage Guide）

对使用 Cursor 的团队，可这样获得部分 Trellis 收益：

### 可用部分（What Works）

1. **Workspace 跟踪**：journals 与 sessions 正常工作
2. **任务组织**：任务目录与 PRD 可用
3. **Spec 阅读**：会话开始时手动阅读 specs
4. **把 Commands 当提示**：把命令文件当参考阅读

### 推荐工作流（Recommended Workflow）

```
1. Session Start
   - Read .trellis/workflow.md
   - Read relevant specs from .trellis/spec/
   - Run `task.py current --source`

2. Before Implementation
   - Read implement.jsonl for session files
   - Manually read each file listed
   - Follow spec guidelines

3. Before Commit
   - Run verify commands manually (pnpm lint, pnpm typecheck)
   - Self-review against check.jsonl specs
```

### 不可用部分（What Doesn't Work）

- 无自动 spec 注入
- 无 Ralph Loop（仅手动验证）
- 无 Multi-Session（无 worktree 自动化）
- 无会话恢复

---

## OpenCode 考量（未来）（OpenCode Considerations）

### 支持所需条件（Requirements for Support）

要支持 OpenCode，需要：

1. **Hook 等价物**：某种拦截 agent 生命周期事件的方式
2. **Agent 系统**：带上下文的 subagent 调用
3. **CLI 集成**：脚本与自动化支持

### 可能路径（Potential Approaches）

| Approach | Pros | Cons |
|----------|------|------|
| Native integration | 体验最好、功能完整 | 需要 OpenCode 改动 |
| Adapter layer | 适配当前 OpenCode | 维护负担 |
| File-based polling | 无需改 OpenCode | 取巧、有延迟 |
| MCP server | 标准协议 | 可能覆盖不了全部 hooks |

### 最小可行支持（Minimum Viable Support）

若 OpenCode 增加类似 Claude Code 的 hook 支持：

1. 把 `session-start.py` 移植到 OpenCode 格式
2. 移植 `inject-subagent-context.py` 做上下文注入
3. 移植 `ralph-loop.py` 做质量强制

没有 hooks 时，只有 Layer 1（持久化）功能可用。

---

## 版本兼容矩阵（Version Compatibility Matrix）

| Trellis Version | Claude Code | Cursor | OpenCode |
|-----------------|-------------|--------|----------|
| 0.3.x | Full support | Partial | Not supported |
| 0.4.x (planned) | Full support | Partial | TBD |

### 破坏性变更（Breaking Changes）

| Version | Change | Impact |
|---------|--------|--------|
| 0.3.0 | New hook format | Update settings.json |
| 0.3.0-beta.3 | worktree.yaml schema | Update config |

---

## 检查你的平台（Checking Your Platform）

### Claude Code

```bash
# Check Claude Code version
claude --version

# Verify hooks are loaded
cat .claude/settings.json | grep -A 5 '"hooks"'
```

### Cursor

```bash
# No CLI check available
# Verify by checking if hooks execute (they won't)
```

### 判定支持级别（Determining Support Level）

```
Is hooks system available?
├── YES → Full Trellis support (Claude Code)
└── NO  → Partial support only
         ├── Can read files → Layer 1 works
         └── Has agent system → Layer 2 partial
```
