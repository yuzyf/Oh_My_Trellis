<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/local-architecture/overview.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 本地架构总览（Local Architecture Overview）

本地 Trellis 把工作流、持久化与平台集成连成用户项目内的可定制系统。

所有三层都在用户项目内，因此 AI 可直接读改。

## 核心路径（Core Paths）

| Path | Purpose |
| --- | --- |
| `.trellis/workflow.md` | Workflow phases, skill routing, and workflow-state prompt blocks. |
| `.trellis/config.yaml` | Project configuration, task lifecycle hooks, monorepo package configuration, and journal configuration. |
| `.trellis/spec/` | The user's project-specific coding conventions and thinking guides. |
| `.trellis/tasks/` | Each task's PRD, technical notes, research files, and JSONL context. |
| `.trellis/workspace/` | Per-developer journals and cross-session memory. |
| `.trellis/scripts/` | Local Python runtime used by commands, hooks, and context injection. |
| `.trellis/.runtime/` | Session-level runtime state, such as the current task pointer. |
| `.trellis/.template-hashes.json` | Template hashes for Trellis-managed files, used by update to determine whether local files were modified by the user. |

## AI 定制原则（AI Customization Principles）

1. **先找本地真源**：不要凭记忆改。先读 `.trellis/workflow.md`、`.trellis/config.yaml`、相关平台目录与任务文件。
2. **改用户项目，不改 npm 包缓存**：改项目内生成文件，不要改 `node_modules` 或全局 npm 安装目录。
3. **平台文件与 `.trellis/` 对齐**：若 workflow 路由变了，检查平台 skills/commands 是否仍描述同一流程。
4. **项目特有规则放 `.trellis/spec/` 或本地 skill**：不要把团队约定写进 `trellis-meta`。
5. **保留用户改动**：文件已本地修改时，从当前内容出发，不要用默认模板覆盖。

## 如何使用本目录（How To Use This Directory）

- 理解 init 后有哪些文件：读 `generated-files.md`。
- 改阶段、路由或下一步动作：读 `workflow.md`。
- 改任务模型、JSONL 上下文或 active task：读 `task-system.md`。
- 改编码约定注入：读 `spec-system.md`。
- 理解 journals 与跨会话记忆：读 `workspace-memory.md`。
- 改 hooks 或 sub-agent 上下文加载：读 `context-injection.md`。
