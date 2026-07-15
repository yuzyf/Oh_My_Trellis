<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/first-principles-thinking/references/case-studies.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 第一性原理思考：案例研究（First Principles Thinking: Case Studies）

把第一性原理（first principles）用到真实场景，挑战常规假设，得出更好解法的实例。

---

## 第 1 部分：软件工程案例（Software Engineering Case Studies）

### 示例 1：数据库选型（Database Selection）

**常规思路（Conventional Thinking）：**「新服务我们要用 PostgreSQL。」

**第一性原理分析：**

| 假设（Assumption） | 质疑（Challenge） | 基本事实（Ground Truth） |
|---|---|---|
| 需要 RDBMS | 真实数据关系是什么？ | 数据是键值对，不需要 join |
| 需要 ACID | 用例实际要什么一致性？ | 读多写少，最终一致性可接受 |
| 需要 SQL 查询能力 | 实际会跑哪些查询？ | 只有按主键的点查 |

**基本事实：**
1. 服务把用户偏好存成键值对
2. 实体之间没有关系
3. 访问模式全是单键查找
4. 读写比约 100:1
5. 每个 key 的数据小于 1KB

**推理链（Reasoning Chain）：**
- 我们默认 PostgreSQL，是因为那是团队标准库
- 实际数据模型没有任何关系型特征
- 全部按主键访问，无 join、聚合或范围查询
- 键值存储（DynamoDB、Redis，甚至内存 map）正好匹配访问模式
- 对本用例，PostgreSQL 只会增加连接池、vacuum、schema 迁移等运维负担，零收益

**结论：** 键值存储就够了。对本无关系特征的问题上 PostgreSQL，会引入不必要的运维复杂度。选匹配真实数据模型的工具，而不是团队默认。

---

### 示例 2：微服务 vs 单体（Microservices vs Monolith）

**常规思路：**「微服务是现代最佳实践。第一天就该拆成服务。」

**第一性原理分析：**

| 假设 | 质疑 | 基本事实 |
|---|---|---|
| 微服务能更快开发 | 对谁更快，在什么团队规模？ | 2 人团队时，网络边界让每次改动都变慢 |
| 独立扩缩容至关重要 | 什么真正需要独立扩？ | 整站 100 RPS，单进程轻松应付 |
| 服务间网络调用开销可接受 | 实际延迟预算是多少？ | 用户期望 <100ms；每次跨服务调用加 5–20ms |

**基本事实：**
1. 未来 12 个月团队是 2 名工程师
2. 可预见负载 <100 RPS
3. 领域组件耦合高——订单、支付、库存会一起变
4. 部署复杂度随服务数线性上升（CI、监控、service mesh）

**推理链：**
- 微服务解决的是大规模下独立团队部署的问题
- 2 人时，没有需要解决的团队协调问题
- 领域紧耦合——拆开只会带来分布式事务，却不减复杂度
- 模块边界清晰的单体，能得到同样的代码组织收益，却无网络开销
- 团队长到 8–10 人时，再沿团队所有权边界拆服务

**结论：** 小团队 + 紧耦合领域逻辑时，结构良好的单体才是对的架构。微服务带来的运维成本，只有在独立团队需要独立部署时才回本。先做单体、保持模块边界干净，等团队增长再拆。

---

### 示例 3：认证系统（Authentication System）

**常规思路：**「认证要用 OAuth2 + JWT。」

**第一性原理分析：**

| 假设 | 质疑 | 基本事实 |
|---|---|---|
| 需要 OAuth2 协议 | 认证的消费者是谁？ | 只有自家第一方 Web 应用——没有第三方客户端 |
| JWT 对无状态认证必要 | 是否真的需要无状态认证？ | 单机服务；session 查找是 hash map 访问 |
| 需要 refresh token 轮换 | 实际会话生命周期？ | 用户登一次待几天；会话过期是可接受 UX |

**基本事实：**
1. 唯一客户端是公司自己的 Web 应用
2. 没有需要委托授权的第三方集成
3. 应用跑在单机（或带 sticky session 的小集群）
4. 活跃用户数千量级——session 存储微不足道

**推理链：**
- OAuth2 解决的是第三方应用的委托授权
- 我们没有第三方——只是自家用户登自家应用
- JWT 引入复杂度：撤销要 blocklist（反而破坏无状态）、token 体积膨胀每个请求、密钥轮换要小心
- 带安全 cookie 的服务端 session 更简单、可立即撤销、无 token 膨胀
- 若将来有第三方客户端，再引入 OAuth2；现在上是过早优化

