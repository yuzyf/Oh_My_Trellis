<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/how-to-modify/add-spec.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# How To: 添加 Spec 分类

添加如 `mobile/` 这样的新 spec 分类。

**Platform**：All

---

## 要修改的文件（Files to Modify）

| File | Action | Required |
|------|--------|----------|
| `.trellis/spec/mobile/index.md` | Create | Yes |
| `.trellis/spec/mobile/*.md` | Create | Yes |
| Task JSONL templates | Update | Yes |
| `trellis-local/SKILL.md` | Update | Yes |

---

## Step 1: 创建分类目录

```bash
mkdir -p .trellis/spec/mobile
```

---

## Step 2: 创建 Index 文件

创建 `.trellis/spec/mobile/index.md`：

```markdown
# Mobile Specifications

Guidelines for mobile development.

## Quick Reference

| Topic | Guideline |
|-------|-----------|
| Architecture | MVVM pattern |
| State | Use StateFlow |
| Navigation | Jetpack Navigation |

## Specifications

1. [Architecture Guidelines](./architecture.md)
2. [UI Guidelines](./ui-guidelines.md)
3. [State Management](./state-management.md)

## Key Principles

- Principle 1
- Principle 2
- Principle 3
```

---

## Step 3: 创建 Spec 文件

在分类下创建各条 spec 文件：

### 示例：`architecture.md`

```markdown
# Mobile Architecture

## Overview

Description of architecture approach.

## Guidelines

### 1. Use MVVM Pattern

Explanation...

**Do:**
```kotlin
// Good example
```

**Don't:**
```kotlin
// Bad example
```

### 2. Another Guideline

...

## Related Specs

- [UI Guidelines](./ui-guidelines.md)
```

---

## Step 4: 更新 JSONL 模板

把新 specs 加入相关 JSONL 模板。

### 选项 A：更新 task.py

修改 `init-context` 以包含 mobile specs：

```python
def init_mobile_context(task_dir):
    jsonl_path = os.path.join(task_dir, "implement.jsonl")
    with open(jsonl_path, "a") as f:
        f.write(json.dumps({
            "file": ".trellis/spec/mobile/index.md",
            "reason": "Mobile guidelines"
        }) + "\n")
```

### 选项 B：加入现有模板

编辑现有 JSONL 文件：

```jsonl
{"file": ".trellis/spec/mobile/index.md", "reason": "Mobile guidelines"}
{"file": ".trellis/spec/mobile/architecture.md", "reason": "Architecture patterns"}
```

---

## Step 5: 在 trellis-local 中记录

更新 `.claude/skills/trellis-local/SKILL.md`：

```markdown
## Specs Customized

### Added Categories

#### mobile/
- **Path**: `.trellis/spec/mobile/`
- **Purpose**: Mobile development guidelines
- **Added**: 2026-01-31
- **Files**:
  - `index.md` - Overview
  - `architecture.md` - Architecture patterns
  - `ui-guidelines.md` - UI patterns
```

---

## Spec 文件最佳实践（Spec File Best Practices）

### 结构

```markdown
# [Spec Title]

## Overview
Brief description.

## Guidelines

### 1. [Guideline Name]
Explanation with examples.

### 2. [Another Guideline]
...

## Related Specs
Links to related specs.
```

### 命名

- 使用 kebab-case：`ui-guidelines.md`
- 描述性：`state-management.md` 而不是 `state.md`

### 交叉引用

在 specs 之间链接：

```markdown
See [State Management](./state-management.md) for more details.
```

---

## 测试（Testing）

1. 验证 index 链接可用
2. 创建 JSONL 含新 specs 的任务
3. 验证 specs 注入正确（Claude Code）
4. 验证 specs 可读（Cursor）

---

## 检查清单（Checklist）

- [ ] 分类目录已创建
- [ ] Index 文件已创建并含总览
- [ ] Spec 文件已按正确格式创建
- [ ] JSONL 模板已更新
- [ ] 已在 trellis-local 记录
- [ ] 交叉引用已验证
