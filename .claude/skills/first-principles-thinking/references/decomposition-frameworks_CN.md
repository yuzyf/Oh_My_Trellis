<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/first-principles-thinking/references/decomposition-frameworks.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 问题分解框架（Problem Decomposition Frameworks）

在对问题做第一性原理之前，常常需要先拆成可管理的块。缠成一团的复杂问题会抵抗 FP 推理——你隔离不了基本事实，一切都互相牵连、令人窒息。下面 15 个框架提供结构化拆解方式，让第一性原理有具体对象可抓。

先选匹配问题类型的框架，先分解，再对每一块做第一性原理推理。

来源：think-better 项目的 problem-solving-pro skill。

---

### Issue Tree（议题树）
**是什么**：把宽问题拆成子问题树，每一层 MECE（Mutually Exclusive, Collectively Exhaustive：相互独立、完全穷尽）。
**何时用**：诊断类——找根因或映射决策空间。
**结构**：
```
Why is revenue declining?
├── Are we losing customers?
│   ├── Is churn increasing?
│   └── Are we acquiring fewer?
└── Are customers spending less?
    ├── Is average deal size shrinking?
    └── Is expansion revenue declining?
```
**示例**：「为何 NPS 掉了 15 点？」可分支到产品质量、支持响应时间、onboarding 体验、价格感知——各自独立探索。

### Hypothesis Tree（假设树）
**是什么**：从一个假设出发，拆成该假设成立时必须全部为真的条件。
**何时用**：原因不确定、你怀疑答案但需要系统验证。
**结构**：
```
Hypothesis: We should enter the EU market
├── Condition 1: Sufficient demand exists (>$50M TAM)
├── Condition 2: We can comply with GDPR at reasonable cost
├── Condition 3: We can hire or partner locally
└── Condition 4: Unit economics work with EU pricing
```
**示例**：「产品市场契合在变弱」——拆成留存、激活、推荐、支付意愿等条件，分别测试。

### MECE Decomposition（MECE 分解）
**是什么**：把集合分成不重叠（Mutually Exclusive）且覆盖全部（Collectively Exhaustive）的类别。
**何时用**：任何需要完整、不重复计数的通用结构原则。
**结构**：用两个问题检验：(1) 有没有落入两类？(2) 有没有漏掉？任一为是则重构。
**示例**：按合同金额分段客户（SMB < $50K，Mid-Market $50K–$250K，Enterprise > $250K）——每位客户恰好一桶。

### Profitability Tree（盈利树）
**是什么**：利润 = 收入（价格 × 量）− 成本（固定 + 可变）。
**何时用**：财务分析、毛利诊断、定价决策，或理解盈利为何变化。
**结构**：
```
Profit
├── Revenue
│   ├── Price per unit
│   └── Volume (units sold)
│       ├── New customers
│       └── Existing customers (expansion)
└── Costs
    ├── Fixed (rent, salaries, infrastructure)
    └── Variable (COGS, commissions, hosting per user)
```
**示例**：「毛利率掉 8 个点」——树很快隔离是定价、量结构还是成本上升。

### Process Flow Decomposition（流程分解）
**是什么**：把流程映射为顺序步骤，度量每步，找瓶颈。
**何时用**：运营问题——工作经阶段流动且某处慢、坏或不一致。
**结构**：`Step 1 → Step 2 → Step 3 → ... → Output`，每步量时间、错误率、吞吐。
**示例**：Lead-to-close：Inbound → Qualification (2 days) → Demo (5 days) → Proposal (3 days) → Negotiation (14 days) → Close。14 天谈判是瓶颈。

### Customer Journey Map（客户旅程图）
**是什么**：映射客户从首次认知到倡导的每一个触点。
**何时用**：体验问题、激活问题、流失诊断或 onboarding 重设计。
**结构**：`Awareness → Consideration → Trial → Purchase → Onboarding → Usage → Expansion → Advocacy`——每阶段映射：客户做什么、感受如何、卡在哪。
**示例**：SaaS 试用旅程显示 60% 用户在注册与第一次有意义动作之间流失，因为 onboarding 向导要的数据他们还没有。

### Value Chain Analysis（价值链分析）
**是什么**：按增值活动（入站物流、运营、出站、营销/销售、服务）与支持活动（基础设施、HR、技术、采购）拆业务。
**何时用**：竞争优势分析——理解哪里创造独特价值、哪里商品化。
**结构**：Porter 价值链：主活动（左到右）由上方支持活动支撑。
**示例**：发现「客户成功」是独特价值点，而「发票」完全商品化——外包发票、投资 CS。

### Systems Map（系统图）
**是什么**：画出组件、反馈环、延迟与杠杆点，而不是线性因果。
**何时用**：复杂自适应系统——行为涌现、有意想不到的副作用。
**结构**：节点 + 箭头（强化环 R、平衡环 B），标延迟。
**示例**：招聘加速 → 入职负担 ↑ → 质量 ↓ → 人员流失 ↑ → 再招聘——强化负环。

