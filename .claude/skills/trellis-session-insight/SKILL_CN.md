> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.claude/skills/trellis-session-insight/SKILL.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

---
name: trellis-session-insight
description: "通过 `trellis mem` CLI 触达过去的 AI 对话历史。在用户问「上次怎么解的 X」「我们讨论过吗」「X 的决策是什么」「提醒我这个任务做了什么」「上次怎么解的」「之前讨论过吗」「想起一段对话」时使用；也在 brainstorm 与过往工作重叠、调试熟悉 bug、跨会话续任务，或做 finish-work 复盘时使用。返回的是原始过往对话；当即决定是更新 spec、追加任务笔记、在回答里引用，还是只内化吸收。"
---

# Trellis 会话洞察（Session Insight）

本 skill 教 AI **如何调用 `trellis mem`** —— 项目的跨会话记忆原料 —— 以及 **什么时候伸手去用它是对的**。

它有意做成 **能力 skill，而不是工作流**。没有固定产出文件，没有强制写回步骤，也没有「每次 finish-work 后都要跑」的规则。`mem` 返回的内容怎么用，是当下对话里的判断。本 skill 存在的意义是：让 AI 知道这项能力在，并能决定要不要用。

## `trellis mem` 是什么

一个本地 CLI，索引用户过去的 Claude Code、Codex、Pi Agent 对话日志（各平台存在 `~/.claude/projects/`、`~/.codex/sessions/`、`~/.pi/agent/sessions/` 的 JSONL），并支持列表、搜索、按 Trellis 任务边界切片，以及导出清洗后的对话。OpenCode 日志尚不可索引（provider adapter 待实现）——若目标明显是 OpenCode 会话，应说明限制，而不是瞎猜。

`mem` 中没有任何内容会上传。全部读取都在本地。

## 何时该用

门槛是：「资深同事会不会问『这事我们不是聊过吗？』」——那些时刻才该用。具体模式包括：

- **Brainstorm 重跑风险。** 新任务碰到用户以前待过的区域，你想先查是否已有决策——再问用户之前。
- **熟悉 bug 调试。** 当前 bug 模式像用户以前报过/修过的。拉相关旧会话可省一整轮调试。
- **跨会话续作。** 用户隔了一段时间回来，说「说到哪了」/「继续上次的」，但没说具体。
- **决策检索。** 用户提到「我们关于 X 的那个决策」，但决策在旧 brainstorm 里，不在任何 `prd.md` / `spec/`。
- **Finish-work 复盘。** 用户明确要求总结本任务决定了什么 / 哪疼 / 哪意外——不是每次 finish-work 的强制步骤。
- **跨过往工作找模式。** 用户问「我是不是总在 X 上犯同样错」/「我每次都踩这个坑吗」——跨会话搜索能答。

若以上都不适用，不要调用 `mem`。它是工具，不是仪式。

## 何时不该用

- 相关上下文已在当前轮次、`prd.md`、`design.md`、最近 `git log` 或打开的文件里。`mem` 是给「已经够不着」的东西。
- 用户问的是代码里的事实，不是过往对话里的事实。`git log -p` / `grep` / 直接读文件更快且更权威。
- 你在子 agent（`trellis-implement` / `trellis-check`）里，其派发提示已包含策展过的 `implement.jsonl` / `check.jsonl` 上下文。再叠 `mem` 通常只会添乱。
- 用户明确说「别翻历史，就答我问的」。

## `mem` 返回后做什么

把输出当 **原料**，不是交付物。拿到后按现场对话决定：

- **在回复里引用**，若某段过往交流直接回答当前问题——并引用 session-id / phase 以便用户核验。
- **更新 `<task>/prd.md` 或 `<task>/design.md`**，若 `mem` 挖出本该写下来却没写的关键决策。先把拟议修改亮给用户。
- **追加到任务本地笔记**（如 `<task>/notes.md` 或扩展既有文件），若发现属于当前任务记录但塞不进 PRD。
- **更新 `.trellis/spec/`**，若发现是项目级约定或 gotcha，对未来任务有用。为此运行 `trellis-update-spec` skill——`session-insight` 止于发现。
- **只吸收** 用于接下来几轮、答得更好，什么都不写。一次性回忆时这常常是正确动作。

Trellis 不规定唯一落点。强迫每次回忆都进固定文件，文件会涨成噪音。让情境决定。

## 怎么调用

完整 CLI 参考见 `references/cli-quick-reference.md`。80% 的情况是下面之一：

```bash
# 找内容提到关键词的会话（默认项目范围；
# 需要跨项目时加 --global）
trellis mem search "keyword"

# 列出本项目最近会话
trellis mem list --limit 20

# 深入某一会话：高分命中轮次 + 周边上下文
trellis mem context <session-id> --grep "keyword"

# 导出清洗后的对话（可按 phase 切片）
trellis mem extract <session-id> --phase brainstorm
trellis mem extract <session-id> --phase implement
```

Phase 切片（`--phase brainstorm|implement|all`）按 `task.py create` 与 `task.py start` 边界切割会话。对本任务的 finish-work 复盘，`--phase brainstorm` 恢复规划讨论，`--phase implement` 恢复执行循环。默认是 `all`。

## 触发话术模式

`references/triggering-patterns.md` 列出更多应让你想到「该用 `mem`」的用户原话（中英）——训练直觉时备查。

## 范围外

- `mem` 不改代码、不更新文件。任何写回都是你当下的决定。
- `mem` 对平台 JSONL 存储只读。不推送、不同步到远端。
- 本 skill 不替代 `trellis-update-spec`（那是把发现提升为项目级指南的正确工具），也不替代平台原生的任务 / 规范工作流。
