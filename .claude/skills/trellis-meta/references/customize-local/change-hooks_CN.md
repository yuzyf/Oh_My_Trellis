<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/customize-local/change-hooks.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 修改本地 Hooks（Change Local Hooks）

Hooks 是连接平台与 Trellis 的自动化层。当用户想改「何时注入上下文」「shell 命令如何继承 session」或「agent 启动前读哪些文件」时，通常改 hooks。

## 先读这些文件（Read These Files First）

1. 目标平台 settings/config，例如 `.claude/settings.json`、`.codex/hooks.json`、`.cursor/hooks.json`
2. 目标平台 hooks 目录
3. `.trellis/scripts/common/active_task.py`
4. `.trellis/scripts/common/session_context.py`
5. `.trellis/workflow.md`

## 常见 Hook 类型（Common Hook Types）

| Hook | Purpose |
| --- | --- |
| session-start | 在 session 开始、清空或 compact 时注入 Trellis 总览。 |
| workflow-state | 在每次用户输入时注入状态提示。 |
| sub-agent context | 在 agent 启动前注入 PRD/spec/research。 |
| shell session bridge | 让 shell 中的 `task.py` 命令看到同一 session 身份。 |

## 修改步骤（Modification Steps）

1. 在 settings/config 中找到 hook 注册。
2. 确认注册的脚本路径存在。
3. 读 hook 脚本，识别输入、输出与调用的 `.trellis/scripts/`。
4. 修改 hook 行为。
5. 若 hook 依赖 workflow 内容，同步 `.trellis/workflow.md`。

## 示例：改新会话注入内容（Example: Change New-Session Injection Content）

先找 session-start hook：

```text
.claude/settings.json
.claude/hooks/session-start.py
```

若 hook 最终调用 `.trellis/scripts/get_context.py` 或 `session_context.py`，改本地脚本通常比在 hook 里硬编码更稳。

## 示例：Agent 没读 JSONL（Example: Agent Did Not Read JSONL）

先确认：

```bash
python3 ./.trellis/scripts/task.py current --source
python3 ./.trellis/scripts/task.py validate <task>
```

若 task 与 JSONL 都正确，再判断平台是 hook push 还是 agent pull。hook push 改 `inject-subagent-context`；agent pull 改 agent 文件。

## 注意（Notes）

- Settings 管注册，hook 脚本管行为；两者一起看。
- 平台 hook 路径各不相同；以项目中真实 settings 为准。
- 不要只改一处平台 hook 却期望所有平台自动一致。
