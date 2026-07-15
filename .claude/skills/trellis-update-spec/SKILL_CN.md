> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.claude/skills/trellis-update-spec/SKILL.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

---
name: trellis-update-spec
description: "把可执行契约与编码约定沉淀进 .trellis/spec/ 文档。在调试、实现或讨论中学到值得保留给未来会话的内容时使用。"
---

# 更新 Code-Spec - 沉淀可执行契约（Update Code-Spec）

当你学到有价值的东西（来自调试、实现或讨论）时，用本 skill 更新相关 code-spec 文档。

**时机**：完成任务、修好 bug，或发现新模式之后

---

## Code-Spec 优先规则（CRITICAL）

在本项目中，实现工作所说的 “spec” 指的是 **code-spec**：
- 可执行契约（不只是原则性文字）
- 具体签名、payload 字段、环境变量键、边界行为
- 可测试的校验/错误行为

若改动触及基础设施或跨层契约，code-spec 深度是强制的。

### 强制触发条件（Mandatory Triggers）

出现以下任一情况时，应用 code-spec 深度：
- 新增/变更命令或 API 签名
- 跨层 request/response 契约变更
- 数据库 schema/迁移变更
- 基础设施集成（storage、queue、cache、secrets、env 接线）

### 强制输出（7 节）

对触发任务，须包含以下全部小节：
1. Scope / Trigger
2. Signatures (command/API/DB)
3. Contracts (request/response/env)
4. Validation & Error Matrix
5. Good/Base/Bad Cases
6. Tests Required (with assertion points)
7. Wrong vs Correct (at least one pair)

---

## 何时更新 Code-Specs

| 触发 | 例子 | 目标规范 |
|---------|---------|-------------|
| **实现了功能** | 加了新集成或模块 | 相关 spec 文件 |
| **做了设计决策** | 选了可扩展模式而非极简 | 相关 spec + "Design Decisions" 节 |
| **修了 bug** | 发现错误处理里的隐蔽问题 | 相关 spec（如 error-handling 文档） |
| **发现了模式** | 找到更好的代码结构方式 | 相关 spec 文件 |
| **踩了坑** | 学到必须先做 X 再做 Y | 相关 spec + "Common Mistakes" 节 |
| **确立了约定** | 团队就命名模式达成一致 | 质量指南 |
| **新的思考触发器** | 「做 Y 前别忘了查 X」 | `guides/*.md`（作为检查项） |

**关键洞察**：Code-spec 更新不只为了问题。每次功能实现都包含设计决策与契约，未来的 AI/开发者需要它们才能安全执行。

---

## 规范结构总览（Spec Structure Overview）

```
.trellis/spec/
├── <layer>/           # Per-layer coding standards (e.g., backend/, frontend/, api/)
│   ├── index.md       # Overview and links
│   └── *.md           # Topic-specific guidelines
└── guides/            # Thinking checklists (NOT coding specs!)
    ├── index.md       # Guide index
    └── *.md           # Topic-specific guides
```

### 关键：Code-Spec vs Guide —— 分清差别

| 类型 | 位置 | 目的 | 内容风格 |
|------|----------|---------|---------------|
| **Code-Spec** | `<layer>/*.md` | 告诉 AI「如何安全实现」 | 签名、契约、矩阵、用例、测试点 |
| **Guide** | `guides/*.md` | 帮助 AI「写之前要想什么」 | 清单、问题、指向 specs 的指针 |

**决策规则**：问自己：

- 「这是 **怎么写** 代码」→ 放进某个 spec 层目录
- 「这是写之前 **要考虑什么**」→ 放进 `guides/`

**例子**：

| 所学 | 错误位置 | 正确位置 |
|----------|----------------|------------------|
| 「这个任务用 API X 不要用 API Y」 | ❌ `guides/`（对思考指南太具体） | ✅ 相关 spec 文件（具体约定） |
| 「做 Y 时记得检查 X」 | ❌ Spec 文件（对 spec 太抽象） | ✅ `guides/`（思考清单） |

**Guides 应是指向 specs 的短清单**，不要复制详细规则。

---

## 更新流程（Update Process）

### 步骤 1：识别你学到了什么

回答这些问题：

1. **你学到了什么？**（要具体）
2. **为什么重要？**（它防止什么问题？）
3. **它属于哪里？**（哪个 spec 文件？）

### 步骤 2：分类更新类型

| 类型 | 说明 | 动作 |
|------|-------------|--------|
| **Design Decision** | 为什么选方案 X 而不是 Y | 加入 "Design Decisions" 节 |
| **Project Convention** | 本项目怎么做 X | 加入相关节并带例子 |
| **New Pattern** | 发现的可复用做法 | 加入 "Patterns" 节 |
| **Forbidden Pattern** | 会惹麻烦的做法 | 加入 "Anti-patterns" 或 "Don't" 节 |
| **Common Mistake** | 容易犯的错 | 加入 "Common Mistakes" 节 |
| **Convention** | 已达成一致的标准 | 加入相关节 |
| **Gotcha** | 不显然的行为 | 加入 warning 提示块 |

### 步骤 3：阅读目标 Code-Spec

