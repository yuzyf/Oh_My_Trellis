> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.claude/skills/trellis-session-insight/references/cli-quick-reference.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

# `trellis mem` CLI 参考

五个子命令的完整 flag 参考。以此为权威源——运行时 `trellis mem help` 打印相同内容，因此这里若与运行时漂移就是 bug。

## 子命令

| 命令 | 用途 |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `list`                 | 列出会话。未指定子命令时的默认。                                                                  |
| `search <keyword>`     | 找内容匹配关键词的会话。                                                                          |
| `context <session-id>` | 钻进单一会话：top-N 命中轮次 + 周边上下文。可配 `--grep` 锚定关键词。               |
| `extract <session-id>` | 导出清洗后的对话。可与 `--phase` / `--grep` 组合切片。                                                     |
| `projects`             | 列出活跃项目 `cwd` 与会话数。用来发现应传给其他子命令的 `--cwd`。 |

## Flags（在有意义的子命令上生效）

| Flag                                          | 子命令       | 含义                                                                                                                                                    |
| --------------------------------------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--platform claude\|codex\|opencode\|pi\|all` | all               | 默认 `all`。OpenCode adapter 在 `0.6.0-beta.*` 上目前是 stub——见下方 "Caveats"。                                                               |
| `--since YYYY-MM-DD`                          | list / search     | 含下界的日期。                                                                                                                                |
| `--until YYYY-MM-DD`                          | list / search     | 含上界的日期。                                                                                                                                |
| `--global`                                    | list / search     | 包含本机所有项目的会话。默认是当前项目 `cwd`。                                                                                      |
| `--cwd <path>`                                | list / search     | 强制指定项目 cwd，而不是从当前位置推断。                                                                                      |
| `--limit N`                                   | list / search     | 限制输出行数。默认 `50`。                                                                                                                             |
| `--grep KW`                                   | extract / context | 按关键词过滤轮次。空白分隔时为多 token AND。                                                                                        |
| `--phase brainstorm\|implement\|all`          | extract           | 按 Trellis 任务边界切片会话。`brainstorm` = `[task.py create, task.py start)`。`implement` = brainstorm 窗口外的轮次。默认 `all`。 |
| `--turns N`                                   | context           | 返回的命中轮次数。默认 `3`。                                                                                                                |
| `--around N`                                  | context           | 每个命中包含的周边轮次数。默认 `1`。                                                                                                         |
| `--max-chars N`                               | context / extract | 限制输出字符数，避免刷屏。                                                                                                          |

## 常见配方

```bash
# 本项目最近会话
trellis mem list --limit 20

# 关键词搜索（本项目）
trellis mem search "channel worker"

# 跨本机所有项目
trellis mem search "OOM" --global

# 某时间窗
trellis mem list --since 2026-03-01 --until 2026-03-31

# 深挖并锚定关键词
trellis mem context <session-id> --grep "race" --turns 5 --around 2

# 只导出规划阶段
trellis mem extract <session-id> --phase brainstorm

# 导出实现阶段中匹配关键词的轮次
trellis mem extract <session-id> --phase implement --grep "failing test"
```

## Caveats

- OpenCode：provider adapter 在当前 beta 线上可能是 stub；若用户明确指 OpenCode 历史，说明限制。
- 会话 ID 格式随平台变化；以 `list` / `search` 输出的 ID 为准再传给 `context` / `extract`。
- Phase 切片依赖 Trellis 任务边界事件；没有 `task.py create` / `start` 的会话把 `--phase` 当 no-op 或退回全量。
