<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/customize-local/overview.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 本地定制总览（Local Customization Overview）

本目录面向已在用户项目中通过 npm 安装 Trellis 并完成 `trellis init` 的本地 AI。AI 应修改项目内生成的 `.trellis/` 与平台目录，而不是 Trellis CLI 上游源码。

## 先判断用户真正想改什么（First Determine What The User Actually Wants To Change）

| 用户说法 | 先读 |
| --- | --- |
| "Change the Trellis flow / phases / next prompt" | `change-workflow.md` |
| "Change task creation, status, archive, or hooks" | `change-task-lifecycle.md` |
| "AI did not read context / change injected content" | `change-context-loading.md` |
| "A platform hook is not behaving as expected" | `change-hooks.md` |
| "Change implement/check/research agent behavior" | `change-agents.md` |
| "Add a skill/command/workflow/prompt" | `change-skills-or-commands.md` |
| "Adjust the project spec structure" | `change-spec-structure.md` |
| "Add team conventions and local notes" | `add-project-local-conventions.md` |

## 通用操作顺序（General Operation Order）

1. **确认平台与目录**：检查实际存在的目录，例如 `.claude/`、`.codex/`、`.cursor/`、`.zcode/`。
2. **确认当前活跃任务**：运行 `python3 ./.trellis/scripts/task.py current --source`。
3. **读本地真相源**：优先 `.trellis/workflow.md`、`.trellis/config.yaml` 与相关平台文件。
4. **窄范围修改**：只改与用户请求相关的文件。
5. **语义同步**：若共享流程变了，检查平台入口是否也要改；若平台入口变了，检查 `.trellis/workflow.md` 是否仍一致。

## 本地文件优先级（Local File Priority）

| Layer | Files |
| --- | --- |
| Workflow | `.trellis/workflow.md` |
| Project configuration | `.trellis/config.yaml` |
| Task material | `.trellis/tasks/<task>/` |
| Project specs | `.trellis/spec/` |
| Runtime scripts | `.trellis/scripts/` |
| Platform integration | `.claude/`、`.codex/`、`.cursor/`、`.opencode/`、`.zcode/` 及类似目录 |
| Shared skill | `.agents/skills/` |

## 默认不要做的事（Things Not To Do By Default）

- 不要改全局 npm 安装目录。
- 不要改 `node_modules/@mindfoldhq/trellis`。
- 不要假设用户有 Trellis 的 GitHub 仓库。
- 不要用默认模板覆盖用户已改过的本地文件。
- 不要把团队项目规则写进公开的 `trellis-meta`；项目规则应放在 `.trellis/spec/` 或本地 skill。

## 何时查看上游源码（When To Inspect Upstream Source）

仅当用户明确表达以下目标之一时，才切换到上游源码视角：

- "I want to open a PR to Trellis"
- "I want to change npm package publish contents"
- "I want to fork Trellis"
- "I want to modify the generation logic for `trellis init/update`"

否则，默认修改用户项目内的本地 Trellis 文件。
