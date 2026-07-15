> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.claude/skills/trellis-spec-bootstrap/references/spec-writing.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

# Spec 写作（Spec Writing）

Trellis specs 是给未来 agent 的编码指南。它们应解释如何在本仓库工作，而不是泛化项目可能如何组织。

## 从证据写

每条重要规则应有以下之一支撑：

- 展示首选模式的源文件。
- 展示期望行为的测试文件。
- 定义约定的项目文档。
- 跨多个文件重复出现的模式。

仅在短片段能让规则更清楚时使用。优先链到文件路径并点名符号或行为。

## 文件结构

让 spec 树与项目对齐：

- 保留 `index.md` 作为规范目录的导航文件。
- 开发者会独立查找时再拆主题。
- 分文件会重复同一规则时合并主题。
- 删除不适用的模板文件。
- 为模板漏掉的重要本地模式新增文件。

## 内容标准

好的 spec 小节包括：

- 规则何时适用。
- 要遵循的本地模式。
- 证明该模式的源码或测试文件。
- 常见错误或反模式。
- 具体且可靠的校验命令或检查。

避免：

- 占位散文。
- 通用框架建议。
- 只在某一 agent 宿主上成立的工具说明。
- 大段复制代码块。
- 基于单个偶然实现细节的规则。

## 示例形状

```markdown
## Command Handlers

Command handlers should keep argument parsing, validation, and side effects separate. The local pattern is:

- Parse CLI flags at the command boundary.
- Convert raw inputs into typed task options before invoking core logic.
- Keep filesystem writes in the command or service layer, not in template helpers.

Reference files:
- `packages/cli/src/commands/example.ts`
- `packages/cli/test/commands/example.test.ts`

Avoid passing raw `process.argv` or unvalidated config objects into shared helpers.
```

## 最终检查

结束前：

```bash
grep -R "To be filled\\|TODO: fill\\|placeholder" .trellis/spec
```

同时检查链接、index 文件，以及是否还有 spec 在描述模板而不是本仓库。
