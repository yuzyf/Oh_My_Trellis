<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/first-principles-thinking/SKILL.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

---
name: first-principles-thinking
description: >
  面向任意问题域的系统化第一性原理（first principles）思考。当用户说
  "analyze from first principles"、"第一性原理"、"从根本分析"、"从零开始思考"、
  "think from scratch"、"question this design"、"is this the right approach"、
  "challenge assumptions"、"挑战假设"、"为什么要这样做"、"有没有更好的方案"、
  "why are we doing it this way"，或需要在不依赖类比、惯例或「最佳实践」的前提下
  评估决策、设计或策略时使用。也在以下表述时触发：
  "这个设计合理吗"、"从本质上看"、"回到基本面"、"what's really true here"、
  "what are we assuming"，或任何要把问题拆到基本面上的请求。
license: MIT
metadata:
  author: oh-my-openclaw
  version: "1.0"
  composed_from:
    - "awesome-skills/first-principles-skill (GitHub, 11 stars)"
    - "HoangTheQuyen/think-better (GitHub, 41 stars)"
    - "鹅厂架构师 davidycwei — 从第一性原理思考 Agentic Engineering (Zhihu)"
    - "Reddit r/PromptEngineering — 4 Thinking Models Master Prompt (112 upvotes)"
  sources:
    - https://github.com/tt-a1i/first-principles-skill
    - https://github.com/HoangTheQuyen/think-better
    - https://zhuanlan.zhihu.com/p/2010365825916359006
    - https://www.reddit.com/r/PromptEngineering/comments/1ma7f00/
---

# 第一性原理思考（First Principles Thinking）

一套系统方法：把复杂问题拆到不可再分的真相，再自下而上推理——避开类比、惯例或「最佳实践」式推理的陷阱。

## 何时使用（When to Use）

- 评估架构、设计或策略是否真正最优
- 质疑可能不适合当前语境的「最佳实践」
- 常规方案显得不够用、需要破局时
- 做有长期影响的基础性决策
- 挑战遗留系统或遗留思维中继承来的假设
- 主要理由只是「我们一直这么干」的任何时刻

## 何时不要用（When NOT to Use）

- 琐碎决策（改用奥卡姆剃刀 Occam's Razor——选最简单的即可）
- 时间极紧的紧急情况（先行动，后分析）
- 已充分验证、方案成熟的问题（别重复造轮子）
- 既缺领域知识又无法补上时（没有知识的第一性原理 = 幼稚解）

---

## 核心方法：6 个阶段（Core Methodology: 6 Phases）

### 阶段 0：框定问题——建立公理（Phase 0: Frame the Question — Establish Axioms）

在分析任何东西之前，先定义约束该领域的不可再分真相。

**公理（Axioms）** = 可独立验证、无法再拆、违背就必然失败的事实。

**如何识别公理：**
- 问：「还能再拆吗？」——能拆就还不是公理。
- 问：「这是可证明为真，还是只是普遍相信？」——不确定就是假设。
- 问：「违背它是否必然失败？」——「也许」就只是偏好。

**门禁（Gate）**：推进前必须产出 ≥3 条公理。每条一句，并附「为何不可再分」的理由。

```markdown
### Axioms
1. [Axiom] — [Why this cannot be further decomposed]
2. [Axiom] — [Why this is provably true]
3. [Axiom] — [Why violating this causes failure]
```

> 深度方法：`references/axiom-based-reasoning.md`

### 阶段 1：抓住问题本质（Phase 1: Identify the Problem's Essence）

剥掉实现细节，找到核心问题。

1. **把问题说清楚** — 到底要解决什么？
2. **区分症状与原因** — 这是真问题，还是表象？
3. **定义成功标准** — 完美方案会达成什么？（可度量）

**关键问题：**
- 这里真正的 job to be done 是什么？
- 若系统/流程本来不存在，我们真正需要什么？
- 与「怎么实现」无关，什么结果才重要？

**门禁**：必须产出一句话问题陈述 + 可度量的成功标准。

### 阶段 2：浮现并挑战全部假设（Phase 2: Surface and Challenge All Assumptions）

杠杆最高的阶段。多数「最佳实践」其实是伪装成事实的假设。

