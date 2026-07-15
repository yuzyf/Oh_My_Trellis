<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/local-architecture/workspace-memory.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 本地工作区记忆系统（Local Workspace Memory System）

`.trellis/workspace/` 保存跨会话记忆。它的目的，是让 AI 和人在不同窗口、不同日期里，都能看懂「之前发生过什么」。

## 目录结构（Directory Structure）

```text
.trellis/workspace/
├── index.md
└── <developer>/
    ├── index.md
    ├── journal-1.md
    └── journal-2.md
```

| File | Purpose |
| --- | --- |
| `.trellis/.developer` | 当前开发者身份。 |
| `.trellis/workspace/index.md` | 全局工作区总览。 |
| `.trellis/workspace/<developer>/index.md` | 某个开发者的会话索引。 |
| `.trellis/workspace/<developer>/journal-N.md` | 会话日志（journal）。 |

## 开发者身份（Developer Identity）

第一次使用时运行：

```bash
python3 ./.trellis/scripts/init_developer.py <name>
```

这会创建 `.trellis/.developer` 以及对应的 workspace 目录。AI 不应随意改开发者身份；若身份不对，先确认当前项目是谁在用。

## 会话日志（Journal）

`journal-N.md` 记录每次会话里已完成或半完成的工作。默认每个 journal 大约容纳 2000 行，超出后轮转到下一个文件。

常用记录命令：

```bash
python3 ./.trellis/scripts/add_session.py \
  --title "Session title" \
  --summary "What changed" \
  --commit "abc1234"
```

规划或评审类工作没有 commit 时，也可以用 `--no-commit` 或空 commit 值来记录。

## 工作区记忆与任务的关系（Relationship Between Workspace Memory And Tasks）

| System | What it stores |
| --- | --- |
| `.trellis/tasks/` | 某个具体任务的需求、设计、调研与状态。 |
| `.trellis/workspace/` | 跨任务、跨会话的工作记录。 |
| `.trellis/spec/` | 作为长期约定保留的工程知识。 |

若信息只对当前任务有用，放进任务目录。  
若信息描述的是当前会话里发生了什么，放进 workspace journal。  
若信息以后写代码时每次都要遵守，放进 spec。

## 本地可定制点（Local Customization Points）

| Need | Edit location |
| --- | --- |
| 修改 journal 最大行数 | `.trellis/config.yaml` 中的 `max_journal_lines`。 |
| 修改会话自动提交说明 | `.trellis/config.yaml` 中的 `session_commit_message`。 |
| 修改会话内容格式 | `.trellis/scripts/add_session.py`。 |
| 修改 workspace 在上下文中的展示方式 | `.trellis/scripts/common/session_context.py`。 |

## AI 使用规则（AI Usage Rules）

AI 不应把 workspace 当作唯一事实来源。恢复任务时，先读当前任务，再用 workspace 补背景。任务完成后，把重要过程笔记记入 workspace；若沉淀出长期规则，再更新 spec。
