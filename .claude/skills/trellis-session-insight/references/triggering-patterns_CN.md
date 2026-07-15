<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-session-insight/references/triggering-patterns.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 触发话术模式（Triggering Patterns）

下列中英原话应让你想到「该用 `trellis mem`」。把它们当直觉训练，不是刚性匹配器。

## 回忆过往方案（Past-solution recall）

用户在找**以前某次会话里的解法**，而不是仓库里的文档。

- "How did we solve X last time?"
- "Have we hit this before?"
- "Remind me how we ended up doing about X?"
- "We dealt with this once already, didn't we?"
- "上次怎么解的?"
- "之前是怎么搞定 X 的?"
- "我记得以前修过类似的"

触达：`trellis mem search "<symptom keyword>" --global --limit 10`，再对最接近的命中做 `context`。

## 决策检索（Decision retrieval）

用户在引用**旧对话里的决策**，而不是任何已提交文件。到 brainstorm 窗口里找。

- "What was the decision on X?"
- "Did we decide to use Postgres or SQLite?"
- "The rationale for choosing X over Y was…?"
- "我们当时为啥选了 X 而不是 Y?"
- "关于 X 我们之前是怎么定的?"
- "之前讨论过 X 的方案吗?"

触达：`trellis mem search "<decision keyword>"` 找到会话，再 `extract <id> --phase brainstorm` 恢复讨论。

## 跨会话续作（Cross-session continuation）

用户隔了一段时间回来，上下文是隐式的。

- "Where were we?"
- "Continue from last time."
- "Pick up where we left off."
- "继续上次的"
- "我们上次做到哪了"
- "接着昨天那个任务"

触达：`trellis mem list --task <current-task-dir>` 找与当前任务绑定的最近会话，再 `extract` 最后一条。

## 熟悉 bug 调试（Familiar-bug debugging）

当前 bug 感觉见过。过往会话里很可能有解决路径。

- "I feel like I've hit this before."
- "Doesn't this look like that bug from last month?"
- "Same kind of timeout I had in X."
- "这个错好像之前见过"
- "这个 bug 是不是上次那个?"
- "怎么又是这个 error?"

触达：`trellis mem search "<error message fragment>" --global`。锚定实际错误串里短而独特的 token。

## 自我模式识别（Self-pattern spotting）

用户在问自己是否反复犯同类错误或做同类决策。

- "Do I always make this mistake?"
- "How often have I run into X?"
- "Is this a recurring thing for me?"
- "我每次都踩这个坑吗?"
- "我老犯这个错?"
- "这类问题之前出现过几次?"

触达：`trellis mem search "<topic>" --global --limit 50`，扫列表里的日期 / 项目。可选 `extract` 两到三条做对比。

## 收工复盘（Finish-work retrospective，按需）

用户**明确**想回看本任务——不是强制步骤，只在对方要求时做。

- "Summarize what we did in this task."
- "What were the key decisions / surprises?"
- "Write up the lessons from this round."
- "总结一下这次的经验"
- "记一下这次踩的坑"
- "复盘下这个任务"

触达：识别当前任务的 session id（来自 `.trellis/.runtime/sessions/*.json` 或 `mem list --task <task-dir>`），再 `extract <id> --phase brainstorm` 与 `--phase implement`。给出摘要——尽量落到具体 file:line。是否还要把摘要写到某处（PRD、spec、notes 文件）由用户决定；可以提议，不要自动写入。

## 反模式：这里不要伸手去拿 `mem`（Anti-patterns）

- "What does this function do?" → 读文件。
- "Why is this test failing?" → 读测试输出与文件。
- "What's the right pattern for X in our codebase?" → grep / 读 spec 文件。
- "What's the latest npm version of Y?" → 调 `npm view`。
- "Fix this bug." → 调试。只有当你怀疑存在先验上下文时才用 `mem`；否则是噪音。

门槛始终是：资深同事会不会在回答前先问「我们不是已经聊过这个了吗？」若会，就用 `mem`；若不会，就别碰。
