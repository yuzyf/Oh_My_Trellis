> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.trellis/workflow.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

# 开发工作流（Development Workflow）

---

## 核心原则（Core Principles）

1. **先规划再写代码** —— 动手前先想清楚要做什么
2. **规范靠注入，不靠记忆** —— 指南通过 hook/skill 注入，而不是靠模型死记
3. **一切都要落盘** —— 研究、决策、教训都写入文件；对话会被压缩，文件不会
4. **增量开发** —— 一次只做一个任务
5. **沉淀经验** —— 每个任务结束后复盘，把新知识写回规范（spec）

---

## Trellis 系统

### 开发者身份（Developer Identity）

首次使用时，初始化你的身份：

```bash
python3 ./.trellis/scripts/init_developer.py <your-name>
```

会创建 `.trellis/.developer`（gitignore）+ `.trellis/workspace/<your-name>/`。

### 规范系统（Spec System）

`.trellis/spec/` 存放按包（package）与层（layer）组织的编码指南。

- `.trellis/spec/<package>/<layer>/index.md` —— 入口，含 **Pre-Development Checklist（开发前检查清单）** + **Quality Check（质量检查）**。真正的细则在它指向的那些 `.md` 文件里。
- `.trellis/spec/guides/index.md` —— 跨包思考指南。

```bash
python3 ./.trellis/scripts/get_context.py --mode packages   # 列出包 / 层
```

**何时更新规范**：发现新模式/约定 · 需要固化的防 bug 做法 · 新的技术决策。

### 任务系统（Task System）

每个任务在 `.trellis/tasks/{MM-DD-name}/` 下有自己的目录，内含 `task.json`、`prd.md`、可选的 `design.md`、可选的 `implement.md`、可选的 `research/`，以及面向可分子代理平台的上下文清单（`implement.jsonl`、`check.jsonl`）。

```bash
# 任务生命周期
python3 ./.trellis/scripts/task.py create "<title>" [--slug <name>] [--parent <dir>]
python3 ./.trellis/scripts/task.py start <name>          # 设置活跃任务（可用时按会话隔离）
python3 ./.trellis/scripts/task.py current --source      # 显示活跃任务及其来源
python3 ./.trellis/scripts/task.py finish                # 清除活跃任务（触发 after_finish hooks）
python3 ./.trellis/scripts/task.py archive <name>        # 移到 archive/{year-month}/
python3 ./.trellis/scripts/task.py list [--mine] [--status <s>]
python3 ./.trellis/scripts/task.py list-archive

# 代码-规范上下文（通过 JSONL 注入 implement/check 代理）。
# 对可分子代理的平台，`implement.jsonl` / `check.jsonl` 会在 `task create` 时预置；
# 需要时，AI 在规划阶段整理真正的 spec + research 条目。
python3 ./.trellis/scripts/task.py add-context <name> <action> <file> <reason>
python3 ./.trellis/scripts/task.py list-context <name> [action]
python3 ./.trellis/scripts/task.py validate <name>

# 任务元数据
python3 ./.trellis/scripts/task.py set-branch <name> <branch>
python3 ./.trellis/scripts/task.py set-base-branch <name> <branch>    # PR 目标
python3 ./.trellis/scripts/task.py set-scope <name> <scope>

# 层级（父/子）
python3 ./.trellis/scripts/task.py add-subtask <parent> <child>
python3 ./.trellis/scripts/task.py remove-subtask <parent> <child>

# 创建 PR
python3 ./.trellis/scripts/task.py create-pr [name] [--dry-run]
```

> 运行 `python3 ./.trellis/scripts/task.py --help` 查看权威、最新的命令列表。

**当前任务机制**：`task.py create` 会创建任务目录，并在会话身份可用时自动设置“本会话活跃任务”指针，以便规划阶段的面包屑立刻生效。`task.py start` 写入同一指针（若已设置则幂等），并把 `task.json.status` 从 `planning` 翻到 `in_progress`。状态保存在 `.trellis/.runtime/sessions/`。若 hook 输入、`TRELLIS_CONTEXT_ID` 或平台原生会话环境变量都给不出上下文键，则没有活跃任务，`task.py start` 会失败并给出会话身份提示。`task.py finish` 删除当前会话文件（状态不变）。`task.py archive <task>` 写入 `status=completed`，把目录移到 `archive/`，并删除仍指向该已归档任务的运行时会话文件。

> 译注：`create` 只进入规划；`start` 才批准实现。两者不要混用。

### 工作区系统（Workspace System）

在 `.trellis/workspace/<developer>/` 下记录每次 AI 会话，用于跨会话追踪。

- `journal-N.md` —— 会话日志。**每个文件最多 2000 行**；超出会自动创建新的 `journal-(N+1).md`。
- `index.md` —— 个人索引（总会话数、最近活跃）。

