<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/first-principles-thinking/references/thinking-models-toolkit.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 思维模型工具箱（Thinking Models Toolkit）

与第一性原理分析互补的心智模型。来源：Reddit「4-Model Prompt」（112 upvotes）与 think-better 的 mental model catalog。

---

## 1. 四象限框架（The Four-Quadrant Framework）

把四个模型合为统一问题分析循环。按象限顺序推进；前一象限输出喂给下一象限。

### 象限 1：第一性原理思考（Strip to fundamentals）

1. 关于这个问题，我们**确定**知道为真的是什么？（只列客观事实。）
2. 我可能在做哪些底层假设？（挑战「显而易见」。）
3. 若无遗留约束、从零建方案，会是什么样？
4. 若忘掉「通常怎么做」，如何重新想象方案？
5. 解决它的绝对最简、最直接版本是什么？

### 象限 2：二阶思维（Second-Order Thinking）

1. 若方案奏效，还会触发什么？（直接次级效应？）
2. 6 个月、2 年、5 年后局面如何？
3. 是否有解了短期痛、却造更大长期问题的风险？
4. 最可能的非预期后果（正或负）是什么？
5. 一个超然、客观的专家会担心什么？

### 象限 3：根因分析（Fix the system, not the symptom）

1. 问题显现时，精确描述哪里出错。（具体症状与触发？）
2. 倒下的第一块多米诺是什么？（初始事件或崩溃？）
3. 做「5 Whys」——从问题陈述开始连问五个「为什么」。
4. 我们以前在哪里试过解却失败？学到什么？
5. 哪些系统性因素让问题反复出现？

### 象限 4：OODA 循环（Bias toward intelligent action）

1. **Observe（观察）**：原始数据是什么？去掉偏见后，此刻实际在发生什么？
2. **Orient（定向）**：需要忘掉哪些心智模型或旧信念才能看清？
3. **Decide（决策）**：综合全部分析，此刻最聪明的单一决策是什么？
4. **Act（行动）**：能立刻跑的最小、最快、最低风险测试是什么？
5. **Urgency（紧迫）**：若必须在 10 分钟内行动，我们会做什么？

### 最终综合模板（Final Synthesis Template）

四象限都分析完后：

1. **Integrated Insights（整合洞见）** — 把各象限关键发现合成连贯图景。哪里一致？哪里冲突？冲突往往揭示最重要的张力。
2. **Strategic Action Plan（战略行动计划）** — 分步计划须：
   - 对准象限 3 的根因
   - 计入象限 2 的二阶效应
   - 立足象限 1 的第一性原理真相
   - 含象限 4 式的立即测试

---

## 2. 扩展心智模型目录（Extended Mental Models Catalog）

十二个结构化思考模型。每个是一面透镜——没有一个单独完整。

### 1. First Principles（第一性原理）

拆到基本真相，再往上推。

- **关键问题**：「我们确知为真的是什么？」
- **何时用**：新举措、挑战「一直这么做」、评估供应商话术。
- **示例**：SpaceX 不问「怎么买更便宜的火箭？」而问「火箭由什么构成，原材料多少钱？」答案约为报价的 2%。

### 2. Inversion（逆向）

不问「如何成功？」，问「什么会保证失败？」然后避开那些。

- **关键问题**：「什么会让这事必败？」
- **何时用**：风险评估、战略复盘、产品设计、招聘决策。
- **示例**：不问「如何建伟大文化？」，问「什么会毁掉文化？」答案：容忍有毒高绩效、价值观执行不一致、无反馈机制。然后预防它们。

### 3. Second-Order Thinking（二阶思维）

发生之后又发生什么？把后果追 2–3 步。

- **关键问题**：「然后呢？」
- **何时用**：政策变更、定价、组织重组、任何有延迟反馈环的决策。
- **示例**：降价 20% 提升量（一阶）。但也吸引更易流失的价格敏感客户、拉低感知价值、建立折扣预期（二阶）。净利可能下降（三阶）。

### 4. Bayesian Updating（贝叶斯更新）

随新证据增量更新信念。不要锚定首条数据，也不要忽略反信号。

- **关键问题**：「给定新证据，信念该移动多少？」
- **何时用**：市场规模、PMF 信号评估、面试后的招聘决策。
- **示例**：你相信流失是价格问题（80% 置信）。三次离职访谈却指向 onboarding 复杂度而非价格。贝叶斯更新：价格问题降到 40%，onboarding 上升。

### 5. Occam's Razor（奥卡姆剃刀）

在同等解释力下，偏好更简单的解释/方案。

- **关键问题**：「更简单的解释是否同样充分？」
- **何时用**：设计评审、调试、选择架构。
- **示例**：bug 更可能是你上周改的代码，而非内核竞态——先查简单解释。

### 6. Via Negativa（否定路径）

通过去掉有害/多余部分来改进，而非不断添加。

- **关键问题**：「我们该去掉什么？」
- **何时用**：简化产品、减负流程、削减范围。
- **示例**：与其加功能提升激活，不如先砍 onboarding 里导致放弃的步骤。

### 7. Pareto Principle（帕累托）

约 80% 结果来自约 20% 原因。

- **关键问题**：「关键少数是什么？」
- **何时用**：优先级、性能优化、客户细分。
- **示例**：多数收入来自少数客户；多数 bug 来自少数模块。

### 8. Leverage Points（杠杆点）

在系统中找小改动能带来大结果的位置。

