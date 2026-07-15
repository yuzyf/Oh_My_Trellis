<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/local-architecture/spec-system.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 本地 Spec 系统（Local Spec System）

`.trellis/spec/` 是用户项目专属的工程规范库。Trellis 的目标不是让 AI「背住约定」，而是在正确时机注入相关 spec，或要求 AI 主动去读。

## 目录模型（Directory Model）

常见单仓库结构：

```text
.trellis/spec/
├── backend/
│   ├── index.md
│   └── ...
├── frontend/
│   ├── index.md
│   └── ...
└── guides/
    ├── index.md
    └── ...
```

常见 monorepo 结构：

```text
.trellis/spec/
├── cli/
│   ├── backend/
│   │   ├── index.md
│   │   └── ...
│   └── unit-test/
│       ├── index.md
│       └── ...
├── docs-site/
│   └── docs/
│       ├── index.md
│       └── ...
└── guides/
    ├── index.md
    └── ...
```

`index.md` 是每一层的入口。它应列出 Pre-Development Checklist 与 Quality Check；具体指南放在同目录其它 Markdown 文件里。

## 包配置（Package Configuration）

`.trellis/config.yaml` 可声明 packages：

```yaml
packages:
  cli:
    path: packages/cli
  docs-site:
    path: docs-site
    type: submodule
default_package: cli
```

AI 可运行：

```bash
python3 ./.trellis/scripts/get_context.py --mode packages
```

该命令会列出当前项目的 packages 与 spec 分层。配置上下文 JSONL 时，以这份输出为准。

## Spec 如何进入任务（How Specs Enter Tasks）

任务进入实现前，若除任务产物外还需要 spec 或调研上下文，规划阶段可把相关 spec 写入 `implement.jsonl` / `check.jsonl`：

```jsonl
{"file": ".trellis/spec/cli/backend/index.md", "reason": "CLI backend conventions"}
{"file": ".trellis/spec/cli/unit-test/conventions.md", "reason": "Test expectations"}
```

子智能体（sub-agent）或平台 prelude 会读取这些 JSONL 并加载引用的 spec。不支持 sub-agent 的平台上，AI 应按 workflow 直接阅读相关 spec。

## Spec 应包含什么（What Specs Should Contain）

Spec 应写项目可执行的工程约定，而不是泛泛的最佳实践：

- 文件应放在哪里。
- 错误处理应如何表达。
- API、hook、命令的输入/输出契约。
- 禁止使用的模式。
- 必须写测试的情形。
- 项目特有的坑与规避方式。

当 AI 在实现或调试中学到新规则时，应更新 `.trellis/spec/`，而不是只在聊天里总结。

## 本地可定制点（Local Customization Points）

| Need | Edit location |
| --- | --- |
| 新增 spec 层 | `.trellis/spec/<package>/<layer>/index.md` 及对应指南文件。 |
| 修改 monorepo 的 spec 映射 | `.trellis/config.yaml` 中的 `packages` / `default_package` / `spec_scope`。 |
| 修改实现前 AI 要读的 spec | 任务的 `implement.jsonl`。 |
| 修改检查时 AI 要读的 spec | 任务的 `check.jsonl`。 |
| 修改何时应更新 spec | `.trellis/workflow.md` 的 Phase 3.3 与 `trellis-update-spec` skill。 |

## 边界（Boundaries）

`.trellis/spec/` 是用户的项目规范，不是 Trellis 内置模板的永久拷贝。AI 应鼓励用户按真实项目代码更新它，而不是把 Trellis 默认模板当成不可改文档。
