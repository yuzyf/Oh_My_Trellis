<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/core/specs.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# Spec 系统（Spec System）

维护引导 AI 开发的编码标准。

---

## 目录结构（Directory Structure）

```
.trellis/spec/
├── cli/                        # Per-package specs (e.g. packages/cli/)
│   ├── frontend/               # Frontend guidelines
│   │   ├── index.md
│   │   ├── component-guidelines.md
│   │   ├── hook-guidelines.md
│   │   ├── state-management.md
│   │   └── ...
│   │
│   ├── backend/                # Backend guidelines
│   │   ├── index.md
│   │   ├── directory-structure.md
│   │   ├── error-handling.md
│   │   ├── api-patterns.md
│   │   └── ...
│   │
│   └── unit-test/              # Unit test guidelines
│       ├── index.md
│       └── ...
│
└── guides/                     # Thinking guides (cross-package)
    ├── index.md
    ├── cross-layer-thinking-guide.md
    ├── code-reuse-thinking-guide.md
    └── cross-platform-thinking-guide.md
```

---

## Spec 分类（Spec Categories）

### Frontend（`cli/frontend/`）

UI 与客户端模式：
- Component structure
- React hooks usage
- State management
- Styling conventions
- Accessibility

### Backend（`cli/backend/`）

服务端模式：
- Directory structure
- API design
- Error handling
- Database access
- Security

### Guides（`guides/`）

横切思考指南：
- 如何思考跨层变更
- 代码复用策略
- 平台考量

---

## Index 文件（Index Files）

每个分类都有 `index.md`，用于：
1. 提供分类总览
2. 列出该分类下所有 specs
3. 给出常见模式的快速参考

### 示例：`frontend/index.md`

```markdown
# Frontend Specifications

## Quick Reference

| Topic | Guideline |
|-------|-----------|
| Components | Functional components only |
| State | Use React Query for server state |
| Styling | Tailwind CSS |

## Specifications

1. [Component Guidelines](./component-guidelines.md)
2. [Hook Guidelines](./hook-guidelines.md)
3. [State Management](./state-management.md)
```

---

## Spec 文件格式（Spec File Format）

```markdown
# [Spec Title]

## Overview
Brief description of what this spec covers.

## Guidelines

### 1. [Guideline Name]
Detailed explanation...

**Do:**
```typescript
// Good example
```

**Don't:**
```typescript
// Bad example
```

### 2. [Another Guideline]
...

## Related Specs
- [Related Spec 1](./related-spec.md)
```

---

## 使用 Specs（Using Specs）

### 在 JSONL 上下文文件中

在任务上下文中引用 specs：

```jsonl
{"file": ".trellis/spec/cli/frontend/index.md", "reason": "Frontend overview"}
{"file": ".trellis/spec/cli/frontend/component-guidelines.md", "reason": "Component patterns"}
```

### 手动阅读（Cursor）

会话开始时读 specs：
```
1. Read .trellis/spec/{category}/index.md
2. Read specific guidelines as needed
3. Follow patterns in your code
```

---

## 创建新 Specs（Creating New Specs）

### 1. 选择分类

- Frontend UI 模式 → `frontend/`
- Backend/API 模式 → `backend/`
- 横切指南 → `guides/`

### 2. 创建 Spec 文件

```bash
touch .trellis/spec/cli/frontend/new-pattern.md
```

### 3. 遵循格式

使用上面的 spec 文件格式。

### 4. 更新 Index

加入分类的 `index.md`：

```markdown
## Specifications
...
N. [New Pattern](./new-pattern.md)
```

### 5. 在 JSONL 中引用

加入相关任务上下文文件。

---

## 增加新分类（Adding New Categories）

### 1. 创建目录

```bash
mkdir .trellis/spec/mobile
```

### 2. 创建 Index

```bash
touch .trellis/spec/mobile/index.md
```

### 3. 添加分类 Specs

创建各条 spec 文件。

### 4. 更新任务模板

确保新分类在 JSONL 模板中可用。

---

## 最佳实践（Best Practices）

1. **保持 specs 聚焦** - 一文件一主题
2. **使用示例** - 展示 do/don't 模式
3. **链接相关 specs** - 交叉引用
4. **定期更新** - Specs 随代码库演进
5. **全部编入 index** - 保持 index 文件最新