```bash
python3 ./.trellis/scripts/add_session.py --title "Title" --commit "hash" --summary "Summary"
```

### 上下文脚本（Context Script）

```bash
python3 ./.trellis/scripts/get_context.py                            # 完整会话运行时
python3 ./.trellis/scripts/get_context.py --mode packages            # 可用包 + 规范层
python3 ./.trellis/scripts/get_context.py --mode phase --step <X.Y>  # 某个工作流步骤的详细指南
```

---

<!--
  WORKFLOW-STATE 面包屑契约（编辑下面的标签块前先读）

  下方 ## Phase Index 小节中嵌入的 [workflow-state:STATUS] 块，是每个受支持
  AI 平台的 UserPromptSubmit hook 所读取的“每轮 <workflow-state> 面包屑”的
  唯一事实来源。inject-workflow-state.py（Python 平台）与
  inject-workflow-state.js（OpenCode 插件）只解析它们 —— 自 v0.5.0-rc.0 起，
  脚本内不再内嵌回退字典。

  STATUS 字符集：[A-Za-z0-9_-]+。当 hook 找不到标签时，会降级为通用的
  "Refer to workflow.md for current step." 行 —— 故意做成可见，以便用户
  发现并修复损坏的 workflow.md。

  不变量（test/regression.test.ts）：
    每个标为 `[required · once]` 的 workflow-walkthrough 步骤，都必须在其
    阶段对应的 [workflow-state:*] 块中有匹配的强制说明行。面包屑是唯一的
    每轮通道；若强制步骤未在此提及，AI 会静默跳过（阶段 1 规划门与
    阶段 3.4 提交被跳过，都曾由此缺口造成）。

  标签 ↔ 阶段 范围：
    [workflow-state:no_task]      → 无活跃任务；阶段 1 之前
    [workflow-state:planning]     → 整个阶段 1（status='planning'）
    [workflow-state:planning-inline] → Codex inline 变体的阶段 1
    [workflow-state:in_progress]  → 阶段 2 + 阶段 3.2-3.4
                                    （status 从 task.py start 起保持
                                    'in_progress'，直到 task.py archive）
    [workflow-state:in_progress-inline] → Codex inline 变体的阶段 2/3
    [workflow-state:completed]    → 当前为 DEAD：cmd_archive 在同一调用中
                                    翻转状态并移动目录，解析器会丢失指针
                                    （块保留，供未来显式
                                    in_progress→completed 过渡使用）

  编辑清单：
    - 当你改 [workflow-state:STATUS] 块时，也要检查对应阶段中
      `[required · once]` 的 walkthrough 步骤是否同步
    - 编辑后运行 `trellis update`，把新正文推到下游用户项目
      （按块级托管替换）
    - 完整运行时契约：
      .trellis/spec/cli/backend/workflow-state-contract.md
-->

## 阶段索引（Phase Index）

```
阶段 1：Plan（规划）    → 先分类、取得创建任务同意，再写规划产物
阶段 2：Execute（执行） → 仅在任务状态为 in_progress 后实现
阶段 3：Finish（收束）  → 核验、更新规范、提交，并收尾
```

### 请求分诊（Request Triage）

- 简单对话或小任务：只问本轮是否要创建 Trellis 任务。若用户说不，本会话跳过 Trellis。
- 复杂任务：询问是否可创建 Trellis 任务并进入规划。若用户说不，不要做大范围的内联实现；解释、澄清范围，或建议拆小。
- 用户同意创建任务 ≠ 同意开始实现。规划仍要先做。

### 规划产物（Planning Artifacts）

- `prd.md` —— 需求、约束与验收标准。不要把技术设计或执行清单放这里。
- `design.md` —— 复杂任务的技术设计：边界、契约、数据流、权衡、兼容性、上线/回滚形态。
- `implement.md` —— 复杂任务的执行计划：有序检查清单、验证命令、评审门与回滚点。
- `implement.jsonl` / `check.jsonl` —— 给子代理上下文用的规范与研究清单。它们不能替代 `implement.md`。
- 轻量任务可以只有 PRD。复杂任务在 `task.py start` 前必须具备 `prd.md`、`design.md` 与 `implement.md`。

### 父/子任务树（Parent / Child Task Trees）

当一个用户请求包含多个可独立验证的交付物时，使用父任务。父任务拥有源需求集合、任务地图、跨子任务验收标准与最终集成评审；除非父任务本身也有直接工作，否则它通常不应作为实现目标。

用子任务承载可独立规划、实现、检查并归档的交付物。父/子结构不是依赖系统：若一个子任务必须等另一个，把排序写进子任务的 `prd.md` / `implement.md`，并保持每个子任务的验收标准可测。