- **关键问题**：「何处小改动 → 大影响？」
- **何时用**：系统重设计、流程改进、产品策略。
- **示例**：与其在所有步骤加人力，不如在真正瓶颈步骤加自动化。

### 9. Reversibility Filter（可逆性过滤）

区分单向门（难逆）与双向门（易逆），校准决策深度。

- **关键问题**：「这是单向门还是双向门？」
- **何时用**：任何资源承诺决策。
- **示例**：选数据库引擎可能是半单向门；选按钮颜色是双向门——别用同样仪式。

### 10. Pre-Mortem（事前验尸）

假设项目已失败，逆向写失败原因。

- **关键问题**：「12 个月后失败了，为什么？」
- **何时用**：启动前、关键里程碑、当你对方案很兴奋时。
- **示例**：「我们失败是因为低估了数据迁移」——于是把迁移列为第一批风险工作。

### 11. Regret Minimization（遗憾最小化）

从未来回望：哪种选择让长期遗憾最小。

- **关键问题**：「10 年后我会更后悔哪条路？」
- **何时用**：职业、战略方向、大赌注。
- **示例**：Bezos 用「80 岁回望」框架决定是否创办 Amazon。

### 12. Antifragility（反脆弱）

脆弱系统在压力下崩溃；稳健系统勉强撑住；反脆弱系统变强。

- **关键问题**：「压力下这系统变强还是崩？」
- **何时用**：组织设计、基础设施、团队结构、商业模式评估。
- **示例**：只卖一个客户细分的创业公司脆弱；每次流失都改进 ICP 与产品的公司反脆弱——流失压力让业务更锋利。

---

## 3. 模型选型指南（Model Selection Guide）

| Decision Type | Recommended Models | Why This Combination |
|---|---|---|
| What to build | First Principles + Inversion + Via Negativa | Strip to essence, avoid pitfalls, remove unnecessary |
| How to prioritize | Pareto + Leverage Points + Reversibility | Find vital few, maximize impact, classify urgency |
| Is this the right direction | Second-Order + Pre-Mortem + Regret Minimization | Trace consequences, stress-test, long-term perspective |
| What are we missing | 5 Whys + Inversion + Bayesian | Dig deeper, flip perspective, update beliefs |
| Which option to choose | First Principles + Reversibility + Occam's Razor | Ground truth basis, urgency classification, simplicity |
| System is fragile | Antifragility + Via Negativa + Second-Order | Build resilience, remove fragility, trace cascades |

**用法**：从左列决策类型开始，按推荐模型从左到右应用。第一个框定问题，第二个压力测试框定，第三个精炼。

---

## 4. 5 Whys 深潜（5 Whys Deep Dive）

5 Whys 是象限 3（根因分析）的骨干。多数团队做得差。下面是做好的方法。

### 坏的 5 Whys（常见失败）

**问题：周五部署失败。**

1. Why? — Because the build broke.
2. Why? — Because a test failed.
3. Why? — Because the code had a bug.
4. Why? — Because the developer made a mistake.
5. Why? — Because people make mistakes.

**结果**：「人会犯错」不可行动。你到了哲学真理，不是根因。每个「为什么」越来越空时就会这样。

### 好的 5 Whys

**问题：周五部署失败。**

1. Why did the deployment fail? — The integration test for the payments module failed, and the pipeline has a hard gate on that test suite.
2. Why did the payments integration test fail? — It depends on a staging API endpoint that was returning 503 errors.
3. Why was the staging API returning 503s? — The staging environment's database connection pool was exhausted.
4. Why was the connection pool exhausted? — A load test was running against staging at the same time, and there's no isolation between load-test traffic and CI traffic.
5. Why is there no isolation? — Staging was set up as a single shared environment 18 months ago and was never split as the team grew.

**根因：** Shared staging environment with no traffic isolation.
**预防动作：** Create dedicated CI environment separate from load-testing environment. Estimated effort: 2 days. Prevents all future occurrences of this class of failure.

### 有效 5 Whys 规则

- **每个「为什么」必须具体且可证伪。**「因为代码有 bug」不可证伪。「因为 payments 集成测试调用了返回 503 的 staging 端点」具体可验。
- **若「为什么」落到「本来就这样」，你停太早或跑偏了。** 退一步换问法。
- **多原因时分支——别硬拧成一条链。** Why #3 有两个有效答案就跟两条支。真实系统常有多个促成原因。
- **停在你能实际改变的地方。** 根因是你可控范围内最深的因。「互联网不可靠」真但无用。「网络调用无重试逻辑」可行动。
- **根因应指向清晰预防动作。** 若指不出可做的具体变更，继续挖。

### 5 Whys 分支示例

```
Problem: Customer onboarding takes 3 weeks instead of 3 days.

Why? Two branches:

Branch A: Technical setup takes 10 days
  Why? — SSO integration requires manual configuration
  Why? — No self-serve SSO setup exists
  Why? — Engineering deprioritized it (only 5 enterprise customers when decided)
  Root cause: SSO self-serve was never re-prioritized as enterprise grew
  Action: Build SSO self-serve wizard (2 sprints)

Branch B: Legal/procurement takes 12 days
  Why? — Custom contract review on every deal
  Why? — No pre-approved contract template for standard tiers
  Why? — Legal reviews each contract individually
  Root cause: No standardized contract for standard-tier customers
  Action: Create pre-approved template for deals under $50K ARR
```

两条支都是真根因，都需要单独修。硬拧成一条会藏掉其中一条。
