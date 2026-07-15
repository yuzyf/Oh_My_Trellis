<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-channel/references/forum.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# Forum 频道（Forum Channels）

Forum 频道是持久、主题式频道。创建时用 `--type forum`，之后不可变。它们不是普通聊天流：默认读取路径是 **forum 摘要 → 单条 thread 时间线 → 当前 context**。

## Forum vs 普通 Channel

频道类型由 `channel create` 的 `--type` 设定且永不改变：

- `chat`（默认）— 扁平消息时间线。`channel messages` 始终渲染事件流。forum 专用 flags（如 `--thread`、`--action`）在此被拒绝。
- `forum` — 面向 thread。无过滤时 `channel messages` 渲染 thread-board 摘要而非原始事件。`post`、`forum`、`thread`、`thread rename` 仅适用于 forum 频道。

两种类型共享同一 scope 模型（`--scope project` 默认；`--scope global` 放入跨项目 bucket）。

## 创建 Forum 频道

```bash
trellis channel create design-feedback \
  --type forum \
  --scope global \
  --description "Cross-project design feedback board." \
  --context-raw "One thread per design topic; close when resolved." \
  --by main
```

单仓库 board 用 `--scope project`；跨项目 board 用 `--scope global`。

## Threads：Open、Comment、Status、Summary

Thread 住在 forum 频道内。每条 thread 用稳定 `--thread <key>` 标识（惯例小写 kebab-case）。对 thread 的第一个动作是 `opened`；之后都用同一 `--thread` key。

```bash
trellis channel post design-feedback opened \
  --scope global \
  --as main \
  --thread login-empty-state \
  --title "Empty state on the login screen" \
  --description "Track design feedback for the new login empty state." \
  --labels design,login \
  --context-raw "Spotted during the 0.4 release review." \
  --text-file /tmp/thread-open.md

trellis channel post design-feedback comment \
  --scope global \
  --as reviewer \
  --thread login-empty-state \
  --text-file /tmp/review.md

trellis channel post design-feedback status \
  --scope global \
  --as main \
  --thread login-empty-state \
  --status closed

trellis channel post design-feedback summary \
  --scope global \
  --as main \
  --thread login-empty-state \
  --summary "Adopted the option-B layout; ticket TRELLIS-123 owns the fix."
```

关键区分：

- `--description` 是 **持久** thread 描述（回答「这条 thread 关于什么？」）。在 `opened` 设定，再跑带 `--description` 的 `post` 可编辑。
- `--text` / `--stdin` / `--text-file` 是 **事件正文** — 附着在该时间线条目上的评论或载荷。
- `--labels` 与 `--assignees` 是 CSV 且 **替换** 当前值；不追加。
- `--summary` 是滚动 thread 摘要。在 `status closed` 时设置是带上下文标记解决的标准方式。

除实践上 `opened` 也需要外，每个动作都要求 `--thread`——没有匿名 thread。

## 读取 Forum

```bash
trellis channel messages design-feedback --scope global
trellis channel forum design-feedback --scope global --status open
trellis channel thread design-feedback login-empty-state --scope global
trellis channel messages design-feedback --scope global --raw --thread login-empty-state
```

若对端说「我在 forum 上评论了」，先跑 `channel forum` 看哪条 thread 变了，再 `channel thread <name> <thread>` 下钻。不要直接去 ad-hoc 解析 `events.jsonl`。

## Context（上下文）

Context 条目是读 channel 或 thread 时始终应在作用域内的持久背景。它们 **不是** 时间线事件；单独投影，对每位读者回放。

使用 `context` 子命令。`create` / `post` 上遗留的 `--linked-context-file` / `--linked-context-raw` 是废弃别名，并入规范的 `--context-file` / `--context-raw`。

### 添加 Context

```bash
# Channel-level context (whole forum)
trellis channel context add design-feedback \
  --scope global \
  --raw "Upstream feedback board; please link tasks before opening threads."

# Thread-level context (one thread)
trellis channel context add design-feedback \
  --scope global \
  --thread login-empty-state \
  --file "$PWD/.trellis/tasks/05-13-login-redesign/design.md"
```

- `--thread <key>` 在 channel 级与 thread 级 context 间切换。
- `--file` 路径 **必须绝对路径**；相对路径被拒绝。
- `--raw` 是内联纯文本。
- 两 flag 都可重复；`add` / `delete` 至少一个。
- `--as <agent>` 记录作者；默认 `main`。

### 列出 Context

```bash
trellis channel context list design-feedback --scope global
trellis channel context list design-feedback --scope global --thread login-empty-state --raw
```

`list` 上的 `--raw` 每行输出一条 JSON（便于脚本）。pretty 输出是 `file <path>` / `raw <truncated text>` 行；空时 `(no context)`。

### 删除 Context

```bash
trellis channel context delete design-feedback \
  --scope global \
  --thread login-empty-state \
  --file "$PWD/.trellis/tasks/05-13-login-redesign/design.md"
```

`delete` 按内容匹配移除；必须精确匹配先前列出的 file 路径或 raw 文本。

## Title

```bash
trellis channel title set design-feedback --title "Design Feedback Board" --scope global
trellis channel title clear design-feedback --scope global
```

Title 是频道的稳定显示名（与频道 id/目录名不同）。

## Thread 重命名

```bash
trellis channel thread rename design-feedback login-empty-state login-empty-v2 \
  --as main --scope global
```

`post --action rename` 被拒绝——唯一变更路径是 `thread rename`。

## Changelog / Issue Board 约定

- 每条 issue / 主题 = 一条 thread。
- 开 thread 时写清 description + 首条 body。
- 相关设计/任务文件挂到 thread-level context（绝对路径）。
- 关闭时写 summary（做了什么、谁跟进、链接工单）。
- 跨项目反馈用 `--scope global`；单仓库实现跟踪用 project scope。

## 不要做的事

- 不要手写解析 `events.jsonl` 当主读路径。
- 不要用 chat 频道冒充 issue board（缺 thread 语义）。
- 不要把长正文塞位置参数；用 `--text-file` / `--stdin`。
- 不要把 context 当聊天消息发送——用 `context add`。