用 `task.py create "<title>" --slug <name> --parent <parent-dir>` 创建新的子任务。用 `task.py add-subtask <parent> <child>` 关联已有任务，用 `task.py remove-subtask <parent> <child>` 解除错误关联。

<!-- 每轮面包屑：无活跃任务时显示（阶段 1 之前） -->

[workflow-state:no_task]
No active task. First classify the current turn and ask for task-creation consent before creating any Trellis task.
Simple conversation / small task: ask only whether this turn should create a Trellis task. If the user says no, skip Trellis for this session.
Complex task: ask the user if you can create a Trellis task and enter the planning phase. If the user says no, explain, clarify scope, or suggest a smaller split.
[/workflow-state:no_task]

> 译注：上面 `[workflow-state:*]` 块正文保留英文原样，因为它们是 hook 解析的运行时契约源；下面各阶段 walkthrough 为人类可读中文对照。

### 阶段 1：Plan（规划）
- 1.0 创建任务 `[required · once]`（仅在取得创建任务同意后）
- 1.1 需求探索 `[required · repeatable]`（`prd.md`；复杂任务还需要 `design.md` + `implement.md`）
- 1.2 研究 `[optional · repeatable]`
- 1.3 配置上下文 `[required · once]` —— Claude Code、Cursor、OpenCode、Codex、Kiro、Gemini、Qoder、CodeBuddy、Copilot、Droid、Pi、Oh My Pi（仅子代理分派平台；inline 平台跳过）
- 1.4 激活任务 `[required · once]`（评审门，然后 `task.py start`；状态 → in_progress）
- 1.5 完成条件

<!-- 每轮面包屑：整个阶段 1 期间显示（status='planning'） -->

[workflow-state:planning]
Load `trellis-brainstorm`; stay in planning.
Lightweight: `prd.md` can be enough. Complex: finish `prd.md`, `design.md`, and `implement.md`; ask for review before `task.py start`.
Multi-deliverable scope: consider a parent task plus independently verifiable child tasks; dependencies must be written in child artifacts, not implied by tree position.
Sub-agent mode: curate `implement.jsonl` and `check.jsonl` as spec/research manifests before start.
[/workflow-state:planning]

<!-- 每轮面包屑：在 codex.dispatch_mode=inline 时于整个阶段 1 显示。
     这是 Codex 专用的可选替代，对应 [workflow-state:planning]。主代理在
     阶段 2 直接改代码，因此跳过 jsonl 整理 ——
     inline 工作流加载 `trellis-before-dev`，而不是把 JSONL 注入子代理。 -->

[workflow-state:planning-inline]
Load `trellis-brainstorm`; stay in planning.
Lightweight: `prd.md` can be enough. Complex: finish `prd.md`, `design.md`, and `implement.md`; ask for review before `task.py start`.
Multi-deliverable scope: consider a parent task plus independently verifiable child tasks; dependencies must be written in child artifacts, not implied by tree position.
Inline mode: skip jsonl curation; Phase 2 reads artifacts/specs via `trellis-before-dev`.
[/workflow-state:planning-inline]

### 阶段 2：Execute（执行）
- 2.1 实现 `[required · repeatable]`
- 2.2 质量检查 `[required · repeatable]`
- 2.3 回滚 `[on demand]`

<!-- 每轮面包屑：status='in_progress' 时显示。
     范围：整个阶段 2 + 阶段 3.2-3.4（status 从 task.py start 起保持
     'in_progress'，直到 task.py archive；只有 archive 会翻转它）。
     因此正文必须覆盖从实现到提交的全部强制步骤，包括阶段 3.3 规范更新
     与阶段 3.4 提交。 -->

子代理分派协议适用于所有平台与所有子代理，包括 class-2 的 Codex/Copilot/Gemini/Qoder 以及 `trellis-research`：每个分派提示都以 `Active task: <task path from task.py current>` 开头，然后再写角色专属说明。

[workflow-state:in_progress]
Tools: `trellis-implement` / `trellis-research` are sub-agent types only (Task/Agent tool, NOT Skill; there is no skill by these names). `trellis-update-spec` is a skill. `trellis-check` exists as both; prefer the Agent form when verifying after code changes.
Flow: `trellis-implement` -> `trellis-check` -> `trellis-update-spec` -> commit (Phase 3.4) -> `/trellis:finish-work`.
Main-session default: dispatch implement/check sub-agents. Sub-agent self-exemption: if already running as `trellis-implement`, do NOT spawn another `trellis-implement` or `trellis-check`; if already running as `trellis-check`, do NOT spawn another `trellis-check` or `trellis-implement`. Dispatch is main session only.
Dispatch prompt starts with `Active task: <task path from task.py current>`. Read context: jsonl entries -> `prd.md` -> `design.md if present` -> `implement.md if present`.
[/workflow-state:in_progress]

