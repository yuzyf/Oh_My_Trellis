<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/customize-local/add-project-local-conventions.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 添加项目本地约定（Add Project-Local Conventions）

很多时候用户并不需要改 Trellis 机制，而是需要本地 AI 理解团队约定。这时优先写 `.trellis/spec/` 或项目本地 skill，而不是改 `trellis-meta`。

## 内容放哪里（Where To Put Things）

| Content type | Location |
| --- | --- |
| 代码必须遵守的规则 | `.trellis/spec/<layer>/` |
| 跨层思考方法 | `.trellis/spec/guides/` |
| 面向项目专属流程的 AI 能力 | 平台本地 skill |
| 一次性任务材料 | `.trellis/tasks/<task>/` |
| 会话摘要 | `.trellis/workspace/<developer>/journal-N.md` |

## 创建项目本地 Skill（Create A Project-Local Skill）

若用户希望 AI 知道「本项目如何定制 Trellis」，创建本地 skill：

```text
.claude/skills/trellis-local/
└── SKILL.md
```

示例：

```md
---
name: trellis-local
description: "Project-local Trellis customizations for this repository. Use when changing this project's Trellis workflow, hooks, local agents, or team-specific conventions."
---

# Trellis Local

## Local Scope

This skill documents this repository's Trellis customizations only.

## Custom Workflow Rules

- ...

## Local Hook Changes

- ...

## Local Agent Changes

- ...
```

多平台项目可在其他平台 skill 目录放等价版本，或在支持共享层的平台使用 `.agents/skills/`。

## 写入 `.trellis/spec/`（Write To `.trellis/spec/`）

若内容是编码约定，写入 spec。例如：

```text
.trellis/spec/backend/error-handling.md
.trellis/spec/frontend/components.md
.trellis/spec/guides/cross-platform-thinking-guide.md
```

写完后更新对应 `index.md`，让 AI 能从入口找到新规则。

## 让当前任务用上新约定（Make The Current Task Use New Conventions）

写完 spec 后，把它加入当前任务上下文：

```bash
python3 ./.trellis/scripts/task.py add-context <task> implement ".trellis/spec/backend/error-handling.md" "Error handling conventions"
python3 ./.trellis/scripts/task.py add-context <task> check ".trellis/spec/backend/error-handling.md" "Review error handling"
```

## 不要把项目私有规则存进 `trellis-meta`（Do Not Store Project-Private Rules In `trellis-meta`）

`trellis-meta` 是用于理解 Trellis 架构与本地定制入口的公共 skill。项目私有内容放在：

- `.trellis/spec/`
- 项目本地 skill
- 当前任务
- workspace journal

这样可避免将来 Trellis 内置 `trellis-meta` 更新时覆盖团队自己的约定。
