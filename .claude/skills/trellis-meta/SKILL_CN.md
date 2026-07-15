<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/SKILL.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

---
name: trellis-meta
description: "理解并定制用户项目内的本地 Trellis 架构。在修改 .trellis 以及平台 hooks、settings、agents、skills、commands、prompts、workflows、channel 运行时（trellis channel）、.trellis/agents/ 下的捆绑 runtime agents、可选 workflow 模板、基于 registry 的 spec 刷新、trellis init 生成的跨会话记忆（trellis mem），或 AI 面向的捆绑 skills（trellis-channel、trellis-session-insight、trellis-spec-bootstrap）以及捆绑 skill 自动分发流程时使用。"
---

# Trellis Meta

本 skill 面向已经在项目里跑过 `trellis init` 的本地 Trellis 用户。读完后，AI 应能理解该用户项目内的 Trellis 架构、运行模型与定制入口，再按用户请求去改生成的 `.trellis/` 与平台目录文件。

Trellis v0.6 在 pre-v0.6 的 workflow / persistence / platform 模型之上，新增了三块架构面（architectural surfaces）。第一，多智能体协作运行时（multi-agent collaboration runtime）：`trellis channel` 通过项目作用域的 JSONL 事件日志 `~/.trellis/channels/<project>/<channel>/events.jsonl` 协调多个 AI worker 进程，含 worker OOM guard、forum/thread 频道、持久幂等键（idempotency keys），以及捆绑的 `.trellis/agents/{check,implement}.md` 运行时定义。第二，跨会话记忆（cross-session memory）：`trellis mem list | search | context | extract | projects` 读取本机已有的 Claude Code、Codex、Pi Agent JSONL，可用 `--phase brainstorm|implement|all` 切片，且永不上传。第三，双包 npm 发布：`@mindfoldhq/trellis`（CLI）与 `@mindfoldhq/trellis-core`（带 `/channel`、`/task`、`/mem`、`/testing` 子路径的 SDK）同版本锁步发布。应把它们与各平台集成文件一并视为一等定制面。

默认操作范围是用户项目中的本地文件：

- `.trellis/`：workflow、config、tasks、spec、workspace、scripts、捆绑 runtime agents，以及 runtime 状态。
- 平台目录：`.claude/`、`.codex/`、`.cursor/`、`.opencode/`、`.kiro/`、`.gemini/`、`.qoder/`、`.codebuddy/`、`.github/`、`.factory/`、`.pi/`、`.reasonix/`、`.kilocode/`、`.agent/`、`.devin/` 及类似目录。Pi 在文件布局之上还暴露原生 `trellis_subagent` 工具，支持 `single` / `parallel` / `chain` 分发模式、节流进度卡，以及 `isTrellisAgent()` 校验。Reasonix 把 workflow skills 与 subagent skills 都存成 `.reasonix/skills/<name>/SKILL.md`；subagent skills 带 `runAs: subagent` frontmatter。
- 共享 skill 层：`.agents/skills/`。
- 项目树外的用户自有 channel 存储：`~/.trellis/channels/<project>/<channel>/events.jsonl`。
- 可通过 `trellis mem` 查询的原始平台会话日志：`~/.claude/projects/`、`~/.codex/sessions/`、`~/.pi/agent/sessions/`（OpenCode 适配器在 v0.6 线为降级状态）。

不要假设用户拥有 Trellis 源码仓库。不要默认去改全局 npm 安装目录或 `node_modules`——`@mindfoldhq/trellis` 与 `@mindfoldhq/trellis-core` 都是以已发布包形态交付，每次发布共享一个版本与一个 git tag。

## 如何使用（How To Use）

1. 先读 `references/local-architecture/overview.md`，建立本地 Trellis 系统模型。
2. 若请求涉及特定 AI 工具，读 `references/platform-files/platform-map.md` 以及对应平台文件说明。
3. 若涉及多智能体分发或 channel workers，读 `references/local-architecture/multi-agent-channel.md` 与捆绑的 `.trellis/agents/` 文件。
4. 若用户要改行为，读 `references/customize-local/overview.md`，再打开具体定制主题。
5. 动手改之前，先读用户项目里的真实文件，以本地内容为准。

