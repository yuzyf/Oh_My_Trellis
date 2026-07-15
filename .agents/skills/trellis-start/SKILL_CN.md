> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.agents/skills/trellis-start/SKILL.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

---
name: trellis-start
description: "初始化一次 AI 开发会话：读取工作流指南、开发者身份、git 状态、活跃任务，以及 .trellis/ 下的项目规范。对进来的任务做分类，并路由到 brainstorm、直接编辑或任务工作流。在新编码会话开始、恢复工作、启动新任务，或重新建立项目上下文时使用。"
---

# 启动会话（Start Session）

初始化一次由 Trellis 管理的开发会话。该平台没有 session-start hook，因此请按下列步骤手动加载等价的精简上下文。

---

## 步骤 1：当前状态
身份、git 状态、当前任务、活跃任务、日志位置。

```bash
python3 ./.trellis/scripts/get_context.py
```

若输出中有以 `Trellis update available:` 开头的行，在汇总会话上下文时原样复制整行。不要缩短操作命令提示。

## 步骤 2：工作流总览
精简版阶段索引（Phase Index）、请求分诊规则、规划产物约定，以及步骤详情命令。

```bash
python3 ./.trellis/scripts/get_context.py --mode phase
```

完整指南见 `.trellis/workflow.md`（按需阅读）。
中文对照：`.trellis/workflow_CN.md`

## 步骤 3：规范索引
发现包与规范层，然后阅读每个相关的 index 文件。

```bash
python3 ./.trellis/scripts/get_context.py --mode packages
cat .trellis/spec/guides/index.md
cat .trellis/spec/<package>/<layer>/index.md   # 每个相关层
```

index 文件会列出真正开始写代码时要读的具体规范文档。

## 步骤 4：决定下一步
从步骤 1 可知当前任务与状态。检查任务目录：

- **活跃任务状态为 `planning` 且没有 `prd.md`** → 进入阶段 1.1。加载 `trellis-brainstorm` 技能。
- **活跃任务状态为 `planning` 且已有 `prd.md`** → 留在阶段 1。轻量任务可以只有 PRD；复杂任务还需要 `design.md` + `implement.md`。在 `task.py start` 前加载对应的阶段 1 步骤详情。
- **活跃任务状态为 `in_progress`** → 阶段 2 步骤 2.1。加载步骤详情：
  ```bash
  python3 ./.trellis/scripts/get_context.py --mode phase --step 2.1 --platform codex
  ```
- **没有活跃任务** → 先分类。简单对话/小任务，只问本轮要不要创建 Trellis 任务。复杂工作，询问是否可创建 Trellis 任务并进入规划。若用户说不，本会话跳过 Trellis。

---

## 技能路由（速查）

| 用户意图 | 技能 |
|---|---|
| 新功能 / 需求不清晰 | `trellis-brainstorm` |
| 即将写代码 | `trellis-before-dev` |
| 写完代码 / 质量检查 | `trellis-check` |
| 卡住 / 同一 bug 修了多次 | `trellis-break-loop` |
| 学到值得沉淀的东西 | `trellis-update-spec` |

完整规则 + 反合理化表见 `.trellis/workflow.md`。
中文对照：`.trellis/workflow_CN.md`

> 译注：这是 Codex 等无 session-start hook 平台的“进场脚本”。先 `get_context.py` 摸清身份/任务，再按 `planning` / `in_progress` / 无任务分流。
