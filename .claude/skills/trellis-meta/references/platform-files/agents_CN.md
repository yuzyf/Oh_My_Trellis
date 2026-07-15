<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/platform-files/agents.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# Agents

Trellis agent 文件定义专职角色。用户项目中常见 Trellis agents 为：

- `trellis-research`
- `trellis-implement`
- `trellis-check`

文件位置与格式因平台而异，但职责边界应保持一致。

## Agent 职责（Agent Responsibilities）

| Agent | Responsibility |
| --- | --- |
| `trellis-research` | 调查问题，把发现写入当前任务的 `research/`。 |
| `trellis-implement` | 对照 `prd.md`、可选 `design.md` / `implement.md`、`implement.jsonl` 及相关 spec/research 做实现。 |
| `trellis-check` | 审查变更、修复发现的问题，并跑必要检查。 |

Agent 文件不应变成泛泛的聊天 prompt。它们应定义输入来源、写边界、是否可改代码，以及如何汇报结果。

## 常见路径（Common Paths）

| Platform | Agent path |
| --- | --- |
| Claude Code | `.claude/agents/trellis-*.md` |
| Cursor | `.cursor/agents/trellis-*.md` |
| OpenCode | `.opencode/agents/trellis-*.md` |
| Codex | `.codex/agents/trellis-*.toml` |
| Kiro | `.kiro/agents/trellis-*.json` |
| Gemini CLI | `.gemini/agents/trellis-*.md` |
| Qoder | `.qoder/agents/trellis-*.md` |
| CodeBuddy | `.codebuddy/agents/trellis-*.md` |
| Factory Droid | `.factory/droids/trellis-*.md` |
| Pi Agent | `.pi/agents/trellis-*.md` |
| Reasonix | `.reasonix/skills/trellis-*/SKILL.md`（subagent frontmatter） |
| ZCode | `.zcode/cli/agents/trellis-*.md` |

GitHub Copilot 的 agent/prompt 支持由 `.github/agents/`、`.github/prompts/`、`.github/skills/` 等目录组合提供；以用户项目中实际生成的文件为准。

Kilo、Antigravity、Devin 等主会话 workflow 平台可能没有 Trellis sub-agent 文件。它们通常依赖 workflows/skills 引导主会话。

## 两种上下文加载模式（Two Context Loading Modes）

### hook push

平台 hook 在 agent 启动前注入任务上下文。Agent 文件本身可更专注职责与边界。

常见于支持 agent hooks 的平台。

### agent pull

Agent 文件要求 agent 启动后读取：

- `python3 ./.trellis/scripts/task.py current --source`
- `implement.jsonl` 或 `check.jsonl`
- JSONL 引用的 spec/research 文件
- 当前任务 `prd.md`
- 如有则读 `design.md`
- 如有则读 `implement.md`

此模式适合 hooks 无法可靠改写 sub-agent prompt 的平台。

## 本地变更场景（Local Change Scenarios）

| User need | Edit location |
| --- | --- |
| Implement agent 必须遵守额外限制 | 平台的 `trellis-implement` agent 文件。 |
| Check agent 必须跑项目专用命令 | `trellis-check` agent 文件，必要时还有 `.trellis/spec/`。 |
| Research agent 必须输出固定格式 | `trellis-research` agent 文件。 |
| Agent 读不到任务上下文 | Agent prelude 或 `inject-subagent-context` hook。 |
| 增加项目专用 agent | 平台 agent 目录 + 相关 workflow/command/skill 入口。 |

## 修改原则（Modification Principles）

1. **职责保持单一**。不要把 research、implement、check 混进一个 agent。
2. **明确读顺序**。Agents 必须知道从活跃任务出发，读 jsonl/spec 上下文，再读 `prd.md`、如有则 `design.md`、如有则 `implement.md`。
3. **明确写边界**。Research 通常只写 `research/`；implement 可写代码；check 可修问题。
4. **多平台项目保持语义同步**。若用户同时配了 Claude、Codex、Cursor，决定改一个平台的 agent 是否也要应用到其他平台。

## 不要默认改上游模板（Do Not Default To Editing Upstream Templates）

本地 AI 默认应修改用户项目内的平台 agent 文件。仅当用户明确要把改动贡献回 Trellis 时，再讨论上游模板源。