## 参考（References）

### Local Architecture

- `references/local-architecture/overview.md`：分层本地 Trellis 架构（workflow / persistence / platform / channel runtime）与定制原则。
- `references/local-architecture/generated-files.md`：`trellis init` 生成的文件及其定制边界，含 `.trellis/agents/`。
- `references/local-architecture/workflow.md`：阶段、路由、workflow-state 块，以及 `.trellis/workflow.md` 中可选 workflow 模板（`native`、`tdd`、`channel-driven-subagent-dispatch`、marketplace）。
- `references/local-architecture/task-system.md`：任务目录、active task、JSONL context、父子任务树与 task runtime。
- `references/local-architecture/spec-system.md`：`.trellis/spec/` 如何组织、注入，以及从 `registry.spec` 源刷新。
- `references/local-architecture/workspace-memory.md`：`.trellis/workspace/` journals，以及 `trellis mem` 跨会话回忆与任务切片。
- `references/local-architecture/context-injection.md`：编码规范与上下文如何注入会话。
- `references/local-architecture/multi-agent-channel.md`：`trellis channel` 运行时、worker 生命周期、forum/thread、幂等与 OOM guard。
- `references/local-architecture/bundled-skills.md`：捆绑多文件 skills 的布局、自动分发与边界。

### Platform Files

- `references/platform-files/overview.md`：平台集成文件总览。
- `references/platform-files/platform-map.md`：各 AI 工具平台目录与文件地图。
- `references/platform-files/hooks-and-settings.md`：hooks 与 settings/config 如何决定实际运行什么。
- `references/platform-files/agents.md`：平台 agents / subagents 与 `.trellis/agents/` 的关系。
- `references/platform-files/skills-and-commands.md`：平台 skills、commands 与共享 `.agents/skills/`。

### Customize Local

- `references/customize-local/overview.md`：本地定制总览与入口选择。
- `references/customize-local/change-workflow.md`：改 workflow 阶段、路由与模板选择。
- `references/customize-local/change-hooks.md`：改 lifecycle hooks 与平台 hook 接线。
- `references/customize-local/change-agents.md`：改 channel runtime agents 与平台 sub-agents。
- `references/customize-local/change-skills-or-commands.md`：改 skills/commands，以及上游捆绑 skill 自动分发。
- `references/customize-local/change-spec-structure.md`：调整 `.trellis/spec/` 项目规范结构，含 registry 源。
- `references/customize-local/change-task-lifecycle.md`：改任务生命周期与 JSONL/context 行为。
- `references/customize-local/change-context-loading.md`：改上下文加载与注入路径。
- `references/customize-local/add-project-local-conventions.md`：把团队规则放进项目本地 specs 或 local skills。

### How To Modify

- `references/how-to-modify/overview.md`：改动操作手册总入口。
- `references/how-to-modify/add-agent.md`：新增 agent。
- `references/how-to-modify/add-command.md`：新增 command。
- `references/how-to-modify/add-phase.md`：新增 workflow phase。
- `references/how-to-modify/add-spec.md`：新增 spec。
- `references/how-to-modify/change-verify.md`：改校验/verify 流程。
- `references/how-to-modify/modify-hook.md`：改 hook。

### Claude Code / Core / Meta

- `references/claude-code/*`：Claude Code 专用深度（agents、hooks、multi-session、ralph-loop、scripts、worktree-config）。
- `references/core/*`：跨平台核心系统（files、workspace、tasks、specs、scripts）。
- `references/meta/*`：平台兼容、自迭代指南、trellis-local 模板。

## 当前规则（Current Rules）

