<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/local-architecture/generated-files.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 初始化后本地生成的文件（Local Files Generated After Init）

`trellis init` 会把 Trellis 运行时写入用户项目。之后 `trellis update` 会尝试更新由 Trellis 管理的模板文件，但它用 `.trellis/.template-hashes.json` 判断哪些文件已被用户改过。

本页只描述用户项目内可见、可编辑的文件。

## `.trellis/`

```text
.trellis/
├── workflow.md
├── config.yaml
├── .developer
├── .version
├── .template-hashes.json
├── .runtime/
├── scripts/
├── spec/
├── tasks/
└── workspace/
```

| Path | Usually editable? | Notes |
| --- | --- | --- |
| `.trellis/workflow.md` | Yes | 本地工作流文档与 AI 路由规则。 |
| `.trellis/config.yaml` | Yes | 项目配置：hooks、packages、journal 行数上限及相关设置。 |
| `.trellis/spec/` | Yes | 项目规范，预期由用户与 AI 定期更新。 |
| `.trellis/tasks/` | Yes | 任务材料与调研产物，由任务工作流维护。 |
| `.trellis/workspace/` | Yes | 会话记录，通常由 `add_session.py` 写入。 |
| `.trellis/scripts/` | Carefully | 本地运行时。可以定制，但需先理解调用链。 |
| `.trellis/.runtime/` | No | 运行时状态，通常由 hooks/scripts 自动写入。 |
| `.trellis/.developer` | Carefully | 当前开发者身份。 |
| `.trellis/.version` | No | Trellis 版本记录，供 update/migration 使用。 |
| `.trellis/.template-hashes.json` | No | 模板哈希记录。不要在这里手写业务规则。 |

## 平台目录（Platform Directories）

不同平台会生成不同目录。常见类别：

| Category | Example paths | Purpose |
| --- | --- | --- |
| hooks | `.claude/hooks/`、`.codex/hooks/`、`.cursor/hooks/` | 注入会话上下文、workflow-state 与子智能体上下文。 |
| settings | `.claude/settings.json`、`.codex/hooks.json`、`.qoder/settings.json` | 告诉平台何时运行 hooks 或 plugins。 |
| agents | `.claude/agents/`、`.codex/agents/`、`.kiro/agents/`、`.zcode/cli/agents/` | 定义如 `trellis-research`、`trellis-implement`、`trellis-check` 等 agent。 |
| skills | `.claude/skills/`、`.agents/skills/`、`.qoder/skills/` | 可自动触发或由 AI 读取的 skills。 |
| commands/prompts/workflows | `.cursor/commands/`、`.github/prompts/`、`.devin/workflows/`、`.zcode/commands/` | 用户显式调用的命令或工作流入口。 |

修改平台目录时，也要确认 `.trellis/workflow.md` 是否仍描述同一流程。

## 模板哈希的含义（Meaning Of Template Hashes）

`.trellis/.template-hashes.json` 记录 Trellis 上次写入模板文件时的内容哈希。`trellis update` 用它区分三种情形：

| Case | Update behavior |
| --- | --- |
| 文件未被用户修改 | 可自动更新。 |
| 文件已被用户修改 | 提示用户覆盖、保留，或生成 `.new`。 |
| 文件不再是当前模板 | 可能按迁移规则删除、重命名或保留。 |

AI 定制本地 Trellis 文件时，不必手动维护哈希。Trellis update 把结果识别为「用户已修改」是正常的。

## 本地定制边界（Local Customization Boundaries）

默认可编辑：

- `.trellis/workflow.md`
- `.trellis/config.yaml`
- `.trellis/spec/**`
- `.trellis/scripts/**`
- 平台 hooks、settings、agents、skills、commands、prompts 与 workflows

默认不要编辑：

- 全局 npm 安装目录
- `node_modules/@mindfoldhq/trellis`
- Trellis GitHub 仓库源码
- `.trellis/.runtime/**` 下的具体状态文件
- `.trellis/.template-hashes.json` 内的哈希内容

只有在用户明确要贡献上游时，才切换到 Trellis CLI 源码视角。
