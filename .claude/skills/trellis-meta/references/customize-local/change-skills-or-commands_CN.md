<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/customize-local/change-skills-or-commands.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 修改本地 Skills 或 Commands（Change Local Skills Or Commands）

当用户想增加 skill、slash command、prompt 或 workflow 入口时，改平台 skill/command 目录，并视需要同步 `.trellis/workflow.md`。

## 先读这些文件（Read These Files First）

1. 目标平台 skill/command/prompt/workflow 目录
2. `.trellis/workflow.md` 的 `Skill Routing`
3. 相关 `.trellis/scripts/`
4. 现有同类 skill/command 示例

## 先分清用户想改什么（First Distinguish What The User Wants）

| 用户意图 | 改哪里 |
| --- | --- |
| 增加一次性可调用入口 | 平台 command / prompt / workflow |
| 增加可复用 AI 能力 | 平台 skill |
| 改已有捆绑 skill 行为 | **不要**直接改项目里的捆绑副本；另建项目本地 skill，或贡献上游 |
| 改本地已有、但非捆绑的 skill | 直接改项目内该 skill |
| 把改动贡献回上游 | 改 Trellis CLI 仓库中的 `packages/cli/src/templates/common/bundled-skills/<name>/`，不是部署副本 |
| 改 Trellis 流程语义 | 同步 `.trellis/workflow.md` |

## 修改 Skill（Modify A Skill）

Skill 通常是：

```text
<skill-name>/
├── SKILL.md
└── references/
```

`SKILL.md` 应短，负责触发/路由。长内容放 `references/`，让 AI 按需读取。

frontmatter description 应说明何时使用该 skill。示例：

```yaml
description: "Use when customizing this project's deployment workflow and release checklist."
```

不要写「helpful project skill」这类模糊描述，容易误触发。

### 捆绑 vs 项目本地（Bundled vs. Project-Local）

同一目录形态对应两种截然不同的所有权模型：

| Aspect | Bundled（`trellis-meta`、`trellis-spec-bootstrap`、`trellis-session-insight`、`trellis-channel`） | Project-local |
| --- | --- | --- |
| 真相源 | Trellis CLI 仓库中的 `packages/cli/src/templates/common/bundled-skills/<name>/` | 用户项目内部 |
| 分发 | `trellis init` / `trellis update` 时由 `getBundledSkillTemplates()`（`packages/cli/src/templates/common/index.ts`）自动分发到各平台 skill 根 | 由用户（或其他 skill）创建，永不移动 |
| Hash 跟踪 | 每个文件记入 `.trellis/.template-hashes.json`；更新时冲突提示 | 不跟踪 |
| 本地编辑 | 允许，但下次更新会标为 “modified by user” | 可自由编辑 |
| 正确定制方式 | 新增一个**不同名字**的项目本地 skill，补充（或覆盖）捆绑 skill | 直接编辑文件 |

若目标是「讨论 release notes 时让本项目 AI 行为不同」，答案几乎总是项目本地 skill，而不是给 `trellis-meta/` 动刀。

## 修改 Command/Prompt/Workflow（Modify A Command/Prompt/Workflow）

显式入口应说明：

- 用户如何触发。
- 要读哪些 `.trellis/` 文件。
- 要跑哪些脚本。
- 完成后如何汇报。

若 command 只是重复 workflow 规则，优先让它引用/读取 `.trellis/workflow.md`，而不是维护第二份流程副本。

## 常见路径（Common Paths）

| Platform | Entry directories |
| --- | --- |
| Claude Code | `.claude/skills/`、`.claude/commands/` |
| Cursor | `.cursor/skills/`、`.cursor/commands/` |
| OpenCode | `.opencode/skills/`、`.opencode/commands/` |
| Codex | `.agents/skills/`、`.codex/skills/` |
| Gemini CLI | `.agents/skills/`、`.gemini/commands/` |
| Kiro | `.kiro/skills/` |
| Qoder | `.qoder/skills/`、`.qoder/commands/` |
| CodeBuddy | `.codebuddy/skills/`、`.codebuddy/commands/` |
| GitHub Copilot | `.github/skills/`、`.github/prompts/` |
| Factory Droid | `.factory/skills/`、`.factory/commands/` |
| Pi Agent | `.pi/skills/` |
| Reasonix | `.reasonix/skills/`（无独立 commands 目录；slash commands 内置于平台） |
| ZCode | `.agents/skills/`、`.zcode/commands/` |
| Kilo / Antigravity / Devin | workflows + skills |

上面每个目录都是四个捆绑 skills 的部署目标。`trellis init` 时各平台收到完整副本，`trellis update` 时刷新；无需手工接线。

## 添加项目本地 Skill（Add A Project-Local Skill）

若用户要记录团队私有定制，创建项目本地 skill——永远不要把项目私有内容放进捆绑 skill 目录，因为 `trellis update` 会覆盖。

```text
.claude/skills/project-trellis-local/
└── SKILL.md
```

多平台项目在各平台 skill 目录加等价版本，或在支持共享层的平台（Codex、Gemini CLI）使用 `.agents/skills/`。

选一个**不与**捆绑集合冲突的名字：

- `trellis-meta`
- `trellis-spec-bootstrap`
- `trellis-session-insight`
- `trellis-channel`

重名会导致下次更新时 `getBundledSkillTemplates()` 覆盖项目本地副本。常见约定是加项目前缀：`acme-trellis-deploy`、`acme-trellis-onboarding`。

## 注意（Notes）

- 不要把各平台语法混进一个文件。
- 不要只改一个平台入口却声称全平台支持。
- 不要把长期工程约定藏在 command 里；写到 `.trellis/spec/`。
- 不要指望在任意 `.{platform}/skills/` 下手改 `trellis-meta/`、`trellis-spec-bootstrap/`、`trellis-session-insight/`、`trellis-channel/` 的文件能持久——它们是捆绑的，会被 `trellis update` 刷新。要么贡献上游，要么新增互补的项目本地 skill。
- `trellis update` 对捆绑 skill 文件报告 “modified by you” 冲突时，只有在你接受手工维护分叉时才选 **keep**；否则接受覆盖，把意图重新做成项目本地 skill。
