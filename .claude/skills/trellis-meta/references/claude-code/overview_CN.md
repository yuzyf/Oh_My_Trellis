<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/claude-code/overview.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# Claude Code 功能总览（Claude Code Features Overview）

这些功能需要 **Claude Code**，在 Cursor 或其它平台上不可用。

---

## 为什么仅 Claude Code？（Why Claude Code Only?）

Claude Code 提供这些独特能力：

| Feature | Claude Code | Why Required |
|---------|-------------|--------------|
| Hooks | ✅ | 生命周期事件的 hook 系统 |
| Task tool | ✅ | 带上下文的 subagent 调用 |
| `--agent` flag | ✅ | 加载 agent 定义 |
| `--resume` | ✅ | 会话持久化 |
| CLI scripting | ✅ | 用 `claude` 命令做自动化 |

---

## 功能分类（Feature Categories）

### Hooks 系统（Hooks System）
自动上下文注入与质量强制。

| Hook | When | Purpose |
|------|------|---------|
| `SessionStart` | 会话开始 | 注入工作流上下文 |
| `PreToolUse:Task` | subagent 之前 | 通过 JSONL 注入 specs |
| `SubagentStop:check` | Check agent 停止时 | Ralph Loop 强制 |

→ 见 [hooks.md](./hooks.md)

### Agent 系统（Agent System）
面向不同开发阶段的专用 agents。

| Agent | Purpose |
|-------|---------|
| `dispatch` | 编排流水线 |
| `implement` | 写代码 |
| `check` | 评审并自修复 |
| `debug` | 修问题 |
| `research` | 找模式 |
| `plan` | 评估需求 |

→ 见 [agents.md](./agents.md)

### Ralph Loop
面向 Check Agent 的质量强制。

- Check Agent 停止时运行验证命令
- 全部通过前阻塞完成
- 最多 5 次迭代，30 分钟超时

→ 见 [ralph-loop.md](./ralph-loop.md)

### Multi-Session
用 Git worktrees 做并行隔离会话。

- 每个会话在独立 worktree
- 自己的分支、自己的 Claude 进程
- 自动创建 PR

→ 见 [multi-session.md](./multi-session.md)

### worktree.yaml
Multi-Session 与 Ralph Loop 的配置。

→ 见 [worktree-config.md](./worktree-config.md)

---

## 本目录文档（Documents in This Directory）

| Document | Content |
|----------|---------|
| `hooks.md` | Hook 系统、上下文注入 |
| `agents.md` | Agent 类型、调用、上下文 |
| `ralph-loop.md` | 质量强制机制 |
| `multi-session.md` | 并行 worktree 会话 |
| `worktree-config.md` | worktree.yaml 配置 |
| `scripts.md` | 仅 Claude Code 的脚本 |

---

## 架构（Architecture）

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      CLAUDE CODE INTEGRATION                             │
│                                                                          │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐        │
│  │  SessionStart  │    │  PreToolUse    │    │  SubagentStop  │        │
│  │     Hook       │    │     Hook       │    │     Hook       │        │
│  └───────┬────────┘    └───────┬────────┘    └───────┬────────┘        │
│          │                     │                     │                  │
│          ▼                     ▼                     ▼                  │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐        │
│  │ session-start  │    │ inject-context │    │  ralph-loop    │        │
│  │     .py        │    │     .py        │    │     .py        │        │
│  └───────┬────────┘    └───────┬────────┘    └───────┬────────┘        │
│          │                     │                     │                  │
│          ▼                     ▼                     ▼                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     CORE SYSTEMS (File-Based)                    │   │
│  │  Workspace  │  Tasks  │  Specs  │  Commands  │  Scripts          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 检查 Claude Code 是否可用（Checking Claude Code Availability）

```bash
# Check if Claude Code is installed
claude --version

# Verify hooks are configured
cat .claude/settings.json | grep -A 5 '"hooks"'
```

若 hooks 不存在，Claude Code 功能不会生效。