编辑前先读当前 code-spec，以便：
- 理解既有结构
- 避免重复内容
- 找到更新的正确小节

### 步骤 4：进行更新

遵循这些原则：

1. **要具体**：给具体例子，不要只有抽象规则
2. **解释为什么**：写明它防止的问题
3. **展示契约**：补签名、payload 字段、错误行为
4. **展示代码**：关键模式加代码片段
5. **保持简短**：每节一个概念

### 步骤 5：更新索引（若需要）

若你加了新小节，或 code-spec 状态变了，更新该类别的 `index.md`。

---

## 更新模板（Update Templates）

### 基础设施 / 跨层工作的强制模板

```markdown
## Scenario: <name>

### 1. Scope / Trigger
- Trigger: <why this requires code-spec depth>

### 2. Signatures
- Backend command/API/DB signature(s)

### 3. Contracts
- Request fields (name, type, constraints)
- Response fields (name, type, constraints)
- Environment keys (required/optional)

### 4. Validation & Error Matrix
- <condition> -> <error>

### 5. Good/Base/Bad Cases
- Good: ...
- Base: ...
- Bad: ...

### 6. Tests Required
- Unit/Integration/E2E with assertion points

### 7. Wrong vs Correct
#### Wrong
...
#### Correct
...
```

### 添加设计决策

```markdown
### Design Decision: [Decision Name]

**Context**: What problem were we solving?

**Options Considered**:
1. Option A - brief description
2. Option B - brief description

**Decision**: We chose Option X because...

**Example**:
\`\`\`typescript
// How it's implemented
code example
\`\`\`

**Extensibility**: How to extend this in the future...
```

### 添加项目约定

```markdown
### Convention: [Convention Name]

**What**: Brief description of the convention.

**Why**: Why we do it this way in this project.

**Example**:
\`\`\`typescript
// How to follow this convention
code example
\`\`\`

**Related**: Links to related conventions or specs.
```

### 添加新模式

```markdown
### Pattern Name

**Problem**: What problem does this solve?

**Solution**: Brief description of the approach.

**Example**:
\`\`\`
// Good
code example

// Bad
code example
\`\`\`

**Why**: Explanation of why this works better.
```

### 添加禁止模式

```markdown
### Don't: Pattern Name

**Problem**:
\`\`\`
// Don't do this
bad code example
\`\`\`

**Why it's bad**: Explanation of the issue.

**Instead**:
\`\`\`
// Do this instead
good code example
\`\`\`
```

### 添加常见错误

```markdown
### Common Mistake: Description

**Symptom**: What goes wrong

**Cause**: Why this happens

**Fix**: How to correct it

**Prevention**: How to avoid it in the future
```

### 添加 Gotcha

```markdown
> **Warning**: Brief description of the non-obvious behavior.
>
> Details about when this happens and how to handle it.
```

---

## 交互模式（Interactive Mode）

若不确定更新什么，回答这些提示：

1. **你刚完成了什么？**
   - [ ] 修了 bug
   - [ ] 实现了功能
   - [ ] 重构了代码
   - [ ] 讨论了方案

2. **你学到或决定了什么？**
   - 设计决策（为什么选 X 不选 Y）
   - 项目约定（我们怎么做 X）
   - 不显然的行为（gotcha）
   - 更好的做法（pattern）

3. **未来的 AI/开发者需要知道吗？**
   - 为理解代码如何工作 → 是，更新 spec
   - 为维护或扩展功能 → 是，更新 spec
   - 为避免重复犯错 → 是，更新 spec
   - 纯一次性实现细节 → 或许跳过

4. **它关联哪个领域？**
   - [ ] Backend 代码
   - [ ] Frontend 代码
   - [ ] 跨层数据流
   - [ ] 代码组织/复用
   - [ ] 质量/测试

---

## 质量清单（Quality Checklist）

结束 code-spec 更新前：

- [ ] 内容是否具体且可执行？
- [ ] 是否包含代码示例？
- [ ] 是否解释了 WHY，而不只是 WHAT？
- [ ] 是否包含可执行签名/契约？
- [ ] 是否包含校验与错误矩阵？
- [ ] 是否包含 Good/Base/Bad 用例？
- [ ] 是否包含带断言点的必要测试？
- [ ] 是否在正确的 code-spec 文件里？
- [ ] 是否与既有内容重复？
- [ ] 新成员能否看懂？

---

## 与其他命令的关系

```
Development Flow:
  Learn something → /trellis:update-spec → Knowledge captured
       ↑                                  ↓
  /trellis:break-loop ←──────────────────── Future sessions benefit
  (deep bug analysis)
```

- `/trellis:break-loop` - 深度分析 bug，常揭示需要更新的 spec
- `/trellis:update-spec` - 真正执行更新
- `/trellis:finish-work` - 提醒你检查 specs 是否需要更新

---

## 核心理念（Core Philosophy）

> **Code-specs 是活文档。每一次调试、每一个「啊哈」时刻，都是让实现契约更清晰的机会。**

目标是 **机构记忆（institutional memory）**：
- 一个人学到的，所有人受益
- AI 在一次会话中学到的，会留到未来会话
- 错误变成文档化的护栏
