<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/customize-local/change-agents.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 修改本地 Agents（Change Local Agents）

当用户想改 `trellis-research`、`trellis-implement` 或 `trellis-check` 的行为时，编辑用户项目中的平台 agent 文件。

## 先读这些文件（Read These Files First）

1. 目标平台 agent 目录
2. `.trellis/workflow.md` 的 Phase 2 / research 路由
3. 当前任务的 `prd.md`
4. 当前任务的 `implement.jsonl` / `check.jsonl`
5. 相关 hook 或 agent prelude

## 常见路径（Common Paths）

| Platform | Path |
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

以用户项目中的实际路径为准。

## 常见需求（Common Needs）

| Need | Which agent to edit |
| --- | --- |
| Research 必须写文件，不能只在聊天里回复 | `trellis-research` |
| 实现前必须读某些本地 specs | `trellis-implement` + `implement.jsonl` 配置规则 |
| 检查时必须跑特定命令 | `trellis-check` |
| Agent 不得修改某些目录 | 对应 agent 的写边界说明 |
| Agent 输出格式必须固定 | 对应 agent 的 final/reporting 说明 |

## 修改原则（Modification Principles）

1. **保持角色边界**：research 调查并落盘；implement 写实现；check 审查并修复。
2. **不要把项目 specs 硬编码进 agents**：长期 specs 属于 `.trellis/spec/`；agents 负责读取它们。
3. **读顺序要明确**：活跃任务 -> PRD -> info -> JSONL -> spec/research。
4. **写边界要明确**：哪些目录可写，哪些不可写。
5. **跨平台同步**：用户配置了多平台时，决定只改当前平台还是全部平台 agents。

## Agent Pull 平台（Agent Pull Platforms）

若 agent 文件含有「启动后读取 task/context」的 prelude，编辑时不要删掉这些步骤。否则 agent 只会基于聊天上下文工作，绕过 Trellis 的核心机制。

## Hook Push 平台（Hook Push Platforms）

若上下文由 hook 注入，agent 文件仍应保留职责边界。不要因为 hook 会注入上下文，就把 agent 里的 PRD/spec 要求删掉。
