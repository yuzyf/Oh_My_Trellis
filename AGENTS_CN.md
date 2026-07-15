> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`AGENTS.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

<!-- TRELLIS:START -->
# Trellis 说明

这些说明面向在本项目中工作的 AI 助手。

本项目由 Trellis 管理。你需要的工作知识都在 `.trellis/` 下：

- `.trellis/workflow.md` — 开发阶段、何时创建任务、技能路由
  - 中文对照：`.trellis/workflow_CN.md`
- `.trellis/spec/` — 按包（package）与层（layer）划分的编码规范（在对应层写代码前先读）
- `.trellis/workspace/` — 每位开发者的日志与会话记录
- `.trellis/tasks/` — 进行中与已归档的任务（PRD、研究材料、jsonl 上下文）

若当前平台提供 Trellis 命令（例如 `/trellis:finish-work`、`/trellis:continue`），优先用命令，而不是手工逐步操作。并非每个平台都暴露全部命令。

若你使用 Codex 或其他具备 Agent 能力的工具，项目级辅助能力还可能在：

- `.agents/skills/` — 可复用的 Trellis 技能
- `.codex/agents/` — 可选的自定义子代理

由 Trellis 管理。本块之外的编辑会保留；本块之内的编辑可能在后续 `trellis update` 时被覆盖。

<!-- TRELLIS:END -->

<!-- gitnexus:start -->
# GitNexus — 代码智能

本项目已被 GitNexus 索引为 **Trellis**（14336 个符号、20870 条关系、300 条执行流）。请使用 GitNexus 的 MCP 工具理解代码、评估影响，并安全导航。

> 索引过期？在项目根目录运行 `node .gitnexus/run.cjs analyze` —— 它会自动选择可用的 runner。还没有 `.gitnexus/run.cjs`？用 `npx gitnexus analyze`（npm 11 崩溃 → `npm i -g gitnexus`；#1939）。

## 必须做

- **修改任何符号前必须先做影响分析（impact analysis）。** 在改函数、类或方法前，运行 `impact({target: "symbolName", direction: "upstream"})`，并向用户报告爆炸半径（直接调用方、受影响流程、风险等级）。
- **提交前必须运行 `detect_changes()`**，确认你的改动只影响预期符号与执行流。做回归审查时，与默认分支对比：`detect_changes({scope: "compare", base_ref: "main"})`。
- 若影响分析返回 HIGH 或 CRITICAL 风险，**必须先警告用户**，再继续修改。
- 探索陌生代码时，用 `query({query: "concept"})` 找执行流，而不是盲搜。它会按流程分组、按相关度排序返回结果。
- 需要某个符号的完整上下文 —— 调用方、被调用方、它参与哪些执行流 —— 时，使用 `context({name: "symbolName"})`。

## 禁止做

- 未先对函数/类/方法运行 `impact`，绝不要直接改。
- 绝不要忽略影响分析给出的 HIGH 或 CRITICAL 风险警告。
- 绝不要用查找替换重命名符号 —— 要用理解调用图的 `rename`。
- 提交前绝不要跳过 `detect_changes()` 来检查影响范围。

## 资源

| 资源 | 用途 |
|----------|---------|
| `gitnexus://repo/Trellis/context` | 代码库总览，检查索引是否新鲜 |
| `gitnexus://repo/Trellis/clusters` | 全部功能分区 |
| `gitnexus://repo/Trellis/processes` | 全部执行流 |
| `gitnexus://repo/Trellis/process/{name}` | 逐步执行轨迹 |

## CLI

| 任务 | 阅读该技能文件 |
|------|---------------------|
| 理解架构 / “X 怎么工作？” | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| 爆炸半径 / “改 X 会坏什么？” | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| 追踪 bug / “为什么 X 失败？” | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| 重命名 / 抽取 / 拆分 / 重构 | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| 工具、资源、schema 参考 | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| 索引、状态、清理、wiki CLI 命令 | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
