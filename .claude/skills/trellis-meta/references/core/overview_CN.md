<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/core/overview.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 核心系统总览（Core Systems Overview）

这些系统在**所有平台**上工作（Claude Code、Cursor 与未来平台）。

---

## 核心里有什么？（What's in Core?）

| System | Purpose | Files |
|--------|---------|-------|
| Workspace | Session tracking, journals | `.trellis/workspace/` |
| Tasks | Work item tracking | `.trellis/tasks/` |
| Specs | Coding guidelines | `.trellis/spec/` |
| Commands | Slash command prompts | `.claude/commands/` |
| Scripts | Automation utilities | `.trellis/scripts/` (core subset) |

---

## 为何可移植（Why These Are Portable）

所有核心系统都是**基于文件**的：
- 不需要特殊运行时
- 任何工具都可读写
- 适用于任何 AI 编程环境

```
┌─────────────────────────────────────────────────────────────┐
│                    CORE SYSTEMS (File-Based)                 │
│                                                              │
│  .trellis/                                                   │
│  ├── workspace/     → Journals, session history              │
│  ├── tasks/         → Task directories, PRDs, context files  │
│  ├── spec/          → Coding guidelines                      │
│  └── scripts/       → Python utilities (core subset)         │
│                                                              │
│  .claude/                                                    │
│  └── commands/      → Slash command prompts                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 平台用法（Platform Usage）

### Claude Code
所有核心系统通过 hook 集成自动工作。

### Cursor
会话开始时手动读文件：
1. 读 `.trellis/workflow.md`
2. 从 `.trellis/spec/` 读相关 specs
3. 运行 `python3 .trellis/scripts/task.py current --source` 获取活跃工作
4. 读 JSONL 文件作为上下文

### 其他平台
与 Cursor 相同——手动读文件。

---

## 本目录文档（Documents in This Directory）

| Document | Content |
|----------|---------|
| `files.md` | `.trellis/` 中所有文件及其用途 |
| `workspace.md` | Workspace 系统、journals、开发者身份 |
| `tasks.md` | Task 系统、目录、JSONL 上下文文件 |
| `specs.md` | Spec 系统、指南组织方式 |
| `scripts.md` | 核心脚本（平台无关） |
