<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-channel/references/workers.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# Workers 与 Agent Cards（Workers And Agent Cards）

当对端 agent 应独立执行并通过 channel 事件日志回报时，使用 workers。Worker 是附着在 channel 上的已注册子进程（claude 或 codex）；supervisor 把收件箱消息转给它，再把它的输出译回 channel 事件。

## Spawn

```bash
trellis channel create impl-task --by dispatcher --cwd /path/to/repo
trellis channel spawn impl-task --provider codex --as codex-impl --timeout 30m

echo "Implement the schema for table X per .trellis/.../prd.md" \
  | trellis channel send impl-task --as dispatcher --to codex-impl --stdin

trellis channel wait impl-task --as dispatcher --from codex-impl --kind done --timeout 30m
```

`spawn` 派生 `channel __supervisor` worker：发出 `spawned`、流式 `progress`，应以 `done`、`error` 或 `killed` 结束。Worker 保持收件箱空闲，直到 `send --to <worker>`（或在 `--inbox-policy broadcastAndExplicit` 时的广播）唤醒它们。

关键 `spawn` flags：

- `--agent <name>` — 加载 `.trellis/agents/<name>.md`（provider/model/as/系统提示默认值）。
- `--provider <claude|codex>` — 覆盖 agent card；对照 adapter 注册表校验。
- `--as <name>` — channel worker handle；默认 agent 名。
- `--cwd <path>` — worker 工作目录（也是 `--file`/`--jsonl` 的 jail 根）。
- `--model <id>` — 模型覆盖。
- `--resume <id>` — 恢复已有 claude session / codex thread。
- `--timeout <duration>` — 超时自动 kill：`30s` / `2m` / `1h`。
- `--warn-before <duration>` — supervisor_warning 提前量（默认 `5m`；`0ms` 关闭）。
- `--file <path>`（可重复，支持 glob）— 把文件内容注入系统提示。
- `--jsonl <path>`（可重复）— Trellis jsonl manifest（每行 `{file, reason}`）。
- `--by <agent>` — `spawned` 事件作者（默认 `$TRELLIS_CHANNEL_AS` 或 `main`）。
- `--inbox-policy <explicitOnly|broadcastAndExplicit>` — 默认 `explicitOnly`。
- `--idle-timeout <duration>` — OOM guard 空闲 TTL（默认 `5m`；`0` 关闭）。
- `--max-live-workers <n>` — spawn 时 live-worker 预算（默认 `6`；`0` 关闭）。

成功事件 `spawned` 记录 `pid`、`provider`、`agent`、注入的 `files` 与解析后的 `manifests`，便于事后审计上下文。

## Agent Cards

`--agent <name>` 解析到 `.trellis/agents/<name>.md`。名称须匹配 `[A-Za-z0-9._-]+`。默认 Trellis 安装附带两张卡：

- `.trellis/agents/check.md` — 代码质量评审者。
- `.trellis/agents/implement.md` — 实现运行的编码 worker。

```yaml
---
name: check
description: Code quality check expert.
provider: claude
---
```

Frontmatter 字段填充 `spawn` 默认值（provider、model、`as`）；markdown 正文成为 worker 的 system-prompt 角色。Cards **不会**自动挂任务文件——上下文必须在每次 spawn 时显式注入（见下）。

spawn 命名 agent 前务必检视项目 cards：

```bash
ls .trellis/agents
sed -n '1,100p' .trellis/agents/check.md
```

## 上下文注入（Context Injection）

两个 flag 把内容注入 worker 系统提示的 `# CONTEXT FILES` 块，由 `context-loader` 组装：

- `--file <path>` — 可重复，支持 glob（`*`、`**`）。每个匹配被读入并拼接。
- `--jsonl <path>` — 可重复 Trellis manifest，每行 `{"file":"<path>","reason":"<why>"}`。reason 保留为每个文件内容上方的 header 注释。

loader 强制限制：

- 每文件硬顶 1 MB（超大 → error）。
- 每文件 200 KB 警告到 stderr。
- 组装上下文合计 500 KB 警告到 stderr。
- 路径穿越 jail：所有解析路径必须落在 `--cwd` 下。

对任务目录 spawn check agent 示例：

```bash
TASK=.trellis/tasks/05-13-example
trellis channel spawn cr-example --agent check --provider codex --as check-cx \
  --file "$TASK/prd.md" \
  --file "$TASK/design.md" \
  --file "$TASK/implement.md" \
  --jsonl "$TASK/check.jsonl" \
  --cwd "$PWD" --timeout 30m
```

`spawned` 事件记录字面 `files` 数组与任何由 `--jsonl` 展开的 `manifests`，审计轨迹捕获 worker 实际看到的内容。

## 命名与路由（Names And Routing）

`--as` 有两种含义：

- `send` / `wait` / `interrupt`：发言者身份（结果事件的作者）。
- `spawn`：其它 agent 用 `--to` 寻址的 worker handle。

同一 channel 有多个 workers 或 providers 时用明确名字：

```bash
trellis channel spawn cr-feature --agent check --as check-claude
trellis channel spawn cr-feature --agent check --provider codex --as check-cx

trellis channel wait cr-feature --as main \
  --from check-claude,check-cx --kind done --all --timeout 15m
```

`--all` 要求 `--from`，阻塞直到列出的每个 worker 都产生匹配事件；超时退出码 **124**，stderr 打印 `timeout: still waiting on ...`。

## Soft Interrupt vs Kill

**Soft interrupt**（优先）：

```bash
trellis channel interrupt <channel> --as <worker> --message "Stop and report status"
# 或
trellis channel send <channel> --as dispatcher --to <worker> --tag interrupt --text "..."
```

Worker 适配器应协作停下当前 turn 并发出 `interrupted` / 后续 `done`。

**Hard kill**：

```bash
trellis channel kill <channel> --as <worker>
trellis channel kill <channel> --as <worker> --force
```

`kill` 终止 supervisor/worker 进程树并发 `killed`。`--force` 在清理卡住时使用（幽灵 pid、无响应 supervisor）。

## Respawn / Resume

```bash
trellis channel spawn <channel> --agent check --as check-cx --resume <session-or-thread-id>
```

恢复语义依赖 provider：claude session id 与 codex thread id 存储在 `$CHAN/<worker>.session-id` / `.thread-id`。Resume 不重放已消费收件箱——cursor 仍有效。

## 收件箱策略与空闲

- `explicitOnly`（默认）：仅 `--to <worker>` 的消息进入收件箱。
- `broadcastAndExplicit`：广播 + 显式寻址都进入。
- `--idle-timeout`：无新收件箱活动则 supervisor 可退出（OOM guard）；`0` 关闭。
- `--max-live-workers`：防止同一项目失控 spawn 风暴。

## 日志位置

Worker 日志：`~/.trellis/channels/<bucket>/<channel>/<worker>.log`  
配置快照：`<worker>.config`  
PID 文件：`<worker>.pid`、`<worker>.worker-pid`

诊断卡住 worker 时，先读 log + `messages --raw`，不要先手写解析 `events.jsonl`（尤其 forum）。

## 实践清单

1. spawn 前 `ls .trellis/agents` 并读 card 正文。
2. 用 `--file` / `--jsonl` 显式注入上下文；别假设 card 会挂任务文件。
3. 稳定、独特的 `--as` 名（便于并行与 wait `--all`）。
4. 完成信号用 `--kind done`，不要依赖用户 tag。
5. 长 brief 用 `--text-file` / `--stdin`。
6. 先 soft interrupt，再 kill / `--force`。