<!-- 每轮面包屑：status='in_progress' 且 codex.dispatch_mode=inline 时显示。
     这是 Codex 专用的可选替代，对应 [workflow-state:in_progress]。
     主会话直接改代码，而不是分派子代理。 -->

[workflow-state:in_progress-inline]
Flow: `trellis-before-dev` -> edit -> `trellis-check` -> validation -> `trellis-update-spec` -> commit (Phase 3.4) -> `/trellis:finish-work`.
Do not dispatch implement/check sub-agents in inline mode.
Read context: `prd.md` -> `design.md if present` -> `implement.md if present`, plus relevant spec/research loaded by skills.
[/workflow-state:in_progress-inline]

### 阶段 3：Finish（收束）
- 3.2 调试复盘 `[on demand]`
- 3.3 规范更新 `[required · once]`
- 3.4 提交改动 `[required · once]`
- 3.5 收尾提醒

> 注：步骤 3.1 已并入 2.2（最后一轮全范围检查）与 3.4（提交前导）。编号保持稳定，以免破坏外部引用。

<!-- 每轮面包屑：status='completed' 时显示。
     正常流程中当前为 DEAD：cmd_archive 在同一调用中写入 status='completed'
     并把任务目录移到 archive/，因此活跃任务解析器会丢失指针，hook 也不会
     在已归档任务上触发。块保留，供未来状态过渡重设计使用（例如显式的
     in_progress→completed 命令）。编辑通道与在线块相同。 -->

[workflow-state:completed]
Code committed. Run `/trellis:finish-work`; if dirty, return to Phase 3.4 first.
[/workflow-state:completed]

### 规则（Rules）

1. 先判断你在哪个阶段，再从该阶段的下一步继续
2. 每个阶段内按顺序执行步骤；`[required]` 步骤不能跳过
3. 阶段可以回退（例如执行中发现 prd 缺陷 → 回到规划修复，再重新进入执行）
4. 标为 `[once]` 的步骤若输出已存在则跳过；不要重跑
5. 产物是否存在决定下一步；缺少 `design.md` / `implement.md` 对轻量任务有效，对复杂任务则表示规划未完成。

### 活跃任务路由（Active Task Routing）

当活跃任务内的用户请求匹配下列意图时，先路由，再按需加载详细阶段步骤。

[Claude Code, Cursor, OpenCode, codex-sub-agent, Kiro, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi, Oh My Pi]

- 规划或需求不清 -> `trellis-brainstorm`。
- `in_progress` 的实现/检查 -> 分派 `trellis-implement` / `trellis-check`。
- 反复调试 -> `trellis-break-loop`；规范更新 -> `trellis-update-spec`。

[/Claude Code, Cursor, OpenCode, codex-sub-agent, Kiro, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi]

[codex-inline, Kilo, Antigravity, Devin]

- 规划或需求不清 -> `trellis-brainstorm`。
- 编辑前 -> `trellis-before-dev`；编辑后 -> `trellis-check`。
- 反复调试 -> `trellis-break-loop`；规范更新 -> `trellis-update-spec`。

[/codex-inline, Kilo, Antigravity, Devin]

### 护栏（Guardrails）

- 创建任务的批准 ≠ 实现批准；实现要等产物评审后的 `task.py start`。
- 只有 PRD 对轻量任务有效；复杂任务需要 `design.md` + `implement.md`。
- 规划必须落到任务产物；汇报完成前必须先跑检查。

### 加载步骤详情（Loading Step Detail）

在每一步运行此命令，获取详细指导：

```bash
python3 ./.trellis/scripts/get_context.py --mode phase --step <step>
# 例如 python3 ./.trellis/scripts/get_context.py --mode phase --step 1.1
```

---

## 阶段 1：Plan（规划）

目标：对请求分类；在需要任务时取得创建同意；并产出实现前必需的规划产物。

#### 1.0 创建任务 `[required · once]`

仅在取得创建任务同意后创建任务目录。该命令把状态设为 `planning`，写入 `task.json`，创建默认 `prd.md`，并在会话身份可用时自动把新任务设为当前目标：

```bash
python3 ./.trellis/scripts/task.py create "<task title>" --slug <name>
```

`--slug` 只是人类可读名称。**不要**包含 `MM-DD-` 日期前缀；`task.py create` 会自动加。

对任务树：先创建父任务，再为每个子任务使用 `--parent <parent-dir>` 创建。不要因为子任务存在就 start 父任务；start 拥有“下一个可独立验证交付物”的那个子任务。

