> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.agents/skills/trellis-continue/SKILL.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

---
name: trellis-continue
description: "继续当前任务。加载工作流阶段索引，判断应从哪个阶段/步骤续上，再通过 get_context.py --mode phase 拉取步骤级详情。在回到进行中任务、需要知道下一步做什么时使用。"
---

# 继续当前任务（Continue Current Task）

继续当前任务 —— 在 `.trellis/workflow.md` 中从正确的阶段/步骤接上。
中文对照：`.trellis/workflow_CN.md`

---

## 步骤 1：加载当前上下文

```bash
python3 ./.trellis/scripts/get_context.py
```

确认：当前任务、git 状态、最近提交。

## 步骤 2：加载阶段索引

```bash
python3 ./.trellis/scripts/get_context.py --mode phase
```

展示阶段索引（Plan / Execute / Finish）以及路由 + 技能映射。

## 步骤 3：判断你在哪

`get_context.py` 会显示活跃任务的 `status` 字段。按 `status` + 产物是否存在来路由。这条命令替用户记住 Trellis 流程；它本身并不批准进入实现。

- `status=planning` + 没有 `prd.md` → **1.1**（加载 `trellis-brainstorm`）
- `status=planning` + 只有 `prd.md` → 判断任务是轻量还是复杂。轻量可进入 **1.4** 评审；复杂回到 **1.1** 补 `design.md` + `implement.md`。
- `status=planning` + 复杂产物已齐 + 子代理 jsonl 未整理（只有种子 `_example` 行） → **1.3**
- `status=planning` + 必需产物已齐 + 必需 jsonl 已整理或处于 inline 模式 → **1.4**（请用户做 start 评审；用户确认后才运行 `task.py start`）
- `status=in_progress` + 实现尚未开始 → **2.1**
- `status=in_progress` + 实现已完成、尚未检查 → **2.2**
- `status=in_progress` + 检查已通过 → **3.3**（规范更新）→ **3.4**（提交）
- `status=completed`（少见；通常会立刻归档） → 归档流程

阶段规则（完整细节见 `.trellis/workflow.md`）：

1. 同一阶段内步骤**按顺序**执行 —— `[required]` 步骤不得跳过
2. `[once]` 步骤若所需输出已存在则视为已完成。只有轻量任务可以只靠 `prd.md`；复杂任务还需要 `design.md` 和 `implement.md`。
3. 若有新发现，可以回到更早阶段

## 步骤 4：加载具体步骤

一旦知道从哪一步续上：

```bash
python3 ./.trellis/scripts/get_context.py --mode phase --step <X.X> --platform codex
```

按加载到的说明执行。每个 `[required]` 步骤完成后，进入下一步。

---

## 参考

完整工作流与详细阶段步骤在 `.trellis/workflow.md`。本命令只是入口 —— 权威说明在那里。
中文对照：`.trellis/workflow_CN.md`

> 译注：`continue` 的核心是“状态机续跑”：看 `status` + 产物齐不齐，再落到 `1.x/2.x/3.x`，最后用 `--step` 拉步骤细则。
