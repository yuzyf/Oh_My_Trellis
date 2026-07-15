<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-channel/references/workflows.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 工作流（Workflows）

按意图使用这些模式。多轮工作优先持久 channel；一次性问题用 `channel run`。

## 模式 A：多轮 Brainstorm（Multi-round Brainstorm）

用户说「和 codex/claude 讨论一下」、「brainstorm」或「拉一个 agent 进来一起看」时使用。

```bash
trellis channel create brainstorm-storage-layer --by main \
  --task .trellis/tasks/05-XX-storage-adapter

trellis channel spawn brainstorm-storage-layer \
  --agent architect --provider codex \
  --file .trellis/tasks/05-XX-storage-adapter/prd.md \
  --file .trellis/tasks/05-XX-storage-adapter/design.md \
  --as cx-arch --timeout 30m

trellis channel send brainstorm-storage-layer \
  --as main --to cx-arch --text-file /tmp/brainstorm-r1.md

trellis channel wait brainstorm-storage-layer \
  --as main --kind done --from cx-arch --timeout 10m
```

不要一答就停。读答案、找含糊处、发新探针，直到结果可执行。

最低轮次结构：

1. 方向拆分：落在现有机制还是新机制？
2. MVP 边界：v1、v2，以及什么会把 v2 逼回 v1。
3. 数据契约：事件、schema、metadata、状态真源、兼容性。
4. CLI / UX 契约：命令名、flags、错误、默认值、歧义。
5. 跨层风险与测试：共享 helper、漂移点、发布阻断测试。

可选轮次：

- 运维：日志、调试、卡住的 worker、kill/restart、恢复。
- 迁移/发布：破坏性状态、manifest、changelog、docs-site。
- 对立评审：让对端 agent 反对当前计划。

每个探针应要求具体文件路径、命令、schema、被拒备选与发布阻断问题。需要决策时拒绝和稀泥。

## 模式 B：Implement / Check Agent

用户要求派实现或评审工作时使用。

```bash
TASK=.trellis/tasks/05-12-foo
trellis channel create cr-foo --task "$TASK" --by main

trellis channel spawn cr-foo \
  --agent check \
  --jsonl "$TASK/check.jsonl" \
  --file "$TASK/prd.md" \
  --file "$TASK/design.md" \
  --file "$TASK/implement.md" \
  --cwd "$PWD" --timeout 15m

trellis channel send cr-foo --as main --to check --text-file /tmp/cr-brief.md
trellis channel wait cr-foo --as main --kind done --from check --timeout 15m
trellis channel messages cr-foo --kind message --from check --tag final_answer
```

实现工作用 `--agent implement` 并发送实现 brief。检查工作要包含确切 diff 范围、相关 specs、以及已跑过的验证。

## 模式 C：并行 Reviewers（Parallel Reviewers）

一个 channel，不同 worker 名。

```bash
trellis channel create cr-feature --by main --ephemeral

trellis channel spawn cr-feature --agent check \
  --jsonl "$TASK/check.jsonl" --file "$TASK/prd.md" --file "$TASK/design.md" \
  --timeout 15m

trellis channel spawn cr-feature --agent check --provider codex --as check-cx \
  --jsonl "$TASK/check.jsonl" --file "$TASK/prd.md" --file "$TASK/design.md" \
  --timeout 15m

trellis channel send cr-feature --as main --to check --text-file /tmp/cr-brief.md
trellis channel send cr-feature --as main --to check-cx --text-file /tmp/cr-brief.md
trellis channel wait cr-feature --as main --kind done --from check,check-cx --all --timeout 15m
```

`--all` 表示列出的每个 worker 都必须发出匹配事件。

## 模式 D：一次性 Worker（One-shot Worker）

```bash
trellis channel run --provider codex --message "say hi in 3 words" --timeout 1m
trellis channel run --agent plan --message-file /tmp/plan-question.md --timeout 10m
```

成功时 `run` 删除 ephemeral channel。错误/超时/killed 时保留 channel 并打印路径供检视。

## 模式 E：Forum Channel

用于 issue forum、主题式反馈、发布 todo、agent findings、内部 changelog。完整模型见 `forum.md`。

## 模式 F：接管已有 Thread（Take Over Existing Thread）

用户给出 forum/thread 名时，自行恢复上下文：

```bash
trellis channel forum <board> --scope global
trellis channel thread <board> <thread> --scope global --raw
trellis channel context list <board> --scope global --thread <thread>
trellis channel messages <board> --scope global --raw --thread <thread>
```

输出约束摘要，不是 transcript 倾倒：

- 用户层问题
- 影响本仓库的 context 文件
- 当前版本 vs 未来版本需求
- 当前代码/设计是否满足
- 下一步动作或要追加的评论
