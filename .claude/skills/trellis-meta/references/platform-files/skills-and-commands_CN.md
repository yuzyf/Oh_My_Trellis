<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/platform-files/skills-and-commands.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# Skills、Commands、Prompts 与 Workflows（Skills, Commands, Prompts, And Workflows）

Skills 与 commands 是用户与 Trellis 交互的文本入口。不同平台命名不同，但核心目的相同：告诉 AI 在用户表达某意图时如何进入 Trellis 流程。

## 概念差异（Conceptual Differences）

| Type | Trigger mode | Best for |
| --- | --- | --- |
| skill | AI 自动匹配或用户显式提及 | 长期能力、workflow 规则、修改指南。 |
| command | 用户显式调用 | continue、finish-work 等明确操作入口。 |
| prompt | 用户显式调用或平台选择 | 类似 command，但是平台 prompt 格式。 |
| workflow | 用户显式选择或平台自动匹配 | 无 sub-agent/hook 时引导主会话。 |

Trellis workflow skills 通常共享同一语义集合：brainstorm、before-dev、check、update-spec、break-loop。`trellis-meta` 等多文件内置 skills 使用分层 references。

## 常见路径（Common Paths）

| Platform | Common entries |
| --- | --- |
| Claude Code | `.claude/skills/`、`.claude/commands/` |
| Cursor | `.cursor/skills/`、`.cursor/commands/` |
| OpenCode | `.opencode/skills/`、`.opencode/commands/` |
| Codex | `.agents/skills/`、`.codex/skills/` |
| Kilo | `.kilocode/skills/`、`.kilocode/workflows/` |
| Kiro | `.kiro/skills/` |
| Gemini CLI | `.agents/skills/`、`.gemini/commands/` |
| Antigravity | `.agent/skills/`、`.agent/workflows/` |
| Devin | `.devin/skills/`、`.devin/workflows/` |
| Qoder | `.qoder/skills/`、`.qoder/commands/` |
| CodeBuddy | `.codebuddy/skills/`、`.codebuddy/commands/` |
| GitHub Copilot | `.github/skills/`、`.github/prompts/` |
| Factory Droid | `.factory/skills/`、`.factory/commands/` |
| Pi Agent | `.pi/skills/` |
| Reasonix | `.reasonix/skills/` |
| ZCode | `.agents/skills/`、`.zcode/commands/` |

在用户项目中，以 init 实际生成的文件为准。

## Skill 结构（Skill Structure）

常见 skill 是一个目录：

```text
trellis-meta/
├── SKILL.md
└── references/
```

`SKILL.md` 应告诉 AI：

- 何时使用本 skill。
- 当前任务应先读哪份 reference。
- 不要做什么。

References 放更长说明，避免入口文件塞满一切。

## Command/Prompt/Workflow 结构（Command/Prompt/Workflow Structure）

Commands、prompts、workflows 通常是单文件。内容应包括：

- 何时使用。
- 要读哪些 `.trellis/` 文件。
- 要跑哪些脚本。
- 完成后如何汇报。

它们不应存任务状态；任务状态属于 `.trellis/tasks/` 与 `.trellis/.runtime/`。

## 本地变更场景（Local Change Scenarios）

| User need | Edit location |
| --- | --- |
| 改 AI 自动触发规则 | 对应 skill 的 frontmatter description。 |
| 改用户命令行为 | 对应 command/prompt/workflow 文件。 |
| 增加项目本地 skill | 平台 skill 目录，或共享 `.agents/skills/`。 |
| 让多平台共享同一能力 | 在各平台 skill 目录写等价 skills，或在支持共享层的平台使用 `.agents/skills/`。 |
| 改 finish/continue 入口 | 平台 commands/prompts/workflows。 |

## 修改原则（Modification Principles）

1. **入口文件保持短；references 承载长内容**。对 `trellis-meta` 这类多文件 skills 尤其重要。
2. **触发描述要具体**。描述太宽会误触发；太窄可能不触发。
3. **跨平台保持语义一致**。文件格式可以不同，行为描述应匹配。
4. **项目专属能力放本地 skills**。不要把团队私有流程写进公开的 `trellis-meta`。

若用户只是希望本地 AI 再多知道一条项目规则，通常创建项目本地 skill 或更新 `.trellis/spec/`，而不是改 Trellis 内置 workflow skill。