**结论：** 第一方应用 + 单机/小集群时，安全 cookie 的服务端 session 足够。OAuth2/JWT 解决的是我们现在没有的问题。

---

### 示例 4：缓存策略（Caching Strategy）

**常规思路：**「每个服务前面都要加 Redis 缓存层。」

**第一性原理分析：**

| 假设 | 质疑 | 基本事实 |
|---|---|---|
| 数据库是瓶颈 | 实际查询延迟与容量？ | p99 查询 5ms；库 CPU 15% |
| 缓存必然加速 | 数据变更频率与一致性需求？ | 写频繁；强一致性要求；缓存命中率会很差 |
| 共享 Redis 是标准 | 是否有进程内替代？ | 单实例部署；热数据可放进程内存 |

**基本事实：**
1. 当前 DB 远未饱和
2. 写多读少的热路径使缓存失效昂贵
3. 产品要求读你刚写的数据
4. 部署形态允许进程内缓存

**推理链：**
- 缓存解决的是读多写少、可接受短暂不一致的延迟问题
- 我们的负载与一致性要求都不匹配
- 过早加 Redis 等于多一个故障点、多一套运维与一致性协议
- 若将来某条读路径成为瓶颈，再针对那条路径加缓存并明确失效策略

**结论：** 现在不要默认加 Redis。先量测；仅在证据表明某条读路径需要、且一致性模型允许时，再引入缓存。

---

### 示例 5：API 设计（API Design）

**常规思路：**「内部服务通信也一律 REST + JSON。」

**第一性原理分析：**

| 假设 | 质疑 | 基本事实 |
|---|---|---|
| REST 是通用最佳实践 | 消费者是谁？契约稳定性？ | 全是内部 Go 服务；契约由我们控制 |
| JSON 足够好 | 序列化开销与 schema 演进？ | 负载是结构化、schema 稳定；二进制更省 |
| 单向请求/响应够用 | 通信模式？ | 部分场景要服务端流（实时指标、日志 tail） |

**基本事实：**
1. 调用方与被调方都是内部服务
2. 团队统一用 Go
3. Payload 是结构稳定、变更不频繁的结构化数据
4. 部分模式需要 server-sent streams

**推理链：**
- REST 优化的是广泛互操作（浏览器、第三方）
- 内部 Go 服务更受益于强类型契约、高效二进制序列化与代码生成
- gRPC 提供这些：Protobuf schema、二进制序列化（结构化数据常比 JSON 小 5–10 倍）、双向流、Go 客户端/服务端代码生成
- REST 要手写客户端、JSON 编解码开销，流式还要另找方案
- 若以后有外部消费者，可用 gRPC-gateway 从同一服务定义暴露 REST

**结论：** 内部服务通信用 gRPC + Protocol Buffers。强类型契约在编译期抓住集成错误，二进制序列化降低体积与解析开销，原生流匹配真实通信模式。只有出现外部消费者时再加 REST gateway。

---

### 反模式：用第一性原理过度工程（Anti-Pattern: Over-Engineering from First Principles）

第一性原理也会走偏。警惕：

**重新发明轮子：** 第一性原理不是无视现有方案。若 PostgreSQL 确实合适，分析应确认它——而不是为了新奇硬造替代。

**分析瘫痪：** 不是每个决策都值得深度拆解。对难以回退的决策（架构、基础设施、数据模型）用第一性原理；对便宜可改的决策（代码风格、目录结构、变量命名）用惯例。

**忽视运维现实：** 团队没人会运维的「理论最优」方案，不如社区支持广的常规方案。要把团队专长与运维负担算进去。

**检验标准：** 若第一性原理分析最终指向一个知名工具或模式，那也是有效结果。目标不是唱反调，而是用自觉决策替代默认假设。

---

### 软件工程分析模板（Software Engineering Analysis Template）

挑战技术决策时用：

```
DECISION UNDER REVIEW: [What we plan to do]

CONVENTIONAL REASONING: [Why we assumed this was correct]

ASSUMPTION DECOMPOSITION:
| Assumption | Challenge Question | Ground Truth |
|---|---|---|
| [Assumption 1] | [Question that tests it] | [What is actually true] |
| [Assumption 2] | [Question that tests it] | [What is actually true] |
| [Assumption 3] | [Question that tests it] | [What is actually true] |

GROUND TRUTHS:
1. [Verified fact about our specific context]
2. [Verified fact about our specific context]
3. [Verified fact about our specific context]

REASONING CHAIN:
- [Step 1: What the conventional approach actually solves]
- [Step 2: Whether we have that specific problem]
- [Step 3: What our actual problem is]
- [Step 4: What solution matches the actual problem]

CONCLUSION: [Decision and rationale]

REVERSAL TRIGGER: [Under what future conditions should we revisit this decision]
```

