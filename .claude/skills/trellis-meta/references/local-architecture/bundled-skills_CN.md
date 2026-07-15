<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/local-architecture/bundled-skills.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 捆绑 Skills（Bundled Skills）

「捆绑 skills（bundled skills）」是随 Trellis CLI npm 包一起发布的多文件内置 skill。与 marketplace skill（用户单独装到自己的 `.claude/skills/` 或其它平台 skill 根）不同，捆绑 skills 会由 `trellis init` 自动写入每个支持平台的 skill 根，并由 `trellis update` 保持同步。它们是 Trellis 本身的一部分，不是第三方内容。

捆绑 skill 是位于 `packages/cli/src/templates/common/bundled-skills/<skill>/` 下的目录，已包含自己的 `SKILL.md`（带 YAML frontmatter）以及可选的 `references/`、assets 或其它支撑文件。Trellis 把整棵目录树原样复制到各平台 skill 根，因此 references 可保持懒加载，而不是被压成一份过大的 `SKILL.md`。

## 什么算捆绑（相对邻近概念）（What Counts As Bundled）

| Source path | Type | How it ships |
| --- | --- | --- |
| `templates/common/bundled-skills/<name>/` | 捆绑 skill（多文件） | 整目录复制到每个平台 skill 根 |
| `templates/common/skills/<name>.md` | 单文件工作流 skill | 包上 frontmatter，写成 `<root>/<name>/SKILL.md` |
| `templates/common/commands/<name>.md` | Slash 命令 / prompt | 写入各平台命令目录（`.claude/commands/trellis/`、`.cursor/commands/trellis-*.md`、`.gemini/commands/trellis/*.toml` 等） |
| `templates/<platform>/skills/` | 平台专属 skill | 只写入该平台目录（例如 `.codex/skills/`） |
| 用户 skills，位于 `.claude/skills/<my-skill>/` 等 | Marketplace 或用户自写 | Trellis 完全不管 |

Trellis CLI 绝不会触碰不是由它自己的模板加载器产出的内容。用户手丢进平台 skill 根的东西会被原样留下。

## 当前捆绑 Skills（v0.6.0）（Current Bundled Skills）

集合通过枚举 `templates/common/bundled-skills/` 下的目录在运行时发现：

| Skill | Purpose |
| --- | --- |
| `trellis-meta` | 本 skill。向在用户项目内工作的 AI 解释本地 Trellis 架构与定制入口。 |
| `trellis-session-insight` | 封装 `trellis mem` CLI，让 AI 知道何时、如何触及过去的 Claude Code / Codex / Pi Agent 对话日志。 |
| `trellis-spec-bootstrap` | 平台中立工作流，从真实代码库创建或刷新 `.trellis/spec/`（可选 GitNexus / ABCoder 集成）。 |
| `trellis-channel` | 能力 skill，教 AI 何时使用 `trellis channel` 做多智能体协作、forum/thread 持久板与调度器等待模式。 |

列表在运行时发现，因此在 `bundled-skills/` 下新增目录就是注册新 skill 的唯一步骤（见下文「添加新捆绑 Skill」）。

## 各平台落点（Where Bundled Skills Land Per Platform）

每个平台配置器在 `trellis init` 期间调用 `writeSkills(<root>, <workflowSkills>, resolveBundledSkills(ctx))`。`resolveBundledSkills` 读取 `templates/common/bundled-skills/` 下每个目录，解析占位符，并返回扁平的 `{relativePath, content}` 列表。`writeSkills` 再把它们镜像到平台 skill 根下。

