<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/platform-files/overview.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 平台文件总览（Platform Files Overview）

Trellis 把同一套本地架构接到不同 AI 工具上。`.trellis/` 存共享运行时；平台目录存适配文件，定义各 AI 工具如何进入 Trellis。

本地 AI 修改 Trellis 时，应先区分两类文件：

- **共享文件**：`.trellis/workflow.md`、`.trellis/tasks/`、`.trellis/spec/`、`.trellis/scripts/`。
- **平台文件**：`.claude/`、`.codex/`、`.cursor/`、`.opencode/`、`.kiro/`、`.gemini/`、`.qoder/`、`.codebuddy/`、`.github/`、`.factory/`、`.pi/`、`.kilocode/`、`.agent/`、`.devin/`、`.reasonix/`、`.zcode/` 及类似目录。

平台文件不存业务状态。它们让对应 AI 工具读取 Trellis 状态、调用 Trellis 脚本、加载 Trellis skills/agents/hooks。

## 平台文件类别（Platform File Categories）

| Category | Common paths | Purpose |
| --- | --- | --- |
| settings/config | `.claude/settings.json`、`.codex/hooks.json`、`.qoder/settings.json` | 注册 hooks、plugins、extensions 或平台行为。 |
| hooks/plugins/extensions | `.claude/hooks/`、`.opencode/plugins/`、`.pi/extensions/` | 在 session start、用户输入、agent 启动、shell 执行等事件注入上下文。 |
| agents | `.claude/agents/`、`.codex/agents/`、`.kiro/agents/` | 定义 `trellis-research`、`trellis-implement`、`trellis-check`。 |
| skills | `.claude/skills/`、`.agents/skills/`、`.qoder/skills/` | 可自动触发或按需读取的能力描述。 |
| commands/prompts/workflows | `.cursor/commands/`、`.github/prompts/`、`.devin/workflows/` | 用户显式调用的入口。 |

## 三种平台集成模式（Three Platform Integration Modes）

### 1. Hook / Extension 驱动

这些平台可在特定事件触发脚本或插件，主动把 Trellis 上下文注入 AI。

常见能力：

- session-start 注入 `.trellis/` 总览。
- 每轮用户输入的 workflow-state 提示。
- sub-agent 启动时注入 PRD/spec/research。
- Shell 命令继承 session 身份。

要改「AI 何时知道什么」，先检查 hooks/plugins/extensions 与 settings。

### 2. Agent Prelude / 拉取式（Pull-Based）

有些平台无法可靠地用 hooks 改写 sub-agent prompt，因此 agent 文件本身要求 agent 启动后读取活跃任务、PRD 与 JSONL 上下文。

要改 sub-agents 如何加载上下文，检查 agent 文件本身。

### 3. 主会话 Workflow（Main-Session Workflow）

有些平台没有 Trellis sub-agent 或 hook 能力。它们依赖 workflows/skills/commands 引导主会话 AI 读文件、跑脚本、推进任务。

要改行为，检查平台 workflows/skills/commands 与 `.trellis/workflow.md`。

## 本地修改顺序（Local Modification Order）

用户要求为某平台定制行为时，AI 应按此顺序检查文件：

1. 读 `.trellis/workflow.md`，确认共享流程。
2. 读目标平台 settings/config，看注册了哪些 hooks/agents/skills/commands。
3. 读目标平台的 agents/skills/commands/hooks。
4. 修改最贴近用户需求的本地文件。
5. 若变更影响共享流程，同步 `.trellis/workflow.md` 或 `.trellis/spec/`。

不要只改平台文件却忘了共享 workflow。不要只改 `.trellis/workflow.md` 却忘了平台入口可能仍有旧描述。
