<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/customize-local/change-workflow.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 修改本地 Workflow（Change Local Workflow）

当用户想改 Trellis 阶段、下一步提示、是否建任务、是否用 sub-agents，或何时 check/wrap up 时，先编辑 `.trellis/workflow.md`。

## 先读这些文件（Read These Files First）

1. `.trellis/workflow.md`
2. 当前平台的入口文件，例如 skills/commands/prompts/workflows
3. 当前任务的 `task.json` 与 `prd.md`

## 常见需求与修改点（Common Needs And Edit Points）

| Need | Edit point |
| --- | --- |
| 改阶段名称或顺序 | `Phase Index` 与对应 Phase 小节。 |
| 改无任务时是否建任务 | `[workflow-state:no_task]` 状态块。 |
| 改 planning 期间下一步 | Phase 1 与 `[workflow-state:planning]`。 |
| 改 in_progress 是否要求 agent | Phase 2 与 `[workflow-state:in_progress]`。 |
| 改完成后的收尾 | Phase 3 与 `[workflow-state:completed]`。 |
| 改用户意图触发哪个 skill | `Skill Routing` 表。 |

## 修改步骤（Modification Steps）

1. 在 `.trellis/workflow.md` 中找到相关段落。
2. 改规则时保持触发条件与下一步动作明确。
3. 若新增或重命名 skill/agent，同步平台目录中的对应文件。
4. workflow-state 变更只需改 `.trellis/workflow.md` 中的 `[workflow-state:STATUS]` 块。Hook 只做解析——它读取你放进块里的内容。保持开闭标签 STATUS 字符串一致（`[workflow-state:foo]…[/workflow-state:foo]`）；STATUS 不一致会被静默丢弃。
5. 让 AI 重新读 `.trellis/workflow.md`；不要继续沿用旧对话中的规则。

## 示例：放宽建任务要求（Example: Relax Task Creation Requirements）

要改何时可跳过建任务，通常编辑 `[workflow-state:no_task]`：

```md
[workflow-state:no_task]
Task is not required when the answer is a one-reply explanation, no files are changed, and no research is needed.
[/workflow-state:no_task]
```

若正式 Phase 1 流程也要变，同步 Phase 1 小节。

## 示例：某一平台不用 Sub-Agents（Example: One Platform Does Not Use Sub-Agents）

若用户只希望某一平台不用 sub-agents，先确认 workflow 里该平台是否有独立分组。然后改该平台组的 Phase 2 路由，而不是跨平台删掉所有 `trellis-implement` / `trellis-check` 说明。

## `/trellis:continue` 路由表（Route Table）

`/trellis:continue` 通过 `task.json.status` 与任务目录内 artifact 是否存在，决定下一步加载哪个阶段步骤。映射固定在命令本身；增加自定义 status 的 fork 必须同时扩展 workflow.md 标签块与此表。

| `status` | Artifact state | Resume at |
| --- | --- | --- |
| `planning` | 缺少 `prd.md` | Phase 1.1（加载 `trellis-brainstorm`） |
| `planning` | 轻量任务且 `prd.md` 完成 | 请求 start review，然后运行 `task.py start` |
| `planning` | 复杂任务缺少 `design.md` 或 `implement.md` | 补齐缺失的 planning artifacts |
| `planning` | 复杂任务已有 `prd.md`、`design.md`、`implement.md` | 请求 start review，然后运行 `task.py start` |
| `in_progress` | 对话历史中尚无实现 | Phase 2.1（`trellis-implement`） |
| `in_progress` | 实现完成，尚未跑 `trellis-check` | Phase 2.2（`trellis-check`） |
| `in_progress` | check 通过 | Phase 3.3（spec update）→ 3.4（commit） |
| `completed` | 任务仍在活跃树中 | Phase 3.5（运行 `/trellis:finish-work` 归档） |

当你新增自定义 status（例如 `in-review`）时，在 `.trellis/workflow.md` 增加 `[workflow-state:in-review]` 块作为每轮面包屑，并扩展本路由表——通常通过编辑 `/trellis:continue` 命令文件（`.{platform}/commands/trellis/continue.md` 或等价路径）增加一行决定从何处恢复。没有路由条目时，`/trellis:continue` 会落到默认分支，用户到不了你期望的步骤。

## 注意（Notes）

`.trellis/workflow.md` 是本地项目 workflow，不是不可变模板。用户可按团队习惯改编。改完后平台入口文件可能仍有旧描述，也要一并检查。
