<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/customize-local/change-task-lifecycle.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 修改本地任务生命周期（Change Local Task Lifecycle）

任务生命周期包括创建、start、上下文配置、finish、archive、父子任务与生命周期 hooks。默认定制目标是 `.trellis/tasks/`、`.trellis/config.yaml` 与 `.trellis/scripts/`。

## 先读这些文件（Read These Files First）

1. `.trellis/workflow.md`
2. `.trellis/config.yaml`
3. `.trellis/scripts/task.py`
4. `.trellis/scripts/common/task_store.py`
5. `.trellis/scripts/common/task_utils.py`
6. 当前任务的 `.trellis/tasks/<task>/task.json`

## 常见需求与修改点（Common Needs And Edit Points）

| Need | Edit point |
| --- | --- |
| 建任务后自动同步外部系统 | `.trellis/config.yaml` 的 `hooks.after_create`。 |
| start 后自动更新状态 | `.trellis/config.yaml` 的 `hooks.after_start`。 |
| finish 后运行脚本 | `.trellis/config.yaml` 的 `hooks.after_finish`。 |
| archive 后清理外部资源 | `.trellis/config.yaml` 的 `hooks.after_archive`。 |
| 改默认任务字段 | `.trellis/scripts/common/task_store.py`。 |
| 改任务解析/搜索 | `.trellis/scripts/common/task_utils.py`。 |
| 改活跃任务行为 | `.trellis/scripts/common/active_task.py`。 |

## lifecycle hooks

`.trellis/config.yaml` 支持：

```yaml
hooks:
  after_create:
    - "python3 .trellis/scripts/hooks/my_sync.py create"
  after_start:
    - "python3 .trellis/scripts/hooks/my_sync.py start"
  after_finish:
    - "python3 .trellis/scripts/hooks/my_sync.py finish"
  after_archive:
    - "python3 .trellis/scripts/hooks/my_sync.py archive"
```

Hook 命令会收到 `TASK_JSON_PATH` 环境变量，指向当前任务的 `task.json`。Hook 失败通常应告警，但不阻塞主任务操作。

## 修改任务字段（Change Task Fields）

若用户要增加项目本地字段，优先放在 `task.json` 的 `meta` 下，避免破坏现有脚本对标准字段的假设。

示例：

```json
"meta": {
  "linearIssue": "ENG-123",
  "risk": "high"
}
```

若真要改标准字段，检查所有读取 `task.json` 的本地脚本。

## 修改活跃任务（Change Active Task）

活跃任务是存在 `.trellis/.runtime/sessions/` 的 session 级状态。不要退回全局 `.current-task` 模型。若用户要改活跃任务行为，编辑：

- `.trellis/scripts/common/active_task.py`
- 平台 hooks 或 shell session bridges
- `.trellis/workflow.md` 中对活跃任务的描述

### `task.py create` 会设置活跃指针（Sets the Active Pointer）

`.trellis/scripts/common/task_store.py` 中的 `cmd_create` 在写入新任务目录后会 best-effort 调用 `set_active_task`。行为如下：

- 当调用 shell 携带 session 身份（`TRELLIS_CONTEXT_ID` 环境变量，或任何 `resolve_context_key` 能识别的平台 session 环境——见 `active_task.py:_ENV_SESSION_KEYS`）时，会重写 `.trellis/.runtime/sessions/<context_key>.json` 中的 per-session 指针，指向新任务。任务 `status=planning`，且下一次 `UserPromptSubmit` 就会触发 `[workflow-state:planning]`。
- 当 session 身份不可用（AI session 外的裸 CLI 调用，或平台不把身份传播到 shell）时，任务目录仍会创建且 `status=planning` 仍会写入，但活跃指针不动。用户回到 AI session 后可用 `task.py start <dir>` 再挂接任务。

这让 `[workflow-state:planning]` 在 `task.py create` 之后的 brainstorm 与 JSONL 整理期间成为有效面包屑。R7 之前的行为会把面包屑卡在 `no_task` 直到 `task.py start`，planning 块实际是死文。

若你 fork `task.py` 增加新的创建路径（例如绕过 `cmd_create` 的外部导入），审计该路径是否也调用了 `set_active_task`。没有该调用，创建出的任务不会成为活跃任务。完整 status writer 表见 `.trellis/spec/cli/backend/workflow-state-contract.md`。

## 修改步骤（Modification Steps）

1. 用 `python3 ./.trellis/scripts/task.py current --source` 确认当前任务。
2. 读当前任务的 `task.json`，确认 status 与字段。
3. 配置类需求先改 `.trellis/config.yaml`。
4. 脚本行为类需求再改 `.trellis/scripts/`。
5. 若 AI 流程变了，同步 `.trellis/workflow.md`。

## 不要（Do Not）

- 不要直接改 `.trellis/.runtime/sessions/` 来“修”业务状态。
- 不要把项目私有字段硬编码进脚本；优先用 `meta`。
- 不要默认要求用户 fork Trellis CLI。
