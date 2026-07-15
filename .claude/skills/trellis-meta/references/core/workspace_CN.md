<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/core/workspace.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# Workspace 系统（Workspace System）

跨会话跟踪开发进度，并按开发者隔离。

---

## 目录结构（Directory Structure）

```
.trellis/workspace/
├── index.md                    # Global overview
└── {developer}/                # Per-developer directory
    ├── index.md                # Personal index with @@@auto markers
    ├── journal-1.md            # Session journal (max 2000 lines)
    ├── journal-2.md            # Rolls over when limit reached
    └── ...
```

---

## 开发者身份（Developer Identity）

### `.trellis/.developer`

存储当前开发者名。由 `init_developer.py` 创建。

```
taosu
```

### 初始化开发者（Initialize Developer）

```bash
python3 .trellis/scripts/init_developer.py <name>
```

创建：
- `.trellis/.developer` - 身份文件
- `.trellis/workspace/<name>/` - 个人 workspace
- `.trellis/workspace/<name>/index.md` - 个人索引
- `.trellis/workspace/<name>/journal-1.md` - 第一份 journal

---

## Journals

### 用途（Purpose）

跟踪会话历史、决策与上下文。

### 格式（Format）

```markdown
# Journal 1

## Session: 2026-01-31 10:30

### Context
- Working on: [task description]
- Branch: feature/add-login

### Progress
- [x] Completed step 1
- [ ] Working on step 2

### Notes
Key decisions and learnings...

---
```

### Journal 轮转（Journal Rotation）

当 journal 超过 2000 行时：
1. 归档当前内容（追加到 index）
2. 创建新的 journal-N.md
3. 继续写入

---

## 个人索引（Personal Index）

### `workspace/{developer}/index.md`

跟踪所有会话并提供快速参考。

```markdown
# Developer Workspace - taosu

## Active Work
- Current task: `.trellis/tasks/01-31-add-login-taosu`
- Branch: feature/add-login

## Recent Sessions
<!-- @@@auto-sessions-start -->
- 2026-01-31: Implemented login UI
- 2026-01-30: Set up auth service
<!-- @@@auto-sessions-end -->

## Journals
- journal-1.md (lines 1-2000)
- journal-2.md (current)
```

### @@@auto 标记（@@@auto Markers）

脚本用这些标记自动更新段落：
- `@@@auto-sessions-start/end` - 最近会话列表
- `@@@auto-tasks-start/end` - 任务摘要

---

## 全局索引（Global Index）

### `workspace/index.md`

所有开发者与项目状态总览。

```markdown
# Project Workspace

## Developers
- taosu - Last active: 2026-01-31
- cursor-agent - Last active: 2026-01-30

## Recent Activity
...
```

---

## 脚本（Scripts）

| Script | Purpose |
|--------|---------|
| `init_developer.py` | 初始化开发者身份 |
| `get_developer.py` | 获取当前开发者名 |
| `add_session.py` | 将会话记入 journal |
| `get_context.py` | 获取给 AI 的会话上下文 |

---

## 最佳实践（Best Practices）

1. **一台机器一个开发者** - 身份存在 `.developer`
2. **定期写 journal** - 记录决策与上下文
3. **使用 markers** - 让脚本自动更新 indexes
4. **回顾 journals** - 开始新会话前阅读