该命令成功后，每轮面包屑会自动切到 `[workflow-state:planning]`，要求 AI 留在规划。

这里只运行 `create` —— 不要同时运行 `start`。`start` 会把状态翻到 `in_progress`，在规划产物评审前就把面包屑切到实现阶段。把 `start` 留给步骤 1.4。

若 `python3 ./.trellis/scripts/task.py current --source` 已指向某个任务，则跳过。

#### 1.1 需求探索 `[required · repeatable]`

加载 `trellis-brainstorm` 技能，并按该技能的指导与用户交互式探索需求。

brainstorm 技能会引导你：

- 一次只问一个问题
- 优先调研，而不是先问用户
- 优先给选项，而不是开放题
- 用户每回答一次，立刻更新 `prd.md`
- 当交付物可独立验证时，把大范围拆成父任务 + 子任务
- 让 `prd.md` 聚焦需求与验收标准
- 对复杂任务，在实现开始前产出 `design.md` 与 `implement.md`

考虑父/子拆分时：

- 当一个请求包含多个可独立验证交付物时，使用父任务。
- 父任务拥有源需求、子任务映射、跨子任务验收标准与最终集成评审。
- 子任务拥有可独立规划、实现、检查并归档的实际交付物。
- 父/子结构不是依赖系统。若子任务 B 依赖子任务 A，把该顺序写进 B 的 `prd.md` / `implement.md`。
- start 拥有下一交付物的子任务。除非父任务本身有直接实现工作，否则不要 start 父任务。

每当需求变化时回到本步，并修订相关产物。

#### 1.2 研究 `[optional · repeatable]`

研究可以在需求探索的任何时刻发生。它不限于本地代码 —— 你可以用任何可用工具（MCP 服务器、技能、网页搜索等）查阅外部信息，包括第三方库文档、行业实践、API 参考等。

[Claude Code, Cursor, OpenCode, codex-sub-agent, Kiro, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi, Oh My Pi]

拉起研究子代理：

- **代理类型**：`trellis-research`
- **任务描述**：研究 <具体问题>
- **关键要求**：研究输出必须落到 `{TASK_DIR}/research/`

[/Claude Code, Cursor, OpenCode, codex-sub-agent, Kiro, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi]

[codex-inline, Kilo, Antigravity, Devin]

在主会话中直接做研究，并把发现写入 `{TASK_DIR}/research/`。（对 `codex-inline` 而言，这可避开 `fork_turns="none"` 的隔离，那种隔离会让 `trellis-research` 子代理无法解析活跃任务路径。）

[/codex-inline, Kilo, Antigravity, Devin]

**研究产物约定**：

- 每个研究主题一个文件（例如 `research/auth-library-comparison.md`）
- 把第三方库用法示例、API 参考、版本约束记入文件
- 记下你发现的相关规范文件路径，供后续引用

brainstorm 与 research 可以自由交错 —— 暂停去研究技术问题，再回来与用户对话。

**关键原则**：研究输出必须写入文件，不能只留在聊天里。对话会被压缩；文件不会。

#### 1.3 配置上下文 `[required · once]`

[Claude Code, Cursor, OpenCode, codex-sub-agent, Kiro, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi, Oh My Pi]

整理 `implement.jsonl` 与 `check.jsonl`，让阶段 2 的子代理拿到正确的规范/研究上下文。这些文件在 `task create` 时已用一条自描述的 `_example` 行预置；这里的工作是填入真实条目。

**位置**：`{TASK_DIR}/implement.jsonl` 与 `{TASK_DIR}/check.jsonl`（已存在）。

**格式**：每行一个 JSON 对象 —— `{"file": "<path>", "reason": "<why>"}`。路径相对仓库根。

**该放什么**：

- **规范文件** —— 与本任务相关的 `.trellis/spec/<package>/<layer>/index.md` 以及具体指南文件（`error-handling.md`、`conventions.md` 等）
- **研究文件** —— 子代理需要查阅的 `{TASK_DIR}/research/*.md`

**不该放什么**：

- 代码文件（`src/**`、`packages/**/*.ts` 等）—— 由子代理在实现时读取，不在此预注册
- 你即将修改的文件 —— 同理

**两个文件如何拆分**：

- `implement.jsonl` → 实现子代理正确写代码所需的规范 + 研究
- `check.jsonl` → 检查子代理用的规范（质量指南、检查约定；需要时也可含同一研究）

这些清单不能替代 `implement.md`。`implement.md` 是复杂任务的人类可读执行计划；jsonl 只列出要注入或加载的上下文文件。

**如何发现相关规范**：

```bash
python3 ./.trellis/scripts/get_context.py --mode packages
```

会列出每个包及其规范层与路径。挑选与本任务领域匹配的条目。

**如何追加条目**：