1. **列出显式假设** — 我们默认成立的是什么？
2. **浮现隐式假设** — 我们不经质疑就在遵循哪些惯例？
3. **用公理检验每一条** — 这真是约束（能追溯到公理），还是「一直这么干」？

**最低要求**：假设表 ≥5 行。

| Assumption | Why Question It | Axiom(s) Used | Verdict |
|------------|----------------|---------------|---------|
| "We need X" | [Challenge] | A1, A2 | Keep / Discard / Modify |

**危险信号（很可能是假假设）：**
- 「我们一直这么干」
- 「行业标准说……」
- 「大家都用 X 做这个」
- 「那太简单了，不可能行」

**深度标准**：每一行都要写清*为何*质疑，以及*哪条公理*支撑裁决。「也许不需要」却没有推理 = 不够深。

**门禁**：≥5 条已挑战的假设且有裁决；每条裁决至少引用一条公理。

> 深度方法：`references/axiom-based-reasoning.md` § "Identify and Challenge Assumptions"

### 阶段 3：确立基本事实（Phase 3: Establish Ground Truths）

在被挑战的假设残骸上，找出对此具体问题不可再分的真。

**基本事实（Ground Truth）检验：**
- 还能再拆吗？→ 能就继续拆。
- 可证明为真，还是只是普遍相信？→ 不确定仍是假设。
- 违背是否必然失败？→ 不是则只是偏好。

**门禁**：≥3 条基本事实。每条必须具体、可证伪——不是空洞真理。

```
❌ "Users need fast response times" (too vague)
✅ "P99 latency must be < 200ms per SLA contract §3.2" (specific, verifiable)

❌ "The team is small" (relative)
✅ "Team is 3 engineers, no new hires possible before Q3" (concrete constraint)
```

### 阶段 4：向上推理（Phase 4: Reason Upward）

只从基本事实搭建方案。每一层都要为自己的存在辩护。

```
Ground Truth → Minimal Solution → Justified Additions → Final Design
     ↑              ↑                    ↑
  (proven)     (sufficient)        (each defended)
```

1. **从最小开始** — 满足全部基本事实的最简东西是什么？
2. **只加必要项** — 每一处添加都要引用基本事实或公理。
3. **挑战每一层** — 这层复杂度是否挣到了存在资格？

**门禁**：产出推理链，每一步都能追溯到基本事实。

```markdown
### Reasoning Chain
GT#1 (latency < 200ms) + GT#3 (3-person team) → Eliminate distributed architecture
GT#2 (read-heavy 95%) + GT#1 → Add read cache with 30s TTL
→ Conclusion: Monolith + in-memory cache
```

### 阶段 5：校验与压力测试（Phase 5: Validate and Stress-Test）

行动前确保推理站得住。

**三个校验问题（完成门禁 Completion Gate）：**

| # | Question | What Failure Means |
|---|---------|-------------------|
| 1 | Can every conclusion trace back to a ground truth? (**Traceability**) | You've introduced unjustified assumptions in Phase 4 |
| 2 | Is every ground truth covered by at least one conclusion? (**Completeness**) | Your solution ignores a constraint — it will fail there |
| 3 | Were any phases skipped or done shallowly? (**Honesty**) | Go back and finish them |

**用互补模型做压力测试：**

| Model | Question to Ask | When It Adds Value |
|-------|----------------|-------------------|
| **Pre-Mortem** | "It's 12 months later and this failed. Why?" | When you're excited about the solution |
| **Second-Order** | "If this works, what happens next? And after that?" | When solution has systemic effects |
| **Inversion** | "What would guarantee failure? Are we doing any of that?" | When you need to find blind spots |
| **OODA Act** | "What's the smallest test we can run right now?" | When analysis paralysis sets in |

> 完整工具箱：`references/thinking-models-toolkit.md`

**门禁**：3 个校验问题均为「是」；至少应用一种压力测试模型。

---

## 推理纪律协议（Reasoning Discipline Protocol）

**问题**：AI 容易跳步、中途分心，或每一步做得很浅。

### 阶段门禁（强制产物 Phase Gates）

