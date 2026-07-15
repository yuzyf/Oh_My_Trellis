> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.claude/skills/trellis-spec-bootstrap/references/spec-task-planning.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

# Spec 任务规划（Spec Task Planning）

默认用单 agent 执行模型。agent 可为可追溯性创建 Trellis 任务，但 skill 不应绑定特定平台、CLI 或并行 worker 模型。

## 分解（Decomposition）

围绕真实所有权边界创建 spec 工作单元：

- 当包有自己的约定时，按包拆。
- 当同一包有不同的 frontend、backend、CLI、worker 或共享库规则时，按层拆。
- 当模式跨包且不归一层所有时，做一个横切 guide。

避免人为过度拆分。小库通常需要一次聚焦的 spec pass，而不是多个任务。

## 任务形状（Task Shape）

当 Trellis 任务有用时，写简洁 PRD，包含这些节：

```markdown
# Fill <package-or-layer> Trellis Specs

## Goal
Write project-specific `.trellis/spec/` guidance for <scope>.

## Scope
- Spec directory:
- Source directories to inspect:
- Tests to inspect:
- Out of scope:

## Architecture Context
Summarize the concrete findings from repository analysis.

## Files To Create Or Update
- `.trellis/spec/.../index.md`
- `.trellis/spec/.../<topic>.md`

## Rules
- Adapt the spec file set to the real codebase.
- Use real source examples with file paths.
- Remove template-only sections that do not apply.
- Do not modify product source code unless the task explicitly asks for it.

## Acceptance Criteria
- [ ] Specs contain concrete examples and anti-patterns from the repository.
- [ ] No placeholder text remains.
- [ ] Index files match the final spec files.
- [ ] Claims are backed by source files, tests, or project docs.
```

## 可选 Helper Agents

若宿主支持 subagents，helper 可检查独立包或跑校验。它们是可选的。主 agent 仍拥有集成与最终质量。

Helper 任务必须有清晰所有权：

- 只读 research 任务可检查分配范围内所需的任何源码。
- 写任务应拥有互不重叠的 spec 目录。
- 校验任务应检查占位去除、坏链与一致性。

不要在 skill 里编码 helper-agent 名、厂商专用命令或平台专用路由。任务里只放必需工作与验收标准。