| Platform | Bundled skill root | Notes |
| --- | --- | --- |
| Claude Code | `.claude/skills/<skill>/` | `configureClaude` |
| Cursor | `.cursor/skills/<skill>/` | `configureCursor` |
| Codex | `.agents/skills/<skill>/` | `configureCodex` 写入共享的 `.agents/skills/` 根，Gemini CLI 0.40+ 也读它 |
| Gemini CLI | `.agents/skills/<skill>/` | 与 Codex 同一共享根；两个配置器必须产出字节级相同的输出 |
| Kiro | `.kiro/skills/<skill>/` | `configureKiro`（基于 skills 的平台——无 commands） |
| Qoder | `.qoder/skills/<skill>/` | `configureQoder` |
| Codebuddy | `.codebuddy/skills/<skill>/` | `configureCodebuddy` |
| Copilot | `.github/skills/<skill>/` | `configureCopilot` |
| Droid | `.factory/skills/<skill>/` | `configureDroid` |
| Antigravity | `.agent/skills/<skill>/` | `configureAntigravity` |
| Devin | `.devin/skills/<skill>/` | `configureDevin` |
| Kilo | `.kilocode/skills/<skill>/` | `configureKilo` |
| OpenCode | （由 `collectOpenCodeTemplates` 处理） | 使用同一 `resolveBundledSkills(ctx)` 输出 |
| Pi, Reasonix | （各自 collector） | 同一 `resolveBundledSkills(ctx)` 输出 |

两条路径使用同一数据：

1. `configureX(cwd)` 在 `trellis init` 期间写文件。
2. `collectPlatformTemplates(platformId)`（在 `configurators/index.ts`）返回 `Map<filePath, content>`，供 `trellis update` 检测漂移并填充 `.trellis/.template-hashes.json`。两者必须产出字节级相同的输出，因此都调用 `resolveBundledSkills(ctx)` 与 `collectSkillTemplates(root, …, resolveBundledSkills(ctx))`。

## 派发接线（代码路径）（Dispatch Wiring）

把捆绑 skills 自动派发到平台 skill 根的机制在两个文件中：

1. `packages/cli/src/templates/common/index.ts`
   - `listDirectories("bundled-skills")` 枚举磁盘上的 skills。
   - `listBundledSkillFiles(skillDir)` 递归遍历每个 skill 目录，为每个文件返回 `{relativePath, content}`。
   - `getBundledSkillTemplates()` 返回缓存的 `CommonBundledSkill[]`。

2. `packages/cli/src/configurators/shared.ts`
   - `resolveBundledSkills(ctx)` 把该列表展平为带 `<skill>/<relativePath>` 路径且已解析占位符的 `ResolvedSkillFile[]`。
   - `writeSkills(skillsRoot, workflowSkills, bundledSkills)` 在 `skillsRoot` 下同时写入工作流 skills 与捆绑 skill 文件。
   - `collectSkillTemplates(skillsRoot, workflowSkills, bundledSkills)` 为 update / 哈希流水线返回同形的 `Map<filePath, content>`。

每个支持 skills 的平台配置器都导入这两个 helper（见 `claude.ts`、`cursor.ts`、`codex.ts`、`gemini.ts`、`kiro.ts`、`qoder.ts`、`codebuddy.ts`、`copilot.ts`、`droid.ts`、`antigravity.ts`、`devin.ts`、`kilo.ts`）。`index.ts` 的 `PLATFORM_FUNCTIONS` 注册表也在每个 `collectTemplates` 闭包内调用 `resolveBundledSkills(ctx)`，以保持 `trellis update` 跟踪一致。

## 添加新捆绑 Skill（Adding a New Bundled Skill）

形状与派发接线已经通用，因此添加 skill 只需要文件变更加发布校验。

1. **创建目录树。**

   ```
   packages/cli/src/templates/common/bundled-skills/<my-skill>/
     SKILL.md                     # YAML frontmatter + body
     references/                  # optional
       <topic>.md
     assets/                      # optional (anything readable as utf-8)
   ```

2. **写合法的 `SKILL.md` 头。** frontmatter 至少包含：

   ```yaml
   ---
   name: <my-skill>
   description: "When the AI should reach for this skill. Triggering phrases go here."
   ---
   ```

   `description` 是各平台自动触发机制匹配的依据，因此应描述用户意图触发词，而不是 skill 内部细节。

3. **在合适处使用占位符。** 捆绑 skill 内容会经过 `resolvePlaceholders(file.content, ctx)`。`resolvePlaceholders` 支持的任何 `{{platform_name}}`、`{{python_cmd}}` 等 token 都会按平台替换。