### Stakeholder Map（干系人图）
**是什么**：按权力/利益（或影响/态度）定位人与群体。
**何时用**：组织/政治问题——变革阻力、跨团队协调、采购。
**结构**：2×2：高/低权力 × 高/低利益；或影响地图。
**示例**：迁移项目：工程（高权力高利益）是驱动者；法务（高权力低日常利益）是潜在阻断者。

### Scenario Tree（情景树）
**是什么**：按关键不确定性分支可能未来，形成可对照规划的情景。
**何时用**：不确定下的规划——正确策略取决于哪条未来成真。
**结构**：
```
Key uncertainty: Market grows fast vs. slow
├── Fast growth
│   ├── We execute well → "Blue Ocean"
│   └── We stumble → "Missed Window"
└── Slow growth
    ├── We execute well → "Efficient Machine"
    └── We stumble → "Survival Mode"
```
**示例**：AI 创业公司对监管（严 vs 松）× 基础模型商品化（快 vs 慢）建模，决定 build-vs-buy。

### Feature Tree（功能树）
**是什么**：把产品拆成功能、能力与子能力的层次。
**何时用**：产品决策——路线图优先级、build-vs-buy、竞争缺口。
**结构**：
```
Product
├── Core capability A
│   ├── Feature A1
│   └── Feature A2
├── Core capability B
│   ├── Feature B1
│   └── Feature B2
└── Platform / Infrastructure
    ├── Feature P1
    └── Feature P2
```
**示例**：项目管理工具拆成任务管理、协作、报表、集成——再对竞品打分找缺口。

### Technology Stack Decomposition（技术栈分解）
**是什么**：按基础设施、平台、应用、接口分层。
**何时用**：技术架构决策、迁移规划或性能诊断。
**结构**：
```
Interface Layer    (UI, API, CLI)
Application Layer  (business logic, services)
Platform Layer     (databases, queues, auth, storage)
Infrastructure     (compute, network, CDN, DNS)
```
**示例**：API 延迟——按层分解度量。发现应用层快，平台层数据库查询全表扫描。

### Fishbone / Ishikawa Diagram（鱼骨图）
**是什么**：把潜在原因归入标准组：People、Process、Technology、Environment、Materials、Measurement。
**何时用**：根因分析——问题已发生，需系统识别所有可能原因。
**结构**：
```
                People ──────┐
               Process ──────┤
            Technology ──────┼──→ [Problem]
           Environment ──────┤
           Measurement ──────┘
```
**示例**：「为何部署失败？」——People（新工程师、无结对）、Process（无 staging）、Technology（不稳 CI）、Environment（第三方 API 限流）。

### Pyramid Principle（金字塔原理）
**是什么**：沟通结构为先答、再论据、再论据下的证据。
**何时用**：沟通与决策——需要向干系人清晰呈现推理。
**结构**：
```
Answer / Recommendation
├── Argument 1
│   ├── Evidence 1a
│   └── Evidence 1b
├── Argument 2
│   ├── Evidence 2a
│   └── Evidence 2b
└── Argument 3
    ├── Evidence 3a
    └── Evidence 3b
```
**示例**：「应收购公司 X」支撑：(1) 补齐分析产品缺口，(2) 其团队专长我们招不到，(3) 比自建便宜——各有具体数据。

### SWOT Matrix（SWOT 矩阵）
**是什么**：在 2×2（内部/外部 × 正/负）中映射优势、劣势、机会、威胁。
**何时用**：战略评估——快速定位竞争位势、新市场或重大举措。
**结构**：

|  | Positive | Negative |
|---|---|---|
| **Internal** | Strengths | Weaknesses |
| **External** | Opportunities | Threats |

**示例**：评估新产品线——优势：既有客户基础；劣势：无领域专长；机会：竞品忽略该细分；威胁：监管变化可能杀死市场。

---

## 框架选型指南（Framework Selection Guide）

| Problem Type | Best Framework(s) |
|---|---|
| Why is something broken? | Issue Tree, Fishbone |
| Validating a hypothesis | Hypothesis Tree |
| Financial diagnosis | Profitability Tree |
| Operational bottleneck | Process Flow Decomposition |
| Customer experience issue | Customer Journey Map |
| Competitive positioning | Value Chain Analysis, SWOT Matrix |
| Complex system behavior | Systems Map |
| Organizational / political | Stakeholder Map |
| Planning under uncertainty | Scenario Tree |
| Product roadmap decisions | Feature Tree |
| Technical architecture | Technology Stack Decomposition |
| Structuring any analysis | MECE Decomposition |
| Presenting recommendations | Pyramid Principle |
| Root cause analysis | Fishbone, Issue Tree |
| Strategic assessment | SWOT Matrix, Scenario Tree |
