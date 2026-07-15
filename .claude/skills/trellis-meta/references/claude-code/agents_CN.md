<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/claude-code/agents.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# Agents 参考（Agents Reference）

Trellis agent 系统文档——面向不同开发阶段的专用 AI agents。

---

## 概述（Overview）

Trellis 对**不同任务使用专用 agents**。每个 agent 有特定能力、限制与上下文注入。

**关键洞察**：Agents 在**当前目录**工作——不需要 worktree。Multi-Session（worktree 隔离）是另一套概念。

---

## Agent 类型（Agent Types）

| Agent | Purpose | Can Write | Git Commit |
|-------|---------|-----------|------------|
| `dispatch` | 编排各阶段 | No | 仅通过脚本 |
| `plan` | 评估需求 | Yes（任务目录） | No |
| `research` | 找模式 | No | No |
| `implement` | 写代码 | Yes | No |
| `check` | 评审并自修复 | Yes | No |
| `debug` | 修问题 | Yes | No |

---

## Agent 定义（Agent Definitions）

位置：`.claude/agents/*.md`

### 格式（Format）

```markdown
---
name: agent-name
description: |
  What this agent does.
tools: Read, Write, Edit, Bash, Glob, Grep
model: opus
---
# Agent Name

## Core Responsibilities
...

## Workflow
...

## Forbidden Operations
...
```

---

## Dispatch Agent

**File**: `.claude/agents/dispatch.md`

**Purpose**: 纯编排器——按顺序调用其它 agents。

**关键原则**: 不直接读 specs。Hooks 把上下文注入 subagents。

**Tools**: `Read, Bash`

**Workflow**:
```
1. Run task.py current --source → find session active task directory
2. Read task.json → get next_action array
3. For each phase:
   - implement → Task(subagent_type="implement")
   - check → Task(subagent_type="check")
   - finish → Task(subagent_type="check", prompt="[finish]...")
   - create-pr → Bash("python3 ... create_pr.py")
```

**Forbidden**:
- 直接读 spec 文件
- 修改代码
- Git 操作（create-pr 脚本除外）

---

## Plan Agent

**File**: `.claude/agents/plan.md`

**Purpose**: 评估需求并配置任务目录。

**Tools**: `Read, Bash, Glob, Grep, Task`

**Capabilities**:
- **REJECT** 不清晰/模糊的需求
- 调用 Research Agent 分析代码库
- 用需求创建 `prd.md`
- 配置 `task.json`（branch、scope、phases）
- 初始化 JSONL 会话文件

**Rejection Criteria**:
- 模糊需求（「弄好一点」）
- 信息不完整
- 超出范围
- 可能有害
- 过大（应拆分）

**Output**:
```
task-dir/
├── task.json      # Configured with branch, scope, dev_type
├── prd.md         # Clear requirements
├── implement.jsonl
├── check.jsonl
└── debug.jsonl
```

---

## Research Agent

**File**: `.claude/agents/research.md`

**Purpose**: 查找并解释代码模式。纯调研，不修改。

**Tools**: `Read, Glob, Grep, web search, chrome-devtools`

**Allowed**:
- 描述存在什么
- 描述在哪里
- 描述如何工作
- 描述交互关系

**Forbidden**（除非明确要求）:
- 建议改进
- 批评实现
- 推荐重构
- 修改任何文件
- Git 操作

**Output Format**:
```markdown
## Query Summary
...

## Files Found
- path/to/file.ts - description

## Code Patterns
...

## Related Specs
...
```

---

## Implement Agent

**File**: `.claude/agents/implement.md`

**Purpose**: 按注入的 specs 写代码。

**Tools**: `Read, Write, Edit, Bash, Glob, Grep`

**Workflow**:
1. 理解 specs（来自注入上下文）
2. 理解任务产物（prd.md，若有 design.md，若有 implement.md）
3. 实现功能
4. 自检（跑 lint/typecheck）

**Forbidden**:
- `git commit`
- `git push`
- `git merge`

**Context Injection**: Hook 注入 `implement.jsonl` 条目 + `prd.md` + 若有 `design.md` + 若有 `implement.md`

---

## Check Agent

**File**: `.claude/agents/check.md`

**Purpose**: 评审代码并**自行修复**问题。

**Tools**: `Read, Write, Edit, Bash, Glob, Grep`

**关键原则**: 自己修问题，不要只报告。

**Workflow**:
1. 取变更：`git diff`
2. 对照 specs 检查
3. 直接自修复问题
4. 跑验证（lint、typecheck）
5. 输出完成标记

**Controlled by**: Ralph Loop（SubagentStop hook）

**Completion Markers**:
```
TYPECHECK_FINISH
LINT_FINISH
CODEREVIEW_FINISH
```

---

## Debug Agent

**File**: `.claude/agents/debug.md`

**Purpose**: 修复具体报告的问题。

**Tools**: `Read, Write, Edit, Bash, Glob, Grep`

**Workflow**:
1. 解析问题（优先级 P1 > P2 > P3）
2. 需要时做调研
3. 逐个修复
4. 验证每次修复（跑 typecheck）

