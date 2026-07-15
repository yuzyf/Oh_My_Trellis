<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/platform-files/hooks-and-settings.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# Hooks 与 Settings（Hooks And Settings）

Hooks/settings 是连接平台与 Trellis 的入口层。它们决定平台在哪些事件上运行哪些 scripts、plugins 或 extensions。

## Settings 职责（Settings Responsibilities）

settings/config 文件通常注册：

- session-start hook：新会话开始或上下文重置时注入 Trellis 总览。
- workflow-state hook：从 `.trellis/workflow.md` 解析 `[workflow-state:STATUS]` 块，并在每次用户输入时发出与当前任务 `status` 匹配的正文。只做解析；脚本不内嵌回退内容。
- sub-agent context hook：implementation/check/research agents 启动时注入任务上下文。
- shell/session bridge：让 shell 命令看到同一 Trellis session 身份。
- 平台 plugin 或 extension 入口。

常见文件：

| Platform | settings/config |
| --- | --- |
| Claude Code | `.claude/settings.json` |
| Cursor | `.cursor/hooks.json` |
| Codex | `.codex/hooks.json`、`.codex/config.toml` |
| OpenCode | `.opencode/package.json`、`.opencode/plugins/*` |
| Kiro | `.kiro/hooks/` + 平台 config |
| Gemini CLI | `.gemini/settings.json` |
| Qoder | `.qoder/settings.json` |
| CodeBuddy | `.codebuddy/settings.json` |
| GitHub Copilot | `.github/copilot/hooks.json` |
| Factory Droid | `.factory/settings.json` |
| Pi Agent | `.pi/settings.json`、`.pi/extensions/trellis/` |

Reasonix 与 ZCode 是 pull-based 平台，不使用 hooks 或 settings 文件；其 agent 文件含有启动后读取上下文的 prelude 说明。

这些文件是否存在于项目中，取决于用户运行了哪些 `trellis init --<platform>` 标志。

## Hook 脚本类型（Hook Script Types）

| Script | Purpose |
| --- | --- |
| `session-start.py` | 生成 session-start 上下文。 |
| `inject-workflow-state.py` | 解析 `.trellis/workflow.md` 中的 `[workflow-state:STATUS]` 块，发出与当前任务 status 匹配的正文。无匹配块时回退为 `Refer to workflow.md for current step.`。 |
| `inject-subagent-context.py` | 向 sub-agents 注入 PRD、JSONL 上下文及相关 spec/research。 |
| `inject-shell-session-context.py` | 让 shell 命令继承 Trellis session 身份。 |

并非每个平台都有每种 hook。不要因为某平台缺 hook 就从另一平台拷贝文件；先确认该平台是否支持对应事件。

## 本地变更场景（Local Change Scenarios）

| User need | Edit location |
| --- | --- |
| AI 在新会话应看到更多/更少上下文 | 平台 `session-start` hook。 |
| 每轮提示策略要改 | `.trellis/workflow.md` 中的 `[workflow-state:STATUS]` 块。Hook 原样解析 workflow.md——通常无需改脚本。 |
| Sub-agent 读不到 PRD/spec | `inject-subagent-context` hook 或 agent prelude。 |
| shell 中的 `task.py current` 没有活跃任务 | Shell/session bridge hook 或平台环境变量配置。 |
| 禁用某次自动注入 | settings/config 中对应的 hook 注册。 |

## 修改原则（Modification Principles）

1. **Settings 接线；hooks 定义行为**。只改 hook，平台可能永远不调用它。只改 settings，行为可能不变。
2. **先确认平台事件名**。不同平台对 SessionStart、UserPromptSubmit、AgentSpawn、shell execution 等事件命名不同。
3. **Hooks 读本地 `.trellis/`，不是上游源码**。用户项目中的 `.trellis/scripts/` 与 `.trellis/workflow.md` 是默认目标。
4. **错误必须可见**。Hook 失败应告诉用户哪些没注入，而不是静默让 AI 没有上下文。

## 排障路径（Troubleshooting Path）

若用户说「AI 没读到 Trellis 状态」：

1. 检查平台 settings 是否注册了 hook。
2. 检查 hook 文件是否存在。
3. 手动运行 hook 依赖的 `.trellis/scripts/get_context.py` 或 `task.py current --source`。
4. 检查 `.trellis/.runtime/sessions/` 是否有活跃任务状态。
5. 检查平台 shell 是否传递 session 身份。