---

## 第 2 部分：SpaceX 与 Tesla 案例（SpaceX & Tesla Case Studies）

### 案例 1：SpaceX 火箭降本（Rocket Cost Reduction）

**常规思路：**「火箭要 6000 万美元，因为航天天生贵。那是市场价。」

**第一性原理分析：**

Elon Musk 把火箭拆到原材料，问：火箭在物理上到底由什么构成？

**火箭原材料成本：** 约 200 万美元（航天级铝、碳纤维、钛、燃料）。

**成品火箭成本：** 既有厂商约 6000 万美元。

**缺口：** 5800 万美元——相对原材料约 30 倍加价。

**成本分解：**

| 成本驱动 | 行业做法 | 第一性原理做法 | 结果 |
|---|---|---|---|
| 制造 | 外包专业航天承包商，cost-plus 利润 | 自建；纵向整合去掉承包商利润 | 部件成本降 50–70% |
| 设计 | 沿用几十年验证设计；极力避险 | 从可制造性重新设计；接受可计算风险 | 更简单设计、更少零件、更低成本 |
| 人力 | 少量高度专业化航天老兵 | 从相邻行业（汽车、软件）招优秀工程师再培训 | 人才池更大、人力更便宜、解题更新鲜 |
| 可复用 | 一次性火箭——每次飞行毁掉 6000 万美元硬件 | 一子级着陆复用——成本摊到 10+ 次飞行 | 最贵部件单次飞行成本约 10x 下降 |

**基本事实：**
1. Falcon 9 原材料大约只占成品价 2%
2. 航天 cost-plus 合同激励的是更高成本，不是更低
3. 没有物理定律禁止助推器着陆复用
4. 软件控制的精确着陆是工程问题，不是不可能

**结果：** Falcon 9 入轨成本大约降到每公斤 2700 美元，对比航天飞机约 54500 美元/kg。SpaceX 通过质疑成本结构每一层，相对在位发射商大约做到 10x 降本。

---

### 案例 2：Tesla 电池成本（Battery Cost）

**常规思路：**「电池包 600 美元/kWh，因为锂离子技术就这样。等化学突破吧。」

**第一性原理分析：**

Musk 把电池包成本拆成原材料与制造过程。

**原材料成本：** 约 80 美元/kWh（锂、钴、镍、锰、石墨、铝、钢、隔膜、电解液）。

**当时包级成本：** 约 600 美元/kWh。

**缺口：** 520 美元/kWh——绝大部分不在材料，而在制造、设计与供应链。

**成本分解：**

| 成本驱动 | 行业做法 | 第一性原理做法 | 结果 |
|---|---|---|---|
| 规模 | 小批量服务小众 EV | 建 Gigafactory——规模拉低每部件单位成本 | 仅体量就可降 30–40% |
| 设计 | 商品圆柱电芯 + 模块托盘 | 电芯/模组/包一体化设计；减少结构件 | 结构电池包（4680）——包即底盘，去掉冗余重量与零件 |
| 供应链 | 向电芯厂买，吃对方利润 | 纵向整合——采矿、精炼、电芯自制 | 去掉矿到车之间 3–4 层利润 |
| 化学 | 等学术突破 | 规模上渐进改进——正极优化、干电极涂布、硅负极等 | 不必等突破化学也能持续降本 |

**基本事实：**
1. 电池包原材料大约只占成品包价 13%
2. 弥合缺口不需要化学突破——制造与设计改进就够
3. 电池制造更像高体量消费电子，而不是传统汽车
4. 从原料到成品包的纵向整合去掉多层利润

**结果：** Tesla 在包级大约做到 100 美元/kWh，相对起点 600 美元/kWh 降幅 80%+。主要靠制造规模、设计整合与供应链控制——不是等基础化学突破。

---

### 给软件工程师的关键启示（Key Lessons for Software Engineers）

#### 启示 1：质疑行业标准

**SpaceX 启示：**「火箭就该那么贵」不是物理定律，而是具体行业做法（cost-plus、一次性硬件、外包制造）无人质疑的后果。

**软件类比：**「软件项目就该那么久」或「这事得 20 人团队」往往反映积累的惯例，而非基本约束。把项目拆成真实任务、从基本事实估每一块，你会发现工期常由协调开销驱动，而不是技术复杂度。

**第一性原理问题：** 若能从零开始、无继承约束，这件事在时间/人力/金钱上会花多少？

#### 启示 2：区分物理约束与人为约束

