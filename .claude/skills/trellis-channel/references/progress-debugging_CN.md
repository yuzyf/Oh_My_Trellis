<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-channel/references/progress-debugging.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 进度与调试（Progress And Debugging）

当 channel「卡住」、progress 被截断、worker 无输出，或你需要审计真实事件流时使用本文。

## Pretty 输出可能截断 Progress

Pretty `messages` 是操作员仪表盘：长 progress 行会被截断以便阅读。**审计与调试必须用 `--raw`。**

```bash
trellis channel messages <channel> --raw --last 50
trellis channel messages <channel> --raw --kind progress --last 80
trellis channel messages <channel> --raw --include-progress --last 100
```

## Progress 事件形状

Progress 事件通常携带：

- `detail.text` / `detail.message` — 局部模型输出（跨事件拼接可重建流式回复）。
- `detail.tool_name`、`detail.tool_input` — 即将运行或正在运行的 tool call。
- `detail.status` — 长动作短串（`starting`、`running`、`flushing`、`done`）。
- `detail.action` — 语义标签（如 thread heartbeat 的 `status`）。

Progress 事件**天生嘈杂**。`wait` 默认忽略它们，除非 `--include-progress`。要看 progress 时优先：

```bash
trellis channel messages <channel> --raw --kind progress --last 80
```

稳定吐 progress 却从不以 `done`/`error`/`message` 收尾的流，是挂死 tool call 的经典形状——检查 worker log 里的子进程。

## Wait 语义（速查）

`channel wait` 从 EOF 监视 `events.jsonl`，在以下事件醒来：

- `message`
- `done`
- `error`
- `killed`
- `progress` 仅在 `--include-progress` 时

有用过滤：

```bash
trellis channel wait T --as main --from check --kind done --timeout 15m
trellis channel wait T --as main --from check,check-cx --kind done --all --timeout 15m
trellis channel wait T --as worker --tag interrupt --timeout 1h
trellis channel wait T --as main --thread release-note --action status --timeout 10m
```

退出码：`0` 匹配，`124` 超时，`1`/`2` 错误。`wait --all` 超时时 stderr 点名仍缺的 workers。

## 审计 `events.jsonl`——用子命令，不要 `grep`

每个 channel 在 `$CHAN/events.jsonl` 持久化完整历史。调试时很想直接 `tail` / `grep` / `jq`。别养成习惯，**永远不要**对 forum 频道这样做。

为何先用子命令：

- `messages` 已用过滤器（`--kind`、`--from`、`--last`、`--tag`、`--thread`、`--action`）回放文件，并用 `--raw` 给精确 JSON。你想写的 one-liner，`messages` 多半已能做。
- `wait` 用 EOF 语义消费同一文件——用 `tail -f | jq` 重实现会在负载下丢事件、在轮转下乱序。
- `context` 物化 worker 收件箱视图（含 cursor）。手写过滤不尊重 `<worker>.inbox-cursor`。

### Forum 频道：切勿直接解析 `events.jsonl`

Forum 频道把多条逻辑 thread 复用到单个 `events.jsonl`。每条事件带 `thread`、`action` 与 tag 字段，forum 子命令知道如何折叠。手解析会：

- 把 threads 混在一起，使 thread 看起来语无伦次。
- 漏掉改变后续解释的生命周期事件（open / status / close）。
- 忽略 worker 收件箱 cursor，于是「看见」worker 已消费的事件还当 pending。

改用 forum 感知视图：

```bash
# List logical threads inside the forum channel
trellis channel forum <channel>

# Inspect one thread end-to-end
trellis channel thread <channel> <thread>

# Replay messages for a thread (supports --raw, --kind, --last)
trellis channel messages <channel> --thread <thread> --raw --last 100

# Context for channel or thread
trellis channel context list <channel> --thread <thread>
```

直接读 `events.jsonl` 仅留给 CLI 本身可疑时——例如确认事件是否真的落盘，或在调试 supervisor 时对照 `<worker>.inbox-cursor`。

## 常见失败（Common Failures）

| Symptom | Cause | Fix |
|---|---|---|
| `trellis: command not found` | CLI not installed globally | `npm install -g @mindfoldhq/trellis` |
| `wait` exits immediately | wrong filter or identity collision | use distinct `--as`, inspect raw messages |
| zsh errors on message text | shell interpreted punctuation | use `--stdin` or `--text-file` |
| progress line is cut off | pretty output truncation | use `messages --raw --kind progress` |
| worker never speaks | provider startup / prompt / MCP delay | inspect `<worker>.log`, `ps`, raw events |
| channel not found in another cwd | project bucket mismatch | `cd` to project, use `--scope global`, or `list --all-projects` |
| ghost worker in list | supervisor died without cleanup | `trellis channel kill <name> --as <worker> --force` |
| forum thread looks scrambled | parsed `events.jsonl` directly | use `forum`, `thread`, `messages --thread` |

## 存储布局（Storage Layout）

```text
~/.trellis/channels/
└── <bucket>/
    └── <channel-name>/
        ├── events.jsonl
        ├── <channel>.lock
        ├── <worker>.log
        ├── <worker>.pid
        ├── <worker>.worker-pid
        ├── <worker>.config
        ├── <worker>.session-id
        ├── <worker>.thread-id
        ├── <worker>.inbox-cursor
        └── <worker>.spawnlock
```

Agent 正常应使用 CLI，而非直接读文件。直接读文件仅在 CLI 视图不足时调试——即便如此，也永远不要直接读 forum 的 `events.jsonl`。

## 诊断流程（建议顺序）

1. `trellis channel list --all`（必要时 `--scope global`）确认频道存在与 scope。
2. `messages --raw --last N` 看最近真实事件。
3. 若有 worker：`ps` + 读 `<worker>.log`。
4. `wait` 行为异常：核对 `--as` / `--from` / `--kind`（完成信号用 kind，不是随意 tag）。
5. 仍卡：soft `interrupt` → 再 `kill` → 必要时 `--force`。
6. Forum 问题：只用 `forum` / `thread` / `messages --thread` / `context list`。