| Phase | Must Produce | Min Depth |
|-------|-------------|-----------|
| 0: Frame | ≥3 axioms with justifications | Each axiom: 1 sentence + why irreducible |
| 1: Essence | Problem statement + success criteria | Specific and measurable |
| 2: Assumptions | Assumption table ≥5 rows | Each row: challenge + axiom reference + verdict |
| 3: Ground Truths | ≥3 ground truths | Each: specific, falsifiable, not a truism |
| 4: Reason Up | Reasoning chain with GT references | Every step traces to a GT |
| 5: Validate | 3 validation answers + 1 stress test | All answers = "yes" |

**没有产物 → 不能进入下一阶段。** 门禁未过就停下来补完。

### 进度跟踪器（防漂移 Progress Tracker）

分析全程维护检查清单。每完成一个阶段就输出：

```markdown
## 🧭 FP Progress
- [x] Phase 0: Frame — ✅ 3 axioms
- [x] Phase 1: Essence — ✅ "..."
- [→] Phase 2: Assumptions — 3/6 checked
- [ ] Phase 3: Ground Truths
- [ ] Phase 4: Reason Upward
- [ ] Phase 5: Validate
```

**若对话跑偏**（用户岔开话题、讨论扩到旁支），处理完后立刻输出：

> 📍 Returning to FP analysis: Phase N has M items remaining. Continuing.

### 深度标准（防浅尝 Depth Standards）

| Phase | Shallow (Fail) | Deep (Pass) |
|-------|----------------|-------------|
| Assumptions | "Maybe we don't need this" | Table row with challenge reason + axiom reference + verdict |
| Ground Truths | "Users want fast" | "P99 < 200ms per SLA §3.2" |
| Reasoning | "So we should use X" | "GT#2 + GT#3 → eliminates Y → X is minimal solution" |

---

## Trellis 集成（Trellis Integration）

在 Trellis 管理的项目中，分析产物接入任务系统。

### 文件落位（File Placement）

```
.trellis/tasks/{MM-DD-slug}/
├── task.json              # Existing
├── prd.md                 # Existing — FP feeds into this
├── fp-analysis.md         # ← FP analysis output (Phases 0-5)
├── fp-progress.md         # ← Phase progress tracker (anti-drift)
├── implement.jsonl        # Existing — fp-analysis.md auto-added
├── check.jsonl            # Existing — fp-analysis.md auto-added
└── ...
```

### 与 Brainstorm 集成

在 `/trellis:brainstorm` 中，当任务被归为「Complex」时：

1. **触发**：用户说「从第一性原理分析」，或 AI 发现 ≥3 个未验证假设
2. **执行**：跑阶段 0–3，输出写入任务目录的 `fp-analysis.md`
3. **喂入 PRD**：
   - Ground Truths → PRD Requirements and Constraints
   - Assumption Table → design.md Trade-offs
   - Reasoning Chain → `design.md`
4. **继续**：阶段 4–5 影响实现决策

### 上下文注入（Context Injection）

FP 分析完成后，写入上下文文件：

```bash
python3 ./.trellis/scripts/task.py add-context "$TASK_DIR" implement "fp-analysis.md" "Ground truths and reasoning chain"
python3 ./.trellis/scripts/task.py add-context "$TASK_DIR" check "fp-analysis.md" "Verify implementation traces to ground truths"
```

### 完成记录（Completion Recording）

阶段 5 后更新 `task.json`：

```json
{
  "fp_analysis": {
    "completed": true,
    "axioms_count": 3,
    "assumptions_challenged": 6,
    "ground_truths_count": 5,
    "validation_passed": true
  }
}
```

---

## 输出格式（Output Format）

应用第一性原理思考时，最终输出结构如下：

```markdown
## First Principles Analysis: [Topic]

### Axioms
1. [Axiom 1] — [Why irreducible]
2. [Axiom 2] — [Why irreducible]
3. [Axiom 3] — [Why irreducible]

### Problem Essence
**Core problem:** [One sentence]
**Success criteria:** [Measurable outcomes]

### Assumptions Challenged
| Assumption | Challenge | Axiom(s) | Verdict |
|------------|-----------|----------|---------|
| ... | ... | A1, A2 | Keep/Discard/Modify |

### Ground Truths
1. [Specific, falsifiable fact]
2. [Specific, falsifiable fact]
3. [Specific, falsifiable fact]

### Reasoning Chain
GT#1 + GT#3 → [Inference] → [Step] → [Conclusion]

### Conclusion
**Recommended approach:** [Description]
**Key insight:** [What FP analysis revealed that convention missed]
**Trade-offs acknowledged:** [What we accept and why]

### Validation
- [x] Every conclusion traces to a ground truth
- [x] Every ground truth is covered
- [x] No phases skipped
- [x] Stress-tested with: [model name]
```