- `.trellis/workflow.md` 是本地 workflow 的权威源；初始内容在 `trellis init` 时从 workflow 模板选出（内置 `native`、`tdd`、`channel-driven-subagent-dispatch`，或 marketplace 模板），也可通过 `trellis workflow --template <id>` 重选。当前模板引用但缺失的 `.trellis/agents/<name>.md` 会触发非阻塞 stderr 警告，并指向 `trellis update`。
- `.trellis/config.yaml` 是项目级 Trellis 配置入口。它承载任务生命周期 hooks（`hooks.after_create` / `after_start` / `after_finish` / `after_archive`）、journal 形态（`session_commit_message` / `max_journal_lines` / `session_auto_commit`）、channel worker guard（`channel.worker_guard.idle_timeout` / `max_live_workers`）、Codex 分发模式（`codex.dispatch_mode: inline | sub-agent`），以及 spec registry 块（`registry.spec.source` + `registry.spec.template`）。
- `.trellis/spec/` 存放用户项目专属编码约定与设计约束。当设置了 `registry.spec` 时，文件由 `trellis update` 刷新；本地修改会在 `.trellis/.template-hashes.json` 中以 “modified by user” 冲突呈现。
- `.trellis/tasks/` 存放任务 PRD、设计笔记、implement 计划、research 文件与 JSONL context。任务形成父子树：`task.py create --parent <slug>`、`task.py add-subtask <parent> <child>`、`task.py remove-subtask <parent> <child>`、`task.py list-context <task>`。`task.py create` 会拒绝已出现在 `.trellis/tasks/archive/**` 中的 slug。
- `.trellis/workspace/` 存放**刻意写下来的**开发者 journals。原始跨会话对话**不**存在这里——它们在本机 `~/.claude/projects/`、`~/.codex/sessions/`、`~/.pi/agent/sessions/`，通过 `trellis mem search|extract|context` 恢复。捆绑的 `trellis-session-insight` skill 教你何时该用 `mem`。
- `.trellis/agents/{check,implement}.md` 是捆绑的、平台无关的 channel runtime agent 定义，由 `trellis channel spawn --agent <name>` 加载。可编辑；`trellis update` 会回填缺失项。改各平台的 `trellis-implement.md` / `trellis-check.md` **不会**改变 channel-runtime worker 行为。
- `~/.trellis/channels/<project>/<channel>/events.jsonl` 是按项目、按频道的 channel runtime 事件日志。用户自有，文件锁序号，支持持久 `idempotencyKey`；永不放在 `.trellis/` 下。
- 捆绑多文件 skills（`trellis-meta`、`trellis-spec-bootstrap`、`trellis-session-insight`、`trellis-channel`）由 `packages/cli/src/templates/common/index.ts` 中的 `getBundledSkillTemplates()` 自动分发到每个平台 skill 根。在上游 `packages/cli/src/templates/common/bundled-skills/` 下新增目录，会在下次 `trellis update` 时下发到所有平台。
- 平台 settings/config 文件决定实际会跑哪些 hooks、agents、skills、commands、prompts 与 workflows。Reasonix 没有 settings 文件——行为编码在 skill frontmatter 里。
- `.trellis/.template-hashes.json` 与 `.trellis/.runtime/` 是管理/运行时状态文件。改之前先确认必要性。

## 不要做（Do Not）

- 不要把 Trellis 上游源码当作本地定制的默认目标。
- 不要为了满足项目需求去改全局 npm 安装目录，或 `node_modules/@mindfoldhq/trellis` / `node_modules/@mindfoldhq/trellis-core`；两包锁步发布。
- 不要用默认模板覆盖用户已改的本地文件；先查 `.trellis/.template-hashes.json`，优先 `.new` sidecar，而不是破坏性覆盖。
- 不要把团队私有项目规则塞进任何公共捆绑 skill（`trellis-meta`、`trellis-spec-bootstrap`、`trellis-session-insight`、`trellis-channel`）；项目规则应放在 `.trellis/spec/`、项目本地 skill、当前任务或 workspace journal——`trellis update` 会覆盖捆绑 skill 目录内的任何内容。
- 不要手改 `~/.trellis/channels/<project>/<channel>/events.jsonl`；序号在文件锁下分配，可重放安全写入应走 `trellis channel` CLI 或 `@mindfoldhq/trellis-core/channel` SDK。
- 若目标是改 channel runtime worker 行为，不要去改 `.claude/agents/trellis-implement.md`（或任何其他平台 sub-agent 文件）——应改 `.trellis/agents/<name>.md`。
- 不要把已移除或从未交付的机制描述成当前 Trellis 行为；在声称某个旋钮存在之前，先对照本地 `.trellis/config.yaml` 与已安装 CLI 的 `trellis --help`。
