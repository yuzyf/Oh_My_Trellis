<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-channel/references/command-reference.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 命令参考（Command Reference）

`trellis channel` 子命令的权威现行参考，已对照源码
`packages/cli/src/commands/channel/`
（`index.ts` 的 Commander 接线与各子命令 handler）校验。

除非另有说明，每个子命令都接受 `--scope <project|global>`；默认 `project`，相对当前 cwd 的 project bucket 解析。

## 顶层（Top-level）

```
trellis channel <subcommand>
```

> 多智能体协作运行时——通过共享事件日志 spawn / 协调 / interrupt worker agents。

---

## 创建 / 列表（Create / List）

### `create <name>`

```bash
trellis channel create <name>
  [--scope project|global]                # default: project
  [--type chat|forum]                     # default: chat
  [--task <path>]                         # associated Trellis task dir
  [--project <slug>]
  [--labels a,b,c]
  [--description <text>]                  # stable channel description
  [--context-file <abs-path>] ...         # repeatable
  [--context-raw  <text>]      ...        # repeatable
  [--linked-context-file <abs-path>]      # [deprecated alias]
  [--linked-context-raw  <text>]          # [deprecated alias]
  [--cwd <path>]                          # recorded in create event
  [--by <agent>]                          # default: main
  [--force]                               # overwrite existing channel
  [--ephemeral]                           # hide from default list, prunable
```

行为：
- 追加一条 `create` 事件；`type` 不可变（创建后不能 forum↔chat 互改）。
- `--ephemeral` 频道默认从 `channel list` 隐藏，并成为 `channel prune --ephemeral` 的清扫目标。
- `--linked-context-*` 会折入 `--context-*`；使用时发出 deprecation 提示。

### `list`

```bash
trellis channel list
  [--scope project|global]
  [--json]
  [--project <slug>]                      # substring match on task field
  [--all]                                 # include ephemeral (suffix '*')
  [--all-projects]                        # scan every project bucket
```

行为：
- 默认 scope：当前 cwd 的 project。`--all-projects` 扫描每个 bucket。
- Pretty 模式打印 `NAME WORKERS EVENTS LAST KIND TYPE TASK`，按最近活动排序，页脚注明隐藏的 ephemeral 数量。
- `--json` 切到 JSON 数组。

---

## 聊天消息（Chat Messages）

### `send <name> [text]`

```bash
trellis channel send <name> [text]
  --as <agent>                            # REQUIRED — author
  [--scope project|global]
  [--to <agents,csv>]                     # default: broadcast
  [--stdin | --text-file <path>]          # body from stdin or file
  [--delivery-mode appendOnly|requireKnownWorker|requireRunningWorker]
```

行为：
- 正文优先级：位置参数 `[text]` → `--stdin` → `--text-file`。
- `--to` 单条目存字符串；多条目存数组；省略即广播。
- `--delivery-mode` 选择定向投递校验：
  - `appendOnly`（偏默认——只记录），
  - `requireKnownWorker`（命名目标必须有过 `spawned` 事件），
  - `requireRunningWorker`（worker 当前必须存活）。
- stdout 打印追加事件的一行 JSON。

