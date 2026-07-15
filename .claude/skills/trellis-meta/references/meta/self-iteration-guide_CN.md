<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/meta/self-iteration-guide.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# Trellis 自迭代指南（Self-Iteration Guide）

定制 Trellis 时如何维护 skill 文档。

---

## 核心原则（Core Principle）

**每一处 Trellis 修改都必须记入对应 skill。**

```
Modification to Trellis → Update trellis-local (project skill)
Update to Trellis itself → Update trellis-meta (meta skill)
```

---

## 决策树（Decision Tree）

```
Is this a modification to Trellis?
│
├── YES: What kind?
│   │
│   ├── Project-specific customization
│   │   └── Update .claude/skills/trellis-local/SKILL.md
│   │
│   ├── Bug fix to core Trellis
│   │   └── Update ~/.claude/skills/trellis-meta/
│   │       (or project copy if reviewing first)
│   │
│   └── New feature to core Trellis
│       └── Update trellis-meta after release
│
└── NO: Just using Trellis
    └── No skill update needed
```

---

## 自迭代工作流（Self-Iteration Workflow）

### 步骤 1：改动之前（Before Making Changes）

```bash
# Check if project skill exists
ls .claude/skills/trellis-local/SKILL.md

# If not, create it from template
mkdir -p .claude/skills/trellis-local
# Copy template from trellis-meta/references/trellis-local-template.md
```

### 步骤 2：做 Trellis 修改（Make the Trellis Modification）

完成你的工作：添加命令、修改 hook 等。

### 步骤 3：写入项目 skill（Document in Project Skill）

打开 `.claude/skills/trellis-local/SKILL.md` 并：

1. **找到正确章节**（Commands/Agents/Hooks/Specs/Workflow）
2. **按模板添加条目**
3. **更新 changelog**
4. **更新摘要计数**

### 步骤 4：核对文档（Verify Documentation）

自问：
- [ ] 另一名 AI 能否理解改了什么？
- [ ] 「为什么」是否写清？
- [ ] 是否列出受影响文件？
- [ ] 是否记录日期？

---

## 文档模板（Documentation Templates）

### 新命令（New Command）

```markdown
#### /trellis:my-command
- **File**: `.claude/commands/trellis/my-command.md`
- **Purpose**: Brief description of what it does
- **Added**: 2026-01-31
- **Reason**: Why this command was needed

**Usage**:
```
/trellis:my-command [args]
```

**Example**:
User asks "..." → Command does "..."
```

### 新 Agent（New Agent）

```markdown
#### my-agent
- **File**: `.claude/agents/my-agent.md`
- **Purpose**: What this agent specializes in
- **Tools**: Read, Write, Edit, Bash, Glob, Grep
- **Model**: opus
- **Added**: 2026-01-31
- **Reason**: Why this agent was needed

**Hook Integration**:
- Added to `inject-subagent-context.py` at line X
- Uses `my-agent.jsonl` for context

**Invocation**:
```
Task(subagent_type="my-agent", prompt="...")
```
```

### Hook 修改（Hook Modification）

```markdown
#### inject-subagent-context.py
- **Hook Event**: PreToolUse:Task
- **Change**: Added handling for `my-agent` subagent type
- **Lines Modified**: 45-67, 120-135
- **Date**: 2026-01-31
- **Reason**: Support new agent type

**Code Changes**:

```python
# Added constant
AGENT_MY_AGENT = "my-agent"

# Added to agent list
AGENTS_ALL = (..., AGENT_MY_AGENT)

# Added context function
def get_my_agent_context(repo_root, task_dir):
    ...
```
```

### 新增 Spec 分类（Spec Category Addition）

```markdown
#### security/
- **Path**: `.trellis/spec/security/`
- **Purpose**: Security guidelines for the project
- **Files**:
  - `index.md` - Category overview
  - `auth-guidelines.md` - Authentication patterns
  - `input-validation.md` - Validation requirements
- **Added**: 2026-01-31
- **Reason**: Project requires security-focused development

**JSONL Integration**:
```jsonl
{"file": ".trellis/spec/security/index.md", "reason": "Security guidelines"}
```
```

### 工作流变更（Workflow Change）

```markdown
#### Custom Phase Order
- **What**: Changed default task phases to include research phase
- **Files Affected**:
  - `.trellis/scripts/task.py` (init-context function)
  - Default task.json template
- **Date**: 2026-01-31
- **Reason**: All tasks in this project need research first

**New Default next_action**:
```json
[
  {"phase": 1, "action": "research"},
  {"phase": 2, "action": "implement"},
  {"phase": 3, "action": "check"},
  {"phase": 4, "action": "finish"},
  {"phase": 5, "action": "create-pr"}
]
```
```

---

## Changelog 格式（Changelog Format）

```markdown
### 2026-01-31 - Feature: Custom Research Phase
- Added research phase as default first phase
- Modified task.py init-context
- Updated task.json template
- Reason: Project complexity requires upfront research

### 2026-01-30 - Bugfix: Hook Timeout
- Increased ralph-loop.py timeout from 10s to 30s
- Reason: Complex verification commands were timing out

### 2026-01-29 - Initial Setup
- Initialized trellis-local skill
- Base Trellis version: 0.3.0
```

---

## 多项目场景（Multi-Project Scenario）

同时维护多个 Trellis 项目时：

```
~/projects/
├── project-a/
│   └── .claude/skills/trellis-local/   # Project A customizations
├── project-b/
│   └── .claude/skills/trellis-local/   # Project B customizations
└── project-c/
    └── .claude/skills/trellis-local/   # Project C customizations

~/.claude/skills/
└── trellis-meta/                        # Shared meta-skill (vanilla Trellis)
```

**每个项目有自己的 `trellis-local`**，记录该项目的具体定制。

**meta skill 是共享的**，记录原版（vanilla）Trellis。

---

## 升级工作流（Upgrade Workflow）

升级 Trellis 到新版本时：

### 1. 审阅新版本变更（Review New Version Changes）

```bash
# Compare new meta-skill with current
diff -r ~/.claude/skills/trellis-meta/references/ \
        ./new-trellis-meta/references/
```

### 2. 检查冲突（Check for Conflicts）

审阅 `trellis-local` 中的每一处定制：
- 新版本是否已原生包含该功能？
- 新版本是否破坏该定制？
- 该定制能否简化？

### 3. 谨慎合并（Merge Carefully）

```bash
# Backup current meta-skill
cp -r ~/.claude/skills/trellis-meta ~/.claude/skills/trellis-meta.backup

# Update meta-skill
cp -r ./new-trellis-meta/* ~/.claude/skills/trellis-meta/
```

### 4. 更新项目 skills（Update Project Skills）

在 `trellis-local` 中添加迁移说明：

```markdown
### 2026-02-01 - Upgraded to Trellis 0.4.0
- Updated meta-skill to 0.4.0
- Kept custom `security-agent` (not in vanilla)
- Migrated `my-command` to new command format
- Removed `old-hook` customization (now in vanilla)
```

---

## AI 指令（AI Instructions）

当 AI 修改 Trellis 时，必须：

1. **检查** 项目中是否存在 `trellis-local`
2. **若不存在**，从模板创建
3. **在改动后立即** 记录变更
4. **用日期与描述** 更新 changelog
5. **核对** 文档是否完整

**永远不要** 为项目专属改动去修改 `trellis-meta`。

**始终** 告诉用户记录了什么。

示例 AI 回复：
> "I've added the `/trellis:deploy` command and documented it in `.claude/skills/trellis-local/SKILL.md` under the Commands section."