4. **不需要派发接线。** `listDirectories("bundled-skills")` 会自动发现新目录，因此下次 `trellis init` 或 `trellis update` 时所有平台都会收到它。

5. **发货前验证分发路径。** 历史上跳过任一步都曾导致功能文档写了「已捆绑」，但发布的 npm tarball 缺文件：

   - 源文件存在于即将打 tag 的分支。
   - `pnpm --filter @mindfoldhq/trellis build` 把资源复制到 `dist/templates/common/bundled-skills/<skill>/`。
   - `npm pack --dry-run --json` 包含期望的 `dist/**` 路径。
   - 在全新临时项目中，`trellis init` 会写入 `.claude/skills/<skill>/SKILL.md`、`.agents/skills/<skill>/SKILL.md` 等。
   - `.trellis/.template-hashes.json` 列出生成的文件。
   - 该临时项目中 `trellis update --dry-run` 报告 "Already up to date!"。

6. **若 skill 出现在其它项目将升级到的版本中，添加迁移清单条目。** 没有显式清单条目时，文件仍会通过 `trellis update` 的标准「缺失文件」分支落地，但清单会让变更出现在 changelog 中。

## 在本地覆盖捆绑 Skill（Overriding a Bundled Skill Locally）

没有正式的「项目本地 skill」机制（例如 `.trellis/skills/`）。捆绑 skills 以平台为根，因此覆盖也以平台为根。

受支持的模式依赖 `trellis update` 已有的模板哈希差异：

1. 直接编辑本地文件。例如：`.claude/skills/trellis-meta/SKILL.md`。
2. 文件哈希与 `.trellis/.template-hashes.json` 中的条目偏离。
3. 下次 `trellis update` 检测到用户修改并保持文件不动（没有显式 `--force` 时，Trellis 从不覆盖用户改过的文件）。

注意：

- 覆盖只作用于你编辑的那个平台目录。若要在例如 Claude Code 与 Codex 上覆盖同一 skill，必须同时编辑 `.claude/skills/<name>/` 与 `.agents/skills/<name>/`。
- 未来的 `trellis update --force` 会覆盖本地编辑。把覆盖纳入版本控制，以便需要时重新应用。
- 以不同文件夹名装在同一平台 skill 根下的 marketplace skill（例如 `.claude/skills/my-custom-meta/`）不会被 Trellis 触碰；当目标是增加行为而不是改捆绑 skill 时，这是更干净的选项。
- 团队私有约定应放在 `.trellis/spec/` 或独立的 marketplace 风格本地 skill 中，而不是改 `trellis-meta` 本身。见 `customize-local/add-project-local-conventions.md`。

## 从项目中移除捆绑 Skill（Removing a Bundled Skill From a Project）

捆绑 skills 没有按项目的 opt-out 标志。两种做法：

1. **在每个平台 skill 根删除该目录。** `trellis update` 会看到文件缺失，对照 `.template-hashes.json`，并把删除当作其它用户修改一样处理——除非传入 `--force`，否则不会静默重建目录。

2. **钉在未发布该 skill 的 Trellis 版本。** 捆绑 skill 集合在构建时确定，因此安装较旧的 CLI 发布版是永久排除当前发布版 skill 的唯一方式。

第三种选项——全局禁用所有捆绑 skills——不受支持。每个配置器中的派发都是无条件的。增加这类标志需要改 `configurators/index.ts` 中的 `PLATFORM_FUNCTIONS` 以及每个 `configureX` 函数。

## 操作规则（Operating Rules）

- 把 `templates/common/bundled-skills/` 当作「存在哪些捆绑 skills」的唯一事实来源。不要按平台手维护 skill 列表。
- 不要在捆绑 `SKILL.md` 内加入平台专属逻辑。若行为是平台专属的，放到 `templates/<platform>/skills/`。
- 不要把捆绑 skills 与特定 CLI 二进制（例如 `trellis mem`）耦合，却不在 skill 的 description 与 references 中暴露依赖——旧发布版用户可能没有该命令。
- 不要把项目私有内容放进捆绑 skill。捆绑 skills 是公开的，会发给每个用户；项目规则属于 `.trellis/spec/` 或本地 skill。
