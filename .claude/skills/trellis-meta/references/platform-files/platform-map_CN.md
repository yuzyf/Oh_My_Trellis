<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/platform-files/platform-map.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 平台文件地图（Platform File Map）

本页按平台列出用户项目中常见的 Trellis 文件位置。实际项目中是否存在某平台目录，取决于用户运行了哪些 `trellis init --<platform>` 命令。

## 矩阵（Matrix）

| Platform | CLI flag | Main directory | Skill directory | Agent directory | Hooks/extensions |
| --- | --- | --- | --- | --- | --- |
| Claude Code | `--claude` | `.claude/` | `.claude/skills/` | `.claude/agents/` | `.claude/hooks/` + `.claude/settings.json` |
| Cursor | `--cursor` | `.cursor/` | `.cursor/skills/` | `.cursor/agents/` | `.cursor/hooks.json` + `.cursor/hooks/` |
| OpenCode | `--opencode` | `.opencode/` | `.opencode/skills/` | `.opencode/agents/` | `.opencode/plugins/` |
| Codex | `--codex` | `.codex/` | `.agents/skills/` | `.codex/agents/` | `.codex/hooks/` + `.codex/hooks.json` |
| Kilo | `--kilo` | `.kilocode/` | `.kilocode/skills/` | Usually none | `.kilocode/workflows/` |
| Kiro | `--kiro` | `.kiro/` | `.kiro/skills/` | `.kiro/agents/` | `.kiro/hooks/` |
| Gemini CLI | `--gemini` | `.gemini/` | `.agents/skills/` | `.gemini/agents/` | `.gemini/settings.json` + `.gemini/hooks/` |
| Antigravity | `--antigravity` | `.agent/` | `.agent/skills/` | Usually none | `.agent/workflows/` |
| Devin | `--devin` | `.devin/` | `.devin/skills/` | Usually none | `.devin/workflows/` |
| Qoder | `--qoder` | `.qoder/` | `.qoder/skills/` | `.qoder/agents/` | `.qoder/hooks/` + `.qoder/settings.json` |
| CodeBuddy | `--codebuddy` | `.codebuddy/` | `.codebuddy/skills/` | `.codebuddy/agents/` | `.codebuddy/hooks/` + `.codebuddy/settings.json` |
| GitHub Copilot | `--copilot` | `.github/` | `.github/skills/` | `.github/agents/` | `.github/copilot/hooks/` + prompts |
| Factory Droid | `--droid` | `.factory/` | `.factory/skills/` | `.factory/droids/` | `.factory/hooks/` + settings |
| Pi Agent | `--pi` | `.pi/` | `.pi/skills/` | `.pi/agents/` | `.pi/extensions/trellis/`（原生 `trellis_subagent` 工具）+ `.pi/settings.json` |
| Reasonix | `--reasonix` | `.reasonix/` | `.reasonix/skills/` | None — sub-agents 是带 `runAs: subagent` frontmatter 的 skills | None |
| ZCode | `--zcode` | `.zcode/` | `.agents/skills/` | `.zcode/cli/agents/` | pull-based prelude（无 hooks） |

## 能力分组（Capability Groups）

### Trellis Sub-Agent 支持

这些平台通常有 `trellis-research`、`trellis-implement`、`trellis-check` 文件：

- Claude Code
- Cursor
- OpenCode
- Codex
- Kiro
- Gemini CLI
- Qoder
- CodeBuddy
- GitHub Copilot
- Factory Droid
- Pi Agent
- Reasonix（以 `.reasonix/skills/` 下带 `runAs: subagent` 的 skills 交付，不是独立 `agents/` 目录）
- ZCode

改 implementation/check/research 行为时，先找对应平台 agent 文件。

### 原生 Trellis Sub-Agent 工具（Native Trellis Sub-Agent Tool）

有些平台暴露宿主运行时理解的一等工具。模型像调用其他工具一样调用它，宿主渲染进度卡、对照 `.<platform>/agents/` 校验 agent 名，并强制分发模式。

- Pi Agent — `trellis_subagent` 工具，定义于 `.pi/extensions/trellis/index.ts`。支持 `single` / `parallel` / `chain` 分发模式，并发出实时 `trellis-subagent-progress` 事件。

在这些平台上改 sub-agent 分发行为时，编辑 extension 文件，**不要**改 agent markdown——agent markdown 定义职责，但宿主 extension 拥有分发、校验与进度渲染。

### 主会话 Workflow 平台（Main-Session Workflow Platforms）

这些平台更多依赖 workflows/skills 引导主会话：

- Kilo
- Antigravity
- Devin

改行为时先检查 workflows 与 skills。不要假设存在 Trellis sub-agents。

### 共享 `.agents/skills/`

Codex 会写入共享的 `.agents/skills/` 层。一些支持 agentskills.io 的工具也能读该目录。若用户希望多个兼容工具共享一个 skill，优先考虑 `.agents/skills/`，但不要假设每个平台都会读。

## 修改平台文件时的决策规则（Decision Rules When Modifying Platform Files）

1. 用户指定了平台：只改该平台目录，除非共享 workflow/spec 文件也必须变。
2. 用户说「所有平台都要这样」：逐平台同步等价入口；不要只改一个目录。
3. 用户只说「我的 AI」：检查项目中实际存在的配置目录，推断当前 AI 平台。
4. 用户要项目规则：优先 `.trellis/spec/` 或项目本地 skill。
5. 用户要 Trellis 行为：编辑 `.trellis/workflow.md` 外加平台 hooks/agents/skills/commands。

## 路径不一致时（When Paths Differ）

平台生态会变，用户项目也可能已定制。若本表与本地文件不一致，以用户项目中的实际 settings/config 为准：

- 检查 settings 注册的 hook。
- 检查 command/prompt/workflow 指向的脚本。
- 以 agent 文件当前写明的读规则判断行为。

不要仅因自定义文件不在本路径表中就删除它。