直接在编辑器里改 jsonl，或使用：

```bash
python3 ./.trellis/scripts/task.py add-context "$TASK_DIR" implement "<path>" "<reason>"
python3 ./.trellis/scripts/task.py add-context "$TASK_DIR" check "<path>" "<reason>"
```

一旦有真实条目，可删除种子 `_example` 行（可选 —— 消费方会自动跳过它）。

就绪门：在 `task.py start` 前，`implement.jsonl` 与 `check.jsonl` 都必须至少包含一条真实的 `{"file": "...", "reason": "..."}`。只有种子 `_example` 行不算就绪。

仅当两个文件都已有真实整理条目时，才跳过本步。

[/Claude Code, Cursor, OpenCode, codex-sub-agent, Kiro, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi, Oh My Pi]

[codex-inline, Kilo, Antigravity, Devin]

跳过本步。上下文由阶段 2 的 `trellis-before-dev` 技能直接加载。

[/codex-inline, Kilo, Antigravity, Devin]

#### 1.4 激活任务 `[required · once]`

产物评审后，把任务状态翻到 `in_progress`：

```bash
python3 ./.trellis/scripts/task.py start <task-dir>
```

对轻量任务，`prd.md` 可以够用。对复杂任务，`prd.md`、`design.md` 与 `implement.md` 必须存在并在 start 前评审。在子代理分派平台上，`implement.jsonl` 与 `check.jsonl` 都必须在 start 前有真实整理条目。运行时消费者为了兼容会容忍缺失或仅种子清单，但那种状态不算规划就绪。

该命令成功后，面包屑会自动切到 `[workflow-state:in_progress]`，随后进入阶段 2 / 3 的其余部分。

若 `task.py start` 因会话身份报错（hook 输入、`TRELLIS_CONTEXT_ID` 或平台原生会话环境都没有上下文键），按错误提示建立会话身份，然后重试。

#### 1.5 完成条件

| 条件 | 是否必需 |
|------|:---:|
| 存在 `prd.md` | ✅ |
| 用户确认任务应进入实现 | ✅ |
| 已运行 `task.py start`（status = in_progress） | ✅ |
| `research/` 有产物（复杂任务） | 推荐 |
| 存在 `design.md`（复杂任务） | ✅ |
| 存在 `implement.md`（复杂任务） | ✅ |

[Claude Code, Cursor, OpenCode, codex-sub-agent, Kiro, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi, Oh My Pi]

| `implement.jsonl` 与 `check.jsonl` 各至少有一条真实整理条目（种子行不算） | ✅ |

[/Claude Code, Cursor, OpenCode, codex-sub-agent, Kiro, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi]

---

## 阶段 2：Execute（执行）

目标：把已评审的规划产物变成通过质量检查的代码。

#### 2.1 实现 `[required · repeatable]`

[Claude Code, Cursor, OpenCode, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi, Oh My Pi]

拉起实现子代理：

- **代理类型**：`trellis-implement`
- **任务描述**：实现已评审的任务产物，查阅 `{TASK_DIR}/research/` 下材料；最后运行项目 lint 与类型检查
- **分派提示护栏**：告诉被拉起的代理：它已经是 `trellis-implement` 子代理，必须直接实现，不要再拉起另一个 `trellis-implement` / `trellis-check`。

平台 hook/插件会自动处理：

- 读取 `implement.jsonl`，并把引用的规范/研究文件注入代理提示
- 注入 `prd.md`，以及若存在的 `design.md` 与 `implement.md`

[/Claude Code, Cursor, OpenCode, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi]

[codex-sub-agent]

拉起实现子代理：

- **代理类型**：`trellis-implement`
- **任务描述**：实现已评审的任务产物，查阅 `{TASK_DIR}/research/` 下材料；最后运行项目 lint 与类型检查
- **分派提示护栏**：提示必须以 `Active task: <task path>` 开头，然后明确说明被拉起的代理已经是 `trellis-implement`，必须直接实现，不要再拉起另一个 `trellis-implement` / `trellis-check`。

Codex 子代理定义会自动处理上下文加载要求：

- 用 `task.py current --source` 解析活跃任务，然后读取 `prd.md`，以及若存在的 `design.md` 与 `implement.md`
- 读取 `implement.jsonl`，并要求代理在写代码前加载每个引用的规范/研究文件

[/codex-sub-agent]

[Kiro]

拉起实现子代理：

- **代理类型**：`trellis-implement`
- **任务描述**：实现已评审的任务产物，查阅 `{TASK_DIR}/research/` 下材料；最后运行项目 lint 与类型检查
- **分派提示护栏**：告诉被拉起的代理：它已经是 `trellis-implement` 子代理，必须直接实现，不要再拉起另一个 `trellis-implement` / `trellis-check`。

