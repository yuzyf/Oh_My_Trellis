> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.claude/skills/trellis-break-loop/SKILL.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

---
name: trellis-break-loop
description: "深度缺陷分析，打破「修了就忘、下次再犯」的循环。分析根因类别、为何修复失败、预防机制，并把知识沉淀进规范。在修完 bug 后使用，以防止同类问题再次发生。"
---

# 打破循环 - 深度缺陷分析（Break the Loop）

调试完成后，用本 skill 做深度分析，打破「修 bug → 遗忘 → 再犯」的循环。

---

## 分析框架（Analysis Framework）

从以下 5 个维度分析你刚修好的 bug：

### 1. 根因类别（Root Cause Category）

这个 bug 属于哪一类？

| 类别 | 特征 | 例子 |
|----------|-----------------|---------|
| **A. 规范缺失（Missing Spec）** | 没有文档说明该怎么做 | 新功能没有检查清单 |
| **B. 跨层契约（Cross-Layer Contract）** | 层间接口不清晰 | API 返回格式与预期不一致 |
| **C. 变更传播失败（Change Propagation Failure）** | 改了一处，漏了别处 | 改了函数签名，漏了调用点 |
| **D. 测试覆盖缺口（Test Coverage Gap）** | 单测过了，集成挂了 | 单独能跑，组合就坏 |
| **E. 隐含假设（Implicit Assumption）** | 代码依赖未文档化的假设 | 时间戳秒 vs 毫秒 |

### 2. 为何修复失败（若适用）

若在成功前试过多次修复，分析每一次失败：

- **表面修复（Surface Fix）**：只修了症状，没动根因
- **范围不全（Incomplete Scope）**：找到了根因，但没覆盖全部情况
- **工具局限（Tool Limitation）**：grep 漏了，类型检查不够严
- **心智模型（Mental Model）**：一直盯同一层，没想到跨层

### 3. 预防机制（Prevention Mechanisms）

什么机制能防止这类问题再次出现？

| 类型 | 机制 | 例子 |
|------|------|------|
| **规范 / 文档** | 检查清单、契约文档 | 在 index 里加 Pre-Development 项 |
| **自动化** | lint 规则、类型约束、CI 门禁 | 禁止危险 API |
| **运行时** | 监控、告警、扫描 | 检测孤儿实体 |
| **测试覆盖** | E2E、集成测试 | 验证完整链路 |
| **代码评审** | 清单、PR 模板 | 「你查过 X 吗？」 |

### 4. 系统性扩展（Systematic Expansion）

这个 bug 暴露了更广的问题吗？

- **类似问题**：别处可能还藏着同样问题吗？
- **设计缺陷**：是否有根本性架构问题？
- **流程缺陷**：开发流程是否需要改进？
- **知识缺口**：团队是否缺某一块理解？

### 5. 知识沉淀（Knowledge Capture）

把洞察固化进系统：

- [ ] 更新 `.trellis/spec/guides/` 思考指南
- [ ] 更新相关 `.trellis/spec/` 文档
- [ ] 创建 issue 记录（若适用）
- [ ] 为根因修复创建功能 ticket
- [ ] 需要时更新检查指南

---

## 输出格式（Output Format）

请按此格式输出分析：

```markdown
## Bug Analysis: [Short Description]

### 1. Root Cause Category
- **Category**: [A/B/C/D/E] - [Category Name]
- **Specific Cause**: [Detailed description]

### 2. Why Fixes Failed (if applicable)
1. [First attempt]: [Why it failed]
2. [Second attempt]: [Why it failed]
...

### 3. Prevention Mechanisms
| Priority | Mechanism | Specific Action | Status |
|----------|-----------|-----------------|--------|
| P0 | ... | ... | TODO/DONE |

### 4. Systematic Expansion
- **Similar Issues**: [List places with similar problems]
- **Design Improvement**: [Architecture-level suggestions]
- **Process Improvement**: [Development process suggestions]

### 5. Knowledge Capture
- [ ] [Documents to update / tickets to create]
```

---

## 核心理念（Core Philosophy）

> **调试的价值不在修好这个 bug，而在于让这类 bug 不再发生。**

三层洞察：
1. **战术（Tactical）**：怎么修 **这个** bug
2. **战略（Strategic）**：怎么防止 **这一类** bug
3. **哲学（Philosophical）**：怎么扩展思维模式

30 分钟分析，省下未来 30 小时调试。

## 思考框架：贝叶斯推理（Bayesian Reasoning）

当多种根因都说得通、证据又不完整时，按新证据成比例更新信念，而不是死抱初始假设。

### 步骤 1：建立先验（Priors）

调查前先写清你相信什么、为什么：

| 假设 | 先验 | 理由 |
|------------|-------|-----------|
| H1: [cause A] | 40% | 该模式最常见 |
| H2: [cause B] | 30% | 结合环境说得通 |
| H3: [other] | 30% | 兜底 |

先验必须合计 100%。若赋不了概率，先调查。

### 步骤 2：观察证据

记录你发现了什么——并写明可靠度：

- 你到底观察到了什么？
- 有多可靠？（测试输出 > 日志 > 用户报告 > 直觉）
- 是否多种假设都能解释它？

### 步骤 3：更新信念

对每个假设问：**若该假设为真，看到这份证据的可能性有多大？**

更新方向比精确计算更重要：
- 证据强烈被 H1 预测 → H1 概率上升
- 证据与 H2 矛盾 → H2 概率下降
- 证据在所有假设下一样可能 → 不更新

### 步骤 4：寻找区分性证据

不要只堆同质证据。找在头部假设之间 **差异很大** 的证据。

> 若 H1 与 H3 接近：「若 H1 为真而 H3 为假，我会看到什么？」然后去查那个。

### 步骤 5：陈述置信度

| 置信度 | 行动 |
|------------|--------|
| 90%+ | 继续修，并监控 |
| 70-90% | 继续，加兜底检查 |
| 50-70% | 提交前先验证假设 |
| <50% | 需要更多证据，别猜 |

证据不完整时不要表达二元确定。用「最可能」「说得通但不大像」「值得查」。

### 常见谬误（Common Fallacies）

| 谬误 | 例子 | 纠正 |
|---------|---------|------------|
| **忽略基础率（Base rate neglect）** | 「测试失败 → 代码坏了」 | 测试因其他原因失败的频率？ |
| **确认偏误（Confirmation bias）** | 「肯定是竞态，我去找竞态证据」 | 主动找 **反对** 你头部假设的证据 |
| **锚定（Anchoring）** | 「上次是缓存，这次大概也是」 | 先验来自当前上下文，不是昨天的 bug |

---

## 分析之后：立刻行动

**重要**：完成上述分析后，你必须立刻：

1. **更新 spec/guides** —— 不要只列 TODO，真正改相关文件：
   - 跨平台问题 → 更新 `cross-platform-thinking-guide.md`
   - 跨层问题 → 更新 `cross-layer-thinking-guide.md`
   - 代码复用问题 → 更新 `code-reuse-thinking-guide.md`
   - 领域相关 → 更新 `backend/*.md` 或 `frontend/*.md`

2. **同步模板** —— 更新 `.trellis/spec/` 后，同步到 `src/templates/markdown/spec/`

3. **提交规范更新** —— 这是主要产出，不只是聊天里的分析文本

> **分析若只留在对话里就没有价值。价值在更新后的规范。**