**SpaceX 启示：** 可复用一子级——最贵部件——改变了航天成本结构。一次工程投入（动力着陆）摊到数十次飞行。

**软件类比：** 很多「硬」约束其实是工具、流程或组织选择。编译时间、部署频率、测试时长常常是可选架构的结果，不是自然法则。

**第一性原理问题：** 这是物理/数学必然，还是我们（或行业）选择的结果？

#### 启示 3：规模与复用改变单位经济

**Tesla 启示：** Gigafactory 用体量把单位成本打下来；结构电池包去掉冗余。

**软件类比：** 平台化、共享库、一次建好被 10 个团队用的内部工具，单位价值远高于一次性脚本。但可复用有成本：泛化、文档、支持。第一性原理问题是复用是否真会发生。

**第一性原理问题：** 这会真的被复用吗？被谁、多少次、泛化成本能不能回本？

#### 启示 4：在关键处纵向整合

**Tesla 启示：** 从原料到整车控制供应链，去掉利润层并实现更紧整合（结构电池包）。但 Tesla 并非一切自研——轮胎、玻璃、大宗件仍外购。

**软件类比：** 自研 vs 采购同一逻辑。当组件是核心差异化、外部选项增加摩擦或利润时，纵向整合（自研）；当组件是大宗商品、别人规模做得更好时，外购。

**第一性原理检验：**
- 是核心差异化？自研。
- 是大宗商品？外购。
- 外部选项带来不可接受依赖风险？自研。
- 自研会分心核心产品？外购。

---

### Musk 方法摘要（The Musk Method Summarized）

1. **识别常规智慧：**「大家都这么做。就得花这么多。就得花这么久。」
2. **拆到物理/基本约束：** 真实原料输入是什么？物理（或问题的根本性质）要求什么？
3. **找出缺口：** 成本/时间/复杂度从哪来？来自基本约束，还是积累的惯例？
4. **逐层质疑：** 对每个成本驱动问：这是必要的，还是「一直这么干」？
5. **从基本事实重建：** 从物理约束与真实需求设计方案，而不是从行业惯例。
6. **接受可计算风险：** 常规路径安全因为已被证明。第一性原理路径要接受新方案可能失败——但当常规比基本约束贵 10–30 倍时，上行空间值得风险。

---

### 警告：此方法何时失败（Caution: When This Approach Fails）

第一性原理很强，但并非万能。它会失败当：

1. **常规方案本来就是最优。** 有时行业标准存在，是因为成千上万人已为同一约束优化过。第一性原理分析在此应确认这一点，而不是强行不同答案。

   **软件启示：** 若分析结论是「用 PostgreSQL」，那也是有效的第一性原理结论。目标是自觉决策，不是为反而反。

2. **执行能力配不上野心。** SpaceX 能纵向整合，因为有数十亿资本与世界级工程人才。5 人创业公司没法纵向整合出 600 美元/kWh 电池成本。

   **软件启示：** 自研数据库可以是存储问题的第一性原理解，但对 99.9% 团队也是糟糕主意。让方案匹配你真实的执行能力。

3. **问题是社会性的，不是技术性的。** 第一性原理适合物理、工程与逻辑问题。对由人类行为、政治、监管或文化驱动的问题效果较差——那里的「常规智慧」反映的是真实社会约束，不是技术约束。

   **软件启示：**「我们用 Java 因为团队会 Java」是合法约束，不是非理性。为了理论上更好而用 Rust 重写，忽略了团队用 Java 交付功能、上 Rust 要 6 个月爬坡的社会现实。

---

### 应用模板（Application Template）

遇到「一直都这么干」时用：

```
CONVENTIONAL WISDOM: [The accepted approach and its assumed cost/timeline]

RAW INPUTS / FUNDAMENTAL CONSTRAINTS:
- [What does the problem actually require at the most basic level?]
- [What are the physical, logical, or mathematical constraints?]
- [What would this cost if built from raw inputs with zero legacy overhead?]

THE GAP:
- Current cost/time/complexity: [X]
- Fundamental minimum: [Y]
- Gap: [X - Y] — where is this gap coming from?

COST DECOMPOSITION:
| Cost Driver | Conventional Approach | First Principles Alternative |
|---|---|---|
| [Driver 1] | [How it is done now] | [What could be done instead] |
| [Driver 2] | [How it is done now] | [What could be done instead] |

FEASIBILITY CHECK:
- Do we have the capability to execute the first principles approach?
- Is the potential improvement large enough to justify the risk?
- What is the worst case if the novel approach fails?
- Can we fall back to the conventional approach?

DECISION: [Proceed with first principles approach / Confirm conventional approach is correct]
```