平台 prelude 会自动处理上下文加载要求：

- 读取 `implement.jsonl`，并把引用的规范/研究文件注入代理提示
- 注入 `prd.md`，以及若存在的 `design.md` 与 `implement.md`

[/Kiro]

[codex-inline, Kilo, Antigravity, Devin]

1. 加载 `trellis-before-dev` 技能，阅读项目指南
2. 阅读 `{TASK_DIR}/prd.md`，再读若存在的 `design.md`，再读若存在的 `implement.md`
3. 查阅 `{TASK_DIR}/research/` 下材料
4. 按已评审产物实现代码
5. 运行项目 lint 与类型检查

[/codex-inline, Kilo, Antigravity, Devin]

#### 2.2 质量检查 `[required · repeatable]`

[Claude Code, Cursor, OpenCode, codex-sub-agent, Kiro, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi, Oh My Pi]

拉起检查子代理：

- **代理类型**：`trellis-check`
- **任务描述**：对照规范与任务产物审查全部代码改动；直接修复发现的问题；确保 lint 与类型检查通过
- **分派提示护栏**：告诉被拉起的代理：它已经是 `trellis-check` 子代理，必须直接审查/修复，不要再拉起另一个 `trellis-check` / `trellis-implement`。

检查代理的职责：

- 对照规范审查代码改动
- 对照 `prd.md`、若存在的 `design.md` 与 `implement.md` 审查代码改动
- 自动修复它发现的问题
- 运行 lint 与 typecheck 验证

[/Claude Code, Cursor, OpenCode, codex-sub-agent, Kiro, Gemini, Qoder, CodeBuddy, Copilot, Droid, Pi]

[codex-inline, Kilo, Antigravity, Devin]

加载 `trellis-check` 技能，并按其指导核验代码：

- 规范合规
- lint / 类型检查 / 测试
- 跨层一致性（当改动跨层时）

若发现问题 → 修复 → 再检查，直到全绿。

[/codex-inline, Kilo, Antigravity, Devin]

**最终一轮（进入阶段 3.4 提交前）**：一个任务的最后一次 2.2 必须做全范围，而不只看最近那一段实现。用 `python3 ./.trellis/scripts/get_context.py --mode packages` 列出所有受影响的包，然后加载每个包规范索引的 Quality Check 部分。这样能抓住中途局部 2.2 抓不到的跨层 / 多包问题。

#### 2.3 回滚 `[on demand]`

- `check` 暴露 prd 缺陷 → 回到阶段 1，修 `prd.md`，再重做 2.1
- 实现走偏 → 回退代码，重做 2.1
- 需要更多研究 → 研究（同阶段 1.2），把发现写入 `research/`

---

## 阶段 3：Finish（收束）

目标：确保代码质量，沉淀教训，记录工作。

#### 3.2 调试复盘 `[on demand]`

若本任务涉及反复调试（同一问题修了多次），加载 `trellis-break-loop` 技能以：

- 归类根因
- 解释为何更早的修复失败
- 提出预防措施

目标是沉淀调试教训，避免同类问题再次发生。

#### 3.3 规范更新 `[required · once]`

加载 `trellis-update-spec` 技能，并审视本任务是否产出了值得记录的新知识：

- 新发现的模式或约定
- 你踩过的坑
- 新的技术决策

相应更新 `.trellis/spec/` 下文档。即便结论是“无需更新”，也要走完判断过程。

#### 3.4 提交改动 `[required · once]`

**规范同步前导**：起草提交前先问：本任务是否修了 bug，或浮现了应落入 `.trellis/spec/` 的非显而易见知识，以免未来的你（或未来的 AI）再踩坑？若是，先回到阶段 3.3 —— 规范写入应落在同一任务的提交批次中，而不是被忘掉的后续。

AI 驱动对本任务代码改动的批量提交，以便之后 `/finish-work` 能干净运行。目标：先产出工作提交，再落记账提交（归档 + 日志）—— 绝不要交错。

**逐步操作**：

1. **检查脏状态**：
   ```bash
   git status --porcelain
   ```
   快照每个脏路径。若工作区干净，跳到 3.5。

2. **从近期历史学习提交风格**（让起草的信息风格一致）：
   ```bash
   git log --oneline -5
   ```
   注意前缀约定（`feat:` / `fix:` / `chore:` / `docs:` ...）、语言（中文/English）与长度风格。

3. **把脏文件分成两组**：
   - **本会话 AI 编辑过** —— 你在本会话通过 Edit/Write/Bash 工具写/改过的文件。你知道改了什么、为什么。
   - **未识别** —— 你本会话未碰过的脏文件（可能是用户手工编辑、上次会话残留 WIP，或无关工作）。不要静默把它们塞进提交。

