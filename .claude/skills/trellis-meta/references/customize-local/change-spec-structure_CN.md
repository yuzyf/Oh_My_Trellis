<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/customize-local/change-spec-structure.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 修改本地 Spec 结构（Change Local Spec Structure）

当用户想改 AI 遵守的工程约定、增加新的 spec 层，或调整 monorepo package 映射时，编辑 `.trellis/spec/` 与 `.trellis/config.yaml`。

## 先读这些文件（Read These Files First）

1. `.trellis/config.yaml`
2. `.trellis/spec/`
3. `.trellis/workflow.md` 中 planning artifact 指导与 Phase 3.3
4. 当前任务的 `implement.jsonl` / `check.jsonl`

## 常见需求（Common Needs）

| Need | Edit location |
| --- | --- |
| 增加 backend/frontend/docs/test spec 层 | `.trellis/spec/<layer>/` 或 `.trellis/spec/<package>/<layer>/` |
| 增加共享思考指南 | `.trellis/spec/guides/` |
| 调整 monorepo packages | `.trellis/config.yaml` 中的 `packages` |
| 改默认 package | `.trellis/config.yaml` 中的 `default_package` |
| 控制 spec 扫描范围 | `.trellis/config.yaml` 中的 `spec_scope` |
| 让任务读取新 spec | 任务的 `implement.jsonl` / `check.jsonl` |

## 增加 Spec 层（Add A Spec Layer）

单仓示例：

```text
.trellis/spec/security/
├── index.md
└── auth.md
```

Monorepo 示例：

```text
.trellis/spec/webapp/security/
├── index.md
└── auth.md
```

`index.md` 应包含：

- 该层适用于哪些代码。
- Pre-Development Checklist。
- Quality Check。
- 指向具体 guideline 文件的链接。

## 更新上下文（Update Context）

新增 spec 并不等于每个任务都会自动读取。当前任务必须在 JSONL 中引用它：

```bash
python3 ./.trellis/scripts/task.py add-context <task> implement ".trellis/spec/webapp/security/index.md" "Security conventions"
python3 ./.trellis/scripts/task.py add-context <task> check ".trellis/spec/webapp/security/index.md" "Security review rules"
```

## 修改 Monorepo Packages（Change Monorepo Packages）

`.trellis/config.yaml` 示例：

```yaml
packages:
  webapp:
    path: apps/web
  api:
    path: apps/api
default_package: webapp
```

编辑后运行：

```bash
python3 ./.trellis/scripts/get_context.py --mode packages
```

用输出确认 AI 能看到正确的 packages 与 spec 层。

## 注意（Notes）

- Specs 是用户项目约定，可按项目需要修改。
- 不要把临时任务信息放进 specs；临时信息放进 task。
- 不要只把长期约定写在 agents 或 commands 里；要沉淀到 specs。
- 改完 spec 结构后，检查已有任务 JSONL 是否仍指向存在的文件。