**Forbidden**:
- 重构周围代码
- 添加新功能
- 修改无关文件
- 使用非空断言（`x!`）
- Git commit

---

## 调用 Agents（Invoking Agents）

用带 `subagent_type` 的 `Task` 工具：

```javascript
Task(
  subagent_type: "implement",
  prompt: "Implement the login feature",
  model: "opus",
  run_in_background: true  // optional
)
```

### Agent 解析（Agent Resolution）

1. Claude Code 查找 `.claude/agents/{subagent_type}.md`
2. 加载 agent 定义（tools、model、instructions）
3. **PreToolUse hook 触发** → `inject-subagent-context.py`
4. Hook 从 JSONL 文件注入上下文
5. Agent 在完整上下文中运行

---

## 上下文注入（Context Injection）

### 工作方式（How It Works）

```
Task(subagent_type="implement") called
            │
            ▼
    PreToolUse hook fires
            │
            ▼
inject-subagent-context.py runs
            │
            ├── Resolve session active task
            │
            ├── Find task directory from .runtime/sessions/<session-key>.json
            │
            ├── Load implement.jsonl
            │   {"file": ".trellis/spec/cli/backend/index.md", "reason": "..."}
            │   {"file": "src/services/auth.ts", "reason": "..."}
            │
            ├── Read each file content
            │
            └── Build new prompt:
                # Implement Agent Task
                ## Your Context
                === .trellis/spec/cli/backend/index.md ===
                [content]
                === src/services/auth.ts ===
                [content]
                ## Your Task
                [original prompt]
```

### JSONL 文件（JSONL Files）

| File | Agent | Purpose |
|------|-------|---------|
| `implement.jsonl` | implement | 开发 specs、要遵循的模式 |
| `check.jsonl` | check | 检查 specs、质量标准 |
| `debug.jsonl` | debug | 调试上下文、错误报告 |
| `research.jsonl` | research | （可选）调研范围 |

---

## 多智能体工作流（Multi-Agent Workflow）

在**当前目录**（无 worktree）：

```
User request
    │
    ▼
Orchestrator (you or dispatch)
    │
    ├── Task(subagent_type="research")
    │   └── Returns: code patterns, relevant files
    │
    ├── Task(subagent_type="implement")
    │   └── Returns: implemented code
    │
    ├── Task(subagent_type="check")
    │   └── Returns: reviewed & fixed code
    │
    └── Human commits
```

### 任务工作流（来自 /trellis:start）（Task Workflow）

```
1. User describes task
2. AI classifies (Question / Trivial / Development Task)
3. For Development Task:
   a. Research Agent → analyze codebase
   b. Create task directory + JSONL files
   c. task.py start → set session active task
   d. Implement Agent → write code
   e. Check Agent → review & fix
   f. Human tests and commits
```

---

## 添加自定义 Agents（Adding Custom Agents）

### 1. 创建定义（Create Definition）

`.claude/agents/my-agent.md`:
```markdown
---
name: my-agent
description: |
  What this agent specializes in.
tools: Read, Write, Edit, Bash, Glob, Grep
model: opus
---
# My Agent

## Core Responsibilities
1. ...

## Workflow
1. ...

## Forbidden Operations
- ...
```

### 2. 更新 Hook（Update Hook）

编辑 `.claude/hooks/inject-subagent-context.py`：

```python
# Add constant
AGENT_MY_AGENT = "my-agent"

# Add to list
AGENTS_ALL = (..., AGENT_MY_AGENT)

# Add context function
def get_my_agent_context(repo_root, task_dir):
    # Load my-agent.jsonl or fallback
    ...

# Add to main switch
elif subagent_type == AGENT_MY_AGENT:
    context = get_my_agent_context(repo_root, task_dir)
    new_prompt = build_my_agent_prompt(original_prompt, context)
```

### 3. 创建 JSONL（Create JSONL）

在任务目录中创建 `my-agent.jsonl`：
```jsonl
{"file": ".trellis/spec/my-spec.md", "reason": "My agent spec"}
```

### 4.（可选）加入 Dispatch（Add to Dispatch）

更新 `task.json` 默认阶段：
```json
"next_action": [
  {"phase": 1, "action": "my-agent"},
  ...
]
```

---

## 与 Multi-Session 对比（vs Multi-Session）

| Aspect | Multi-Agent | Multi-Session |
|--------|-------------|---------------|
| **What** | 当前目录中顺序执行多个 agents | 并行隔离会话 |
| **Where** | 当前目录 | 独立 worktrees |
| **Isolation** | 共享文件系统 | 独立文件系统 |
| **Use case** | 常规开发 | 并行任务 |
| **Worktree** | 不需要 | 必需 |

Multi-Agent 是 **agent 系统**——dispatch 调用 implement、check 等。

Multi-Session 是 **并行执行**——多个 worktrees 同时运行。

两者可组合：Multi-Session 在每个 worktree 中跑 Multi-Agent 工作流。