4. **起草提交计划**。把 AI 编辑过的文件按逻辑分组提交（每个连贯改动单元 1 个提交，而不是每文件 1 个）。每项：`<commit message>` + 文件列表。未识别文件单独列在底部。

5. **一次性展示计划，并请求一次性确认**。格式：
   ```
   Proposed commits (in order):
     1. <message>
        - <file>
        - <file>
     2. <message>
        - <file>

   Unrecognized dirty files (NOT in any commit — confirm include/exclude):
     - <file>
     - <file>

   Reply 'ok' / '行' to execute. Reply with edits, or '我自己来' / 'manual' to abort.
   ```

6. **确认后**：按顺序对每批运行 `git add <files>` + `git commit -m "<msg>"`。不要 amend。不要 push。

7. **被拒绝时**（用户回复“不行” / “我自己来” / “manual” / 或任何对计划的反对）：停止。不要尝试第二套计划。用户会自己提交；他们确认后你跳到 3.5。

**规则**：

- 任何地方都不要 `git commit --amend` —— 三阶段三提交流（工作提交 → 归档提交 → journal 提交）。
- 本步绝不推远程。
- 若用户只想改提交信息措辞但接受文件分组，改措辞后再确认一次 —— 若他们拒绝分组，则退出到手工模式。
- 批量计划只问一次；不要每个提交都问。

#### 3.5 收尾提醒

完成以上后，提醒用户可运行 `/finish-work` 收尾（归档任务、记录会话）。

---

## 定制 Trellis（面向 fork）

本节面向想修改 Trellis 工作流本身的开发者。所有定制都通过编辑本文件完成；脚本只是解析器。

### 改一个步骤的含义

编辑上方阶段 1 / 2 / 3 中对应步骤的 walkthrough 正文。关键不变量：

- 无活跃任务时必须先分诊，并在创建任何 Trellis 任务前征求创建同意。
- 规划必须区分“只要 PRD 的轻量任务”与“start 前需要 `prd.md`、`design.md`、`implement.md` 的复杂任务”。
- 每条强制执行路径都必须保证阶段 3.4 的提交提醒在 `/trellis:finish-work` 之前可达。

所有标签块都在上方 `## Phase Index` 小节中，紧跟各阶段摘要：

| 范围 | 对应标签 |
|---|---|
| 无活跃任务（阶段 1 前） | `[workflow-state:no_task]`（阶段索引 ASCII 图之后） |
| 整个阶段 1（任务已创建 → 准备实现） | `[workflow-state:planning]`（阶段 1 摘要之后） |
| Codex inline 阶段 1 | `[workflow-state:planning-inline]` |
| 阶段 2 + 阶段 3.2–3.4（实现 + 检查 + 收束） | `[workflow-state:in_progress]`（阶段 2 摘要之后） |
| Codex inline 阶段 2 + 阶段 3.2–3.4 | `[workflow-state:in_progress-inline]` |
| 阶段 3.5 之后（已归档） | `[workflow-state:completed]`（阶段 3 摘要之后；**当前为 DEAD**） |

### 改每轮提示正文

直接编辑对应 `[workflow-state:STATUS]` 块的正文。编辑后，运行 `trellis update`（若你是模板维护者），或重启 AI 会话（若你在定制自己的项目）—— 不需要改脚本。

### 添加自定义状态

新增一个块：

```
[workflow-state:my-status]
your per-turn prompt text
[/workflow-state:my-status]
```

约束：

- STATUS 字符集：`[A-Za-z0-9_-]+`（允许下划线与连字符，例如 `in-review`、`blocked-by-team`）
- 必须有生命周期 hook 把 `task.json.status` 写成你的自定义值，否则标签永远不会被读到
- 生命周期 hook 位于 `task.json.hooks.after_*`，绑定到 `after_create / after_start / after_finish / after_archive` 之一

### 添加生命周期 hook

在你的 `task.json` 中加入 `hooks` 字段：

```json
{
  "hooks": {
    "after_finish": [
      "your-script-or-command-here"
    ]
  }
}
```

支持的事件：`after_create / after_start / after_finish / after_archive`。注意 `after_finish` ≠ 状态变更（它只清除活跃任务指针）；“任务做完了”的通知请用 `after_archive`。

### 完整契约

关于工作流状态机的运行时契约、所有状态写入点位置、伪状态（`no_task` / `stale_<source_type>`）、hook 可达性矩阵，以及其他深层细节，见：

- `.trellis/spec/cli/backend/workflow-state-contract.md` —— 运行时契约 + 写入表 + 测试不变量
- `.trellis/scripts/inject-workflow-state.py` —— 实际解析器（只读 workflow.md，无内嵌正文）
