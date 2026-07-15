<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/how-to-modify/overview.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 如何修改 Trellis（How To Modify Trellis）

本目录收录常见本地修改场景的操作指南。在改任何东西之前，先确认你在改**用户项目中的本地 Trellis**，而不是上游 CLI 源码。

---

## 快速场景索引（Quick Scenario Index）

| Scenario | Primary files | Platform |
|----------|---------------|----------|
| [Add slash command](#add-slash-command) | commands/, trellis-local | All |
| [Add agent](#add-agent) | agents/, inject-subagent-context.py | CC |
| [Modify hook](#modify-hook) | hooks/, settings.json | CC |
| [Add spec category](#add-spec-category) | spec/, jsonl templates | All |
| [Change verify commands](#change-verify-commands) | worktree.yaml | CC |
| [Add workflow phase](#add-workflow-phase) | task.json, dispatch.md, agents | CC |
| [Add post_create step](#add-post_create-step) | worktree.yaml | CC |
| [Modify session start](#modify-session-start) | session-start.py, trellis-local | CC |
| [Add core script](#add-core-script) | scripts/, trellis-local | All |
| [Change task types](#change-task-types) | task.py, jsonl templates | All |

**Platform**：`All` = 所有平台 | `CC` = 仅 Claude Code

---

## 详细指南（Detailed Guides）

### 添加 Slash Command

**场景**：增加新的 `/trellis:my-command` 命令。

**要修改的文件**：

```
.claude/commands/trellis/my-command.md    # Create: Command prompt
.cursor/commands/my-command.md            # Create: Mirror for Cursor (optional)
.trellis-local/SKILL.md                   # Update: Document the change
```

**步骤**：
1. 创建带 YAML frontmatter 的命令文件
2. 需要时镜像到 Cursor
3. 在 trellis-local 中记录

→ 详见 `add-command.md`。

---

### 添加 Agent

**场景**：增加如 `my-agent` 这样的新 agent 类型。

**要修改的文件**：

```
.claude/agents/my-agent.md                          # Create: Agent definition
.claude/hooks/inject-subagent-context.py            # Modify: Add agent handling
.trellis/tasks/{template}/my-agent.jsonl            # Create: Context template
.trellis-local/SKILL.md                             # Update: Document the change
```

**可选**：
```
.claude/agents/dispatch.md                          # Modify: If adding to pipeline
task.json template                                  # Modify: Add to next_action
```

→ 详见 `add-agent.md`。

---

### 修改 Hook

**场景**：改 hook 行为（上下文注入、校验等）。

**要修改的文件**：

```
.claude/hooks/{hook-name}.py              # Modify: Hook logic
.claude/settings.json                     # Modify: If changing matcher/timeout
.trellis-local/SKILL.md                   # Update: Document the change
```

→ 详见 `modify-hook.md`。

---

### 添加 Spec 分类

**场景**：增加如 `mobile/` 这样的新 spec 分类。

**要修改的文件**：

```
.trellis/spec/mobile/index.md             # Create: Category index
.trellis/spec/mobile/*.md                 # Create: Spec files
.trellis/tasks/{template}/*.jsonl         # Update: Reference new specs
.trellis-local/SKILL.md                   # Update: Document the change
```

→ 详见 `add-spec.md`。

---

### 修改 Verify 命令

**场景**：增加或修改 Ralph Loop 校验命令。

**要修改的文件**：

```
.trellis/worktree.yaml                    # Modify: verify section
```

**示例**：
```yaml
verify:
  - pnpm lint
  - pnpm typecheck
  - pnpm test        # Add this
```

→ 详见 `change-verify.md`。

---

### 添加 Workflow 阶段

**场景**：在任务 workflow 中增加新阶段。

**要修改的文件**：

```
task.json (in task directories)           # Modify: next_action array
.claude/agents/dispatch.md                # Modify: Handle new phase
.claude/agents/{new-phase}.md             # Create: If new agent needed
.claude/hooks/inject-subagent-context.py  # Modify: If new agent
.trellis-local/SKILL.md                   # Update: Document the change
```

→ 详见 `add-phase.md`。

---

### 添加 post_create 步骤

**场景**：在 worktree 创建后增加 setup 步骤。

**要修改的文件**：

```
.trellis/worktree.yaml                    # Modify: post_create section
```

**示例**：
```yaml
post_create:
  - pnpm install
  - pnpm db:migrate    # Add this
```

---

### 修改 Session Start

**场景**：改会话开始时注入的上下文。

**要修改的文件**：

```
.claude/hooks/session-start.py            # Modify: Injection logic
.trellis-local/SKILL.md                   # Update: Document the change
```

→ 详见 `modify-session-start.md`。

---

### 添加核心脚本

**场景**：增加新的自动化脚本。

**要修改的文件**：

```
.trellis/scripts/my-script.py             # Create: Script
.trellis/scripts/common/*.py              # Create/Modify: If shared utilities
.trellis-local/SKILL.md                   # Update: Document the change
```

→ 详见 `add-script.md`。

---

### 修改任务类型

**场景**：增加或修改任务 dev_type（frontend、backend 等）。

**要修改的文件**：

```
.trellis/scripts/task.py                  # Modify: init-context logic
.trellis/tasks/{template}/*.jsonl         # Create: New JSONL templates
.trellis-local/SKILL.md                   # Update: Document the change
```

→ 详见 `change-task-types.md`。

---

## 本目录文档（Documents in This Directory）

| Document | Scenario |
|----------|----------|
| `add-command.md` | 添加 slash commands |
| `add-agent.md` | 添加新 agent 类型 |
| `modify-hook.md` | 修改 hook 行为 |
| `add-spec.md` | 添加 spec 分类 |
| `change-verify.md` | 修改 verify 命令 |
| `add-phase.md` | 添加 workflow 阶段 |
| `modify-session-start.md` | 修改会话开始注入 |
| `add-script.md` | 添加自动化脚本 |
| `change-task-types.md` | 添加任务类型 |
