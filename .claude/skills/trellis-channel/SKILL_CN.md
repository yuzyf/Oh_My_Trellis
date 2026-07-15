<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-channel/SKILL.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

---
name: trellis-channel
description: >
  用 Trellis channel 做实时多智能体协作：派生子 worker、跨 agent 评审、进度检视、
  forum 频道，以及 channel 日志调试。
---

# trellis-channel

`trellis channel` 是本地多智能体协作运行时。需要 agent 通过持久事件日志对话、把 worker 作为对等进程拉起、对飞行中的 worker 做 interrupt / 调试，或把反馈记到持久 `--type forum` 频道时，用它。

典型用户信号：「和 codex/claude 讨论」、「brainstorm with another agent」、「spawn an implement/check worker」、「let agent review」、「open an issue board / changelog forum」、「look at this thread」、「channel is stuck / no output」、「progress was truncated」、「how do I write that channel command」。

本 skill 是索引。只加载当前任务对应的参考文件——不要预加载全部。

## 首批命令（First Commands）

```bash
trellis --version
trellis channel --help
trellis channel list --all
trellis channel list --scope global --all
```

若用户点名 channel 或 thread，先检视再要背景：

```bash
trellis channel forum <board> --scope global
trellis channel thread <board> <thread> --scope global
trellis channel context list <board> --scope global --thread <thread>
```

## 按用户意图路由（Route By User Intent）

| User intent | Read |
|---|---|
| "和 codex/claude 讨论一下", "brainstorm with another agent" | `references/workflows.md` |
| "派一个 implement/check agent", "让 agent review", "spawn a worker" | `references/workflows.md`, then `references/workers.md` |
| "开 issue 区 / topic 群 / changelog / board", "make a forum" | `references/forum.md` |
| "看看这个 thread / linked context", "inspect a thread" | `references/forum.md` |
| "channel 卡住了 / 没输出 / progress 被截断", "worker stalled" | `references/progress-debugging.md` |
| "具体命令怎么写", "what flags does X take" | `references/command-reference.md` |

## 核心规则（Core Rules）

- 新建 forum 频道用 `--type forum`。`thread` 是 forum 频道内的一条议题。
- 用 `--context-file` / `--context-raw` 与 `trellis channel context add/delete/list`。`--linked-context-*` 是废弃术语。
- 长消息用 `--stdin` 或 `--text-file`。不要把长中英混排正文放在位置 shell 参数里。
- Pretty 的 `messages` 输出是操作员仪表盘，可能截断 progress。审计用 `--raw`。
- `--as` 是发言者或 worker handle（视命令而定）。多 agent / 多会话时用明确、稳定的名字。
- `--scope project`（默认）操作当前 cwd 的 project bucket；`--scope global` 操作共享 `__global__` bucket。有意识选 scope——global board 在 project 列表里不可见，除非传 `--scope global`。
- Brainstorm 要做多轮压力测试。一答一确认是 review，不是 brainstorm。
- **Dispatcher wait 模式**：完成信号用 `--kind done` / `--kind turn_finished`（trellis 发出的系统事件），**不要**用用户 `--tag` 当完成信号。CLI help 会列 `phase_done` / `question` 作 `--tag` 示例，但只有 `interrupt` 是带硬编码 trellis 行为的保留 tag；其它是不透明用户标签。指望 worker 跑 `send --tag <my_signal>` 不可靠——LLM worker 常把 tag 字符串写进散文而不跑真正 CLI。见 `references/command-reference.md`「tag vs kind」。
- Forum 频道是 event-sourced。不要先解析 `events.jsonl`；用 `forum`、`thread`、`messages --thread`、`context list`。
- `@mindfoldhq/trellis-core` 拥有可复用的 channel/thread 状态、事件追加、seq 分配、context/title 投影、reducer 与 task helper。CLI 拥有 flags、终端渲染、prompts、worker 生命周期与进程退出。

## 参考文件（Reference Files）

- `references/workflows.md` — 规范协作模式 A–F（peer brainstorm、spawned review、dispatch-and-wait、forum issue capture、interrupt-and-redirect、one-shot run）。
- `references/forum.md` — forum 频道、context、title、rename、changelog forum、thread 过滤。
- `references/workers.md` — spawn、agent cards、context 注入（`--file` / `--jsonl`）、interrupt、kill 语义。
- `references/progress-debugging.md` — progress/raw 检视、卡住 worker 诊断、OOM guard、退出码。
- `references/command-reference.md` — 当前 CLI 命令参考（每个子命令、每个 flag、输出约定、scope/type 模型）。

## 不适合（Not For）

- 一次静态评审，markdown 文件 + prompt 就够。
- 用自记日志替代正常 tool call。
- 长期记忆检索。可行动 issue 用持久 forum 频道；会话/历史搜索用 `trellis mem`（`trellis-session-insight` skill）。
