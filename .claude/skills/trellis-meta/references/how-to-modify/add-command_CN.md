<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/how-to-modify/add-command.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# How To: 添加 Slash Command

添加新的 `/trellis:my-command` 命令。

**Platform**：All（Claude Code + Cursor）

---

## 要修改的文件（Files to Modify）

| File | Action | Required |
|------|--------|----------|
| `.claude/commands/trellis/my-command.md` | Create | Yes |
| `.cursor/commands/my-command.md` | Create | Optional |
| `trellis-local/SKILL.md` | Update | Yes |

---

## Step 1: 创建命令文件

创建 `.claude/commands/trellis/my-command.md`：

```markdown
---
name: my-command
description: Short description of what the command does
---

# My Command

## Purpose

Detailed description of the command's purpose.

## When to Use

- Scenario 1
- Scenario 2

## Workflow

1. First step
2. Second step
3. Third step

## Output

What the command produces.
```

### 命令命名约定（Command Name Convention）

- 使用 kebab-case：`my-command`，不要用 `myCommand`
- 需要时加分类前缀：`check-cross-layer`、`before-dev`

---

## Step 2: 镜像到 Cursor（可选）

若支持 Cursor，复制到 `.cursor/commands/my-command.md`。

**注意**：Cursor commands 没有 `trellis:` 前缀。

---

## Step 3: 在 trellis-local 中记录

更新 `.claude/skills/trellis-local/SKILL.md`：

```markdown
## Commands

### Added Commands

#### /trellis:my-command
- **File**: `.claude/commands/trellis/my-command.md`
- **Platform**: [ALL]
- **Purpose**: What it does
- **Added**: 2026-01-31
- **Reason**: Why it was added
```

---

## 示例（Examples）

### 简单命令

```markdown
---
name: check-types
description: Run TypeScript type checking
---

# Check Types

Run `pnpm typecheck` and report results.

## Usage

Run this command after making code changes to verify type safety.
```

### 带参数的命令

Commands 可引用用户输入或上下文：

```markdown
---
name: review-file
description: Review a specific file for code quality
---

# Review File

## Input

User should specify which file to review.

## Workflow

1. Read the specified file
2. Check against relevant specs
3. Report issues found
```

---

## 测试（Testing）

1. 运行命令：`/trellis:my-command`
2. 验证行为与描述一致
3. 测试边界情况

---

## 检查清单（Checklist）

- [ ] 命令文件已创建并有正确 frontmatter
- [ ] 需要时已镜像到 Cursor
- [ ] 已在 trellis-local 记录
- [ ] 已测试命令