> **注意：** `send` **没有** `--tag`，也 **没有** `--kind` flag。见下方 [`tag-vs-kind`](#tag-vs-kind--事件形状实际如何控制)。

### `messages <name>`

```bash
trellis channel messages <name>
  [--scope project|global]
  [--raw]                                 # one JSON event per line
  [--follow]                              # stream new events
  [--last <N>]                            # last N matching events
  [--since <seq>]                         # seq > N
  [--kind <kind>]                         # one of CHANNEL_EVENT_KINDS
  [--from <csv>]                          # author filter
  [--to <target>]                         # routing target filter
  [--thread <key>]                        # forum-only
  [--action <thread-action>]              # forum-only
  [--no-progress]                         # hide progress events
```

行为：
- 自动识别 forum 频道：无过滤器时渲染 thread 看板，而不是事件流。`--thread` / `--action` 仅 forum，对 chat 频道会报错。
- `--kind` 对照 `CHANNEL_EVENT_KINDS` 校验（单值，不是 CSV——CSV 在 `wait` 一侧）。

### `wait <name>`

```bash
trellis channel wait <name>
  --as <agent>                            # REQUIRED — self for filter ctx
  [--scope project|global]
  [--timeout <Ns|Nm|Nh|Nms>]              # parsed by parseDuration
  [--from <a,b>]                          # author CSV
  [--kind <k1,k2>]                        # CSV, OR semantics
  [--thread <key>]                        # forum filter
  [--action <thread-action>]              # forum filter
  [--to <target>]                         # default: own agent (broadcast + me)
  [--include-progress]                    # also wake on progress events
  [--all]                                 # require all filters (AND across kinds etc. as implemented)
```

行为：
- 阻塞直到匹配事件到达，或超时。
- 超时 **exit 124**；匹配事件以一行 JSON 打到 stdout。
- 默认可见集合是 `MEANINGFUL_EVENT_KINDS`；用 `--kind` / `--include-progress` 放宽。

---

## tag-vs-kind — 事件形状实际如何控制

历史上有人假设 `send --tag` / `run --tag` 或自定义 kind 能当完成信号。现行 CLI **没有**这些：

- **没有** `--tag` flag（任何子命令都没有用户侧 tag 命名空间）。
- `kind` 是 **白名单系统字段**，由 `CHANNEL_EVENT_KINDS` 约束；非法值报
  `Invalid --kind '<x>'. Must be one of: …`。
- `--kind` 在 `wait`（CSV，OR 语义）与 `messages`（单值）上。`send` 与 `run` 不能发自定义 kind——每次 `send` 都写 `message` 事件。
- 回合中途中止 worker **不是** tag。它是专用 `channel interrupt` 命令，追加 `interrupt_requested` / `interrupted` 对，并在 provider 层 interrupt worker。

调度方等 worker 的实用规则：

- 用 `--kind done,turn_finished` 表示「worker 完成一个 turn」——这些是 supervisor 自动发的系统事件。不要依赖 worker LLM 记得发任何自定义信号。
- 只有在你**真的**要中途 abort 时才用 `trellis channel interrupt`（命令）。
- **不要**发明用户侧 tag 当完成信号。没有 `--tag` 过滤器；worker 把自定义字符串写进最终消息，只是 `message` 事件里的文本，`wait` 匹配不到。

长正文始终走 stdin 或文件：

```bash
trellis channel send T --as A --stdin < /tmp/message.md
trellis channel send T --as A --text-file /tmp/message.md
```

---

## 中断（Interrupt）

### `interrupt <name> [text]`

```bash
trellis channel interrupt <name> [text]
  --as <agent>                            # REQUIRED — caller
  --to <agent>                            # REQUIRED — target worker
  [--scope project|global]
  [--stdin | --text-file <path>]
```

行为：
- 追加 `interrupt` 事件，`reason: "user"`，带替换指令正文；在支持的地方 supervisor 做 provider 级 interrupt（Claude `/interrupt`、Codex turn cancel）。
- stdout 打印追加的事件 JSON。

---

## Workers

### `spawn <name>`

```bash
trellis channel spawn <name>
  [--scope project|global]
  [--agent <agent-name>]                  # loads .trellis/agents/<name>.md
  [--provider claude|codex]               # overrides agent file
  [--as <worker-name>]                    # default: agent name
  [--cwd <path>]
  [--model <id>]
  [--resume <id>]                         # session/thread id resume
  [--timeout <Ns|Nm|Nh>]                  # auto-kill after duration
  [--warn-before <Ns|Nm|Nh>]              # supervisor_warning lead time
                                          # default 5m, 0ms disables
  [--file <path>] ...                     # glob, repeatable; inject content
  [--jsonl <path>] ...                    # Trellis manifest, repeatable
  [--by <agent>]                          # spawn-event author
                                          # default: TRELLIS_CHANNEL_AS env or 'main'
  [--inbox-policy explicitOnly|broadcastAndExplicit]
                                          # default explicitOnly
  [--idle-timeout <Ns|Nm|Nh>]             # OOM-guard idle TTL
                                          # default 5m, 0 disables
  [--max-live-workers <n>]                # spawn-time live-worker budget
                                          # default 6, 0 disables
```

行为：
- provider 对照 adapter registry 校验
  （`packages/cli/src/commands/channel/adapters/`）；当前：`claude`、`codex`。
- 在第一次 `send --to <worker>` 之前，worker 保持 inbox-idle。
- 记录带 `pid`、`provider`、`agent`、`files`、`manifests` 的 `spawned` 事件。
- OOM-guard 优先级：CLI flag → 环境变量
  （`TRELLIS_CHANNEL_WORKER_IDLE_TIMEOUT`、
  `TRELLIS_CHANNEL_MAX_LIVE_WORKERS`）→
  `.trellis/config.yaml#channel.worker_guard` → 内置默认。

### `run [name]`

```bash
trellis channel run [name?]
  [--agent <name>]
  [--provider claude|codex]
  [--as <worker-name>]
  [--cwd <path>]
  [--model <id>]
  [--file <path>] ...                     # repeatable, glob
  [--jsonl <path>] ...                    # repeatable
  [--message <text> | --message-file <path> | --stdin]
  [--timeout <Ns|Nm|Nh>]                  # default 5m
```

行为：
- 一次性。省略 `name` 时自动生成 `run-<hex>`。
- 创建 ephemeral 频道（`createMode=run`），spawn 单个 worker，发送 prompt，等待 `done`，把最终 assistant 文本打到 stdout，成功后删除频道。失败则保留频道供检查，exit code 1。

> `run` **没有** `--tag` flag。完成靠 supervisor 发出的 `done` 事件检测。

### `kill <name>`

```bash
trellis channel kill <name>
  --as <agent>                            # REQUIRED — worker agent name
  [--scope project|global]
  [--force]                               # SIGKILL immediately
```

行为：
- 默认路径：SIGTERM → 8s 宽限 → SIGKILL 升级；需要 SIGKILL 时 CLI 写 `killed` 事件，保持日志真实。
- 清理 `pid`、`worker-pid`、`config`、`spawnlock` sidecar；保留 `log`、`session-id`、`thread-id` 供取证 / resume。

### `rm <name>`

```bash
trellis channel rm <name>
  [--scope project|global]
```

行为：
- 杀掉任何存活 worker，然后删除整个频道目录。
- 打印 `Removed channel '<name>'`。

### `prune`

```bash
trellis channel prune
  [--scope project|global]                # omitted: scan every project
  [--all | --empty | --idle <Ns|Nm|Nh|Nd> | --ephemeral]   # mutually exclusive
  [--yes]                                 # actually delete (default: dry-run)
  [--dry-run]                             # default true; redundant with default
  [--keep <names,csv>]                    # exclusion list
```

行为：
- 过滤 flag 互斥——否则报错。
- 默认 dry-run；`--yes` 才真删。
- 不带 `--scope` 时扫描**每个** project bucket（有意做成仓库级清理）；带 `--scope project|global` 则限该 bucket。
- 有存活 worker 的频道无论过滤如何都跳过。
- 输出：每个候选一行 `name  last-ts  (reason)`，加最终汇总。

---

## Forum 频道（Forum Channels）

### `post <name> <action>`

```bash
trellis channel post <name> <action>
  --as <agent>                            # REQUIRED
  [--scope project|global]
  [--thread <key>]                        # required except action=opened
  [--title <text>]
  [--text <text> | --stdin | --text-file <path>]
  [--description <text>]                  # stable thread description
  [--status <status>]
  [--labels a,b]                          # REPLACES thread labels
  [--assignees a,b]                       # REPLACES assignees
  [--summary <text>]
  [--context-file <abs-path>] ...
  [--context-raw  <text>]      ...
  [--linked-context-file <abs-path>]      # [deprecated alias]
  [--linked-context-raw  <text>]          # [deprecated alias]
```

行为：
- CLI 面上 `<action>` 自由文本；惯用值包括
  `opened`、`comment`、`status`、`labels`、`assignees`、`summary`、
  `processed`。
- `action=rename` 被拒绝——改用 `thread rename`。
- `--labels` / `--assignees` 是替换语义，不是追加。
- 输出：stdout 上的追加事件 JSON。

### `forum <name>`

```bash
trellis channel forum <name>
  [--scope project|global]
  [--status <status>]
  [--raw]
```

行为：
- 列出 threads（归约后状态）。`--status` 按当前 thread status 过滤。`--raw` 每 thread 打一条 JSON。

### `thread <name> <thread>` / `thread rename`

```bash
trellis channel thread <name> <thread-key>
  [--scope project|global]
  [--raw]

trellis channel thread rename <name> <old-thread> <new-thread>
  --as <agent>                            # REQUIRED
  [--scope project|global]
```

行为：
- `thread <name> <key>` 显示一个 thread 的时间线：
  头行 `<thread> [<status>] <title>`，然后 description / labels /
  assignees / summary / timeline 行。`--raw` 切到原始事件。
- `thread rename` 是唯一变更入口；`post --action rename` 被拒绝。

---

## Context / Title

### `context add` / `context delete` / `context list`

```bash
trellis channel context add <name>
  [--as <agent>]                          # default: main
  [--scope project|global]
  [--thread <key>]                        # thread-level instead of channel-level
  [--file <abs-path>] ...                 # repeatable
  [--raw <text>]      ...                 # repeatable
                                          # at least one of --file or --raw

trellis channel context delete <name>
  [--as <agent>]                          # default: main
  [--scope project|global]
  [--thread <key>]
  [--file <abs-path>] ...
  [--raw <text>]      ...

trellis channel context list <name>
  [--scope project|global]
  [--thread <key>]
  [--raw]                                 # one JSON entry per line
```

行为：
- `add` / `delete` 追加 `context` 事件并打印事件 JSON。
- `list` 投影当前 context 条目；pretty 输出为
  `file <path>` / `raw <truncated text>` 行，空时为 `(no context)`。

### `title set <name>` / `title clear <name>`

```bash
trellis channel title set <name>
  --title <text>                          # REQUIRED
  [--as <agent>]                          # default: main
  [--scope project|global]

trellis channel title clear <name>
  [--as <agent>]                          # default: main
  [--scope project|global]
```

行为：
- 追加 `title` 事件，把稳定显示标题投影到频道。输出：事件 JSON。

---

## 隐藏 / 内部（Hidden / Internal）

| Command | Purpose |
|---|---|
| `channel __supervisor <channel> <worker> <config>` | `spawn` 派生的入口。不要直接调用。 |
| `channel __parse-trace <adapter> <file>` | 开发辅助——把录好的 stream-json / wire trace 回放到匹配 adapter，打印得到的 channel 事件。adapter 对照 provider registry 校验。 |

---

## 事件模型（Event Model）

`CHANNEL_EVENT_KINDS`（由 `parseChannelKind` 强制白名单）：

`create`, `join`, `leave`, `message`, `thread`, `context`, `channel`,
`spawned`, `killed`, `respawned`, `progress`, `done`, `error`, `waiting`,
`awake`, `undeliverable`, `interrupt_requested`, `turn_started`,
`turn_finished`, `interrupted`, `supervisor_warning`.

`MEANINGFUL_EVENT_KINDS`（`wait` / `messages` 在未显式给 `--kind` 时默认可见子集）：

`create`, `join`, `leave`, `message`, `thread`, `context`, `channel`,
`spawned`, `killed`, `respawned`, `done`, `error`.

非 meaningful kinds（如 `progress`、`waiting`、`awake`、
`supervisor_warning`、`turn_*` / `interrupt*` 集合）仍会进 store；通过 `--kind` 或 `--include-progress` 选择加入。

Forum 频道是 event-sourced；状态投影用 CLI reducer
（`forum`、`thread`、`context list`）。

---

## 输出约定（Output Conventions）

- **变更类**（`send`、`interrupt`、`post`、`context add/delete`、
  `title set/clear`、`thread rename`）在 **stdout** 打印追加事件的一行 JSON。
- **流式读取**（`wait`、`messages --follow`）stdout 每行一个 JSON 事件。
- **Pretty 读取**（`list`、`messages`、`forum`、`thread`、`context list`）
  打印带颜色、对齐的表格 / 时间线。
- **`run`** 只把最终 assistant 文本打到 stdout（方便管道）；诊断走 stderr。
- **错误** 经 `chalk.red("Error:")` 到 stderr，并 `exit 1`。
- **`wait` 超时** 特别地 **exit 124**。