---

## 常见陷阱（Common Traps）

### 复杂度陷阱（The Complexity Trap）
**症状**：方案比问题该有的复杂度更高。
**FP 检查**：去掉一个组件——是否仍解决核心问题？是则该组件非必要。重复。

### 类比陷阱（The Analogy Trap）
**症状**：「公司 X 这么做，我们也该这么做。」
**FP 检查**：X 当时解决什么问题？我们的问题在相关维度上是否相同？约束哪里不同？

### 遗留陷阱（The Legacy Trap）
**症状**：为已不再服务我们的决策继续兼容。
**FP 检查**：当初理由是什么？那些条件还在吗？变更真实成本 vs 维持成本？

> 更多模式与案例：`references/case-studies.md`

---

## 互补工具速查（Complementary Tools Quick Reference）

| Tool | Key Question | Best Combined With Phase |
|------|-------------|------------------------|
| **Inversion** | "What guarantees failure?" | Phase 2 (find hidden assumptions) |
| **Second-Order** | "Then what? And then?" | Phase 5 (stress-test conclusions) |
| **5 Whys** | "Why? Why? Why? Why? Why?" | Phase 1 (find real problem) |
| **Pre-Mortem** | "It failed. Why?" | Phase 5 (stress-test) |
| **OODA Loop** | "What's the smallest test?" | Phase 5 (move to action) |
| **Via Negativa** | "What should we remove?" | Phase 4 (simplify solution) |
| **Bayesian Update** | "What new evidence changes this?" | Phase 3 (validate ground truths) |
| **Reversibility Filter** | "One-way or two-way door?" | Phase 4 (calibrate decision depth) |

> 完整工具箱与示例：`references/thinking-models-toolkit.md`

---

## 偏见意识（Bias Awareness）

对第一性原理分析最危险的 5 种偏见：

| Bias | How It Corrupts FP | Quick Debias |
|------|-------------------|-------------|
| **Confirmation** | You "find" ground truths that confirm your preferred solution | Seek disconfirming evidence first |
| **Anchoring** | Conventional approach becomes mental anchor even when thinking "fresh" | Generate 3 alternatives before evaluating |
| **Sunk Cost** | Legacy decisions feel like ground truths | "If starting from zero today, would we choose this?" |
| **Status Quo** | "How it works now" feels like a constraint when it's a choice | Separate true constraints from current choices |
| **Overconfidence** | Treat assumptions as ground truths without testing | Assign confidence % to each assumption |

> 完整 12 种偏见与去偏：`references/bias-and-debiasing.md`

---

## 问题分解（Problem Decomposition）

对复杂问题做 FP 前，可能需要先分解。快速选型：

| Problem Type | Best Framework |
|-------------|---------------|
| Diagnostic (why is X happening?) | Issue Tree or Fishbone |
| Financial (revenue/cost) | Profitability Tree |
| Strategic (what should we do?) | Hypothesis Tree |
| Operational (what's broken?) | Process Flow + 5 Whys |
| Complex adaptive system | Systems Map |

> 完整 15 框架目录：`references/decomposition-frameworks.md`

---

## 参考文件（Reference Files）

| File | Content | When to Read |
|------|---------|-------------|
| `references/axiom-based-reasoning.md` | Deep methodology for establishing axioms, challenging assumptions, and deriving conclusions | When you need rigorous derivation, not just analysis |
| `references/thinking-models-toolkit.md` | 4-quadrant framework + 12 mental models + model selection guide + 5 Whys deep dive | When you need complementary thinking tools |
| `references/case-studies.md` | 5 software engineering cases + 2 SpaceX/Tesla cases + templates | When you want concrete examples of FP in action |
| `references/bias-and-debiasing.md` | 12 cognitive biases that corrupt FP thinking + debiasing strategies | When validating your analysis for blind spots |
| `references/decomposition-frameworks.md` | 15 problem decomposition methods (MECE, Issue Tree, etc.) | When the problem is too big to analyze directly |
