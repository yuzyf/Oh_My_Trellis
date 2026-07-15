> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.agents/skills/trellis-finish-work/SKILL.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

---
name: trellis-finish-work
description: "收束当前会话：确认质量门已通过、提醒用户提交、归档已完成任务，并把会话进展写入开发者日志。在写完代码、准备结束会话时使用。"
---

# 收束工作（Finish Work）

收束当前会话：归档活跃任务（以及用户想一并清理的其他“已完成但未归档”任务），并记录会话日志。代码提交不在这里做 —— 那些发生在工作流阶段 3.4，且应在调用本命令之前完成。

## 步骤 1：盘点当前状态

```bash
python3 ./.trellis/scripts/get_context.py --mode record
```

这会打印：

- **我的活跃任务** —— 检查除当前任务外，是否还有实际上已完成（代码已合并、验收标准已满足）并应在本轮归档的任务。
- **Git 状态** —— 快速看哪些路径是脏的。
- **最近提交** —— 步骤 4 的 `--commit` 需要它们的哈希。

若 `--mode record` 暴露了与当前会话无关、但看起来已完成的其他任务，用一次性确认问用户：“这 N 个任务看起来做完了 —— 本轮也一起归档吗？[y/N]”。默认否；当前活跃任务在步骤 3 仍会归档。

## 步骤 2：健全性检查 —— 给脏路径分类

运行：

```bash
git status --porcelain
```

过滤掉 `.trellis/workspace/` 与 `.trellis/tasks/` 下的路径 —— 它们由 `add_session.py` 与 `task.py archive` 的自动提交管理，会因本技能自身工作而变脏。

对每个剩余脏路径，判断它属于**当前任务**还是**其他并行工作**（例如另一个终端窗口在改同一仓库）。启发式：

- 当前任务的 `prd.md` / `implement.jsonl` / `check.jsonl` 中引用的路径 → 当前任务
- 与任务声明范围匹配的代码区域，或你记得本会话改过的路径 → 当前任务
- 你完全不记得本会话动过、且落在无关区域的路径 → 其他并行工作

然后分流：

- **任一剩余路径看起来像当前任务工作** —— 直接退出，并提示：
  > “工作区仍有本任务的未提交代码改动：`<list>`。先回到工作流阶段 3.4 提交它们，再运行 `finish-work`（Trellis 命令）。”

  这里不要运行 `git commit`。也不要提示用户去提交。用户回到阶段 3.4，由 AI 在那里驱动批量提交。
- **所有剩余路径都看起来无关**（其他并行窗口的工作） —— 报告一次，然后继续步骤 3：
  > “提示：有超出本任务范围的脏文件 —— 留给另一个窗口：`<list>`。”
- **确实不确定** —— 问用户一次：“`<list>` 是我忘了提交的本任务工作，还是另一个窗口的？（commit / ignore）” —— 再按其答案分流。

## 步骤 3：归档任务

```bash
python3 ./.trellis/scripts/task.py archive <task-name>
```

至少：当前活跃任务（若有）。再加上步骤 1 中用户确认的额外任务。每次归档都会通过脚本自动提交产生 `chore(task): archive ...` 提交。

若没有活跃任务，且用户也未确认任何清理归档，跳过本步。

## 步骤 4：记录会话日志

```bash
python3 ./.trellis/scripts/add_session.py \
  --title "Session Title" \
  --commit "hash1,hash2" \
  --summary "Brief summary"
```

`--commit` 使用阶段 3.4 产生的工作提交哈希（可见于步骤 1 的 `Recent commits` 列表，或 `git log --oneline`）。不要包含步骤 3 的归档提交哈希。这会产生一个 `chore: record journal` 提交。

最终 git 日志顺序：`<来自 3.4 的工作提交>` → `chore(task): archive ...`（一个或多个） → `chore: record journal`。

> 译注：三阶段提交顺序是硬约束：先工作提交（3.4）→ 再归档提交 → 最后 journal。`finish-work` 绝不替你补代码 commit。
