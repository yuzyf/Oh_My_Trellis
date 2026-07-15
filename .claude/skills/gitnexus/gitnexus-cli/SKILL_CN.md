> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.claude/skills/gitnexus/gitnexus-cli/SKILL.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

---
name: gitnexus-cli
description: "在用户需要运行 GitNexus CLI 命令时使用，例如 analyze/index 仓库、查看 status、清理索引、生成 wiki，或列出已索引仓库。示例：\"Index this repo\"、\"Reanalyze the codebase\"、\"Generate a wiki\""
---

# GitNexus CLI 命令

下列命令使用 `node .gitnexus/run.cjs <command>` —— 项目本地 runner 会随 `gitnexus analyze` 写在索引旁。调用时会自动选择可用 runner（全局 `gitnexus`，否则 `pnpm dlx`，再否则 `npx`），因此不绑定特定包管理器，也不强制全局安装。

> **尚未分析，或 `node .gitnexus/run.cjs` 报 `Cannot find module`**（被 gitignore 的 runner 不存在——例如新 clone 或 `git clean`）？在项目根执行 `npx gitnexus analyze` 重新生成。在 **npm 11.x** 上，若 `npx` 安装时崩溃（`node.target is null`），可先 `npm i -g gitnexus`（再 `gitnexus analyze`），或使用 `pnpm --allow-build=@ladybugdb/core --allow-build=gitnexus --allow-build=tree-sitter dlx gitnexus@latest analyze`。见 [#1939](https://github.com/abhigyanpatwari/GitNexus/issues/1939)。

## 命令

### analyze — 构建或刷新索引

```bash
node .gitnexus/run.cjs analyze
```

在项目根运行。会解析全部源文件、构建知识图谱、写入 `.gitnexus/`，并生成 CLAUDE.md / AGENTS.md 上下文文件。

| Flag           | 效果                                                           |
| -------------- | ---------------------------------------------------------------- |
| `--force`      | 即使已是最新也强制全量重建索引                           |
| `--embeddings` | 启用 embedding 生成以支持语义搜索（默认关闭） |
| `--drop-embeddings` | 重建时丢弃已有 embeddings。默认情况下，不带 `--embeddings` 的 `analyze` 会保留它们。 |

**何时运行：** 项目第一次、大规模代码变更后，或 `gitnexus://repo/{name}/context` 报告索引过期时。在 Claude Code 中，PostToolUse hook 会在 `git commit` 与 `git merge` 后检测过期并通知 agent 运行 `analyze` —— hook 本身不跑 analyze，以免阻塞 agent 最长约 120s，并在超时时有 KuzuDB 损坏风险。

### status — 检查索引新鲜度

```bash
node .gitnexus/run.cjs status
```

显示当前仓库是否有 GitNexus 索引、上次更新时间，以及符号/关系数量。用来判断是否需要重新索引。

### clean — 删除索引

```bash
node .gitnexus/run.cjs clean
```

删除 `.gitnexus/` 目录，并从全局 registry 注销该仓库。在索引损坏需要重建前使用，或从项目移除 GitNexus 后使用。

| Flag      | 效果                                            |
| --------- | ------------------------------------------------- |
| `--force` | 跳过确认提示                          |
| `--all`   | 清理全部已索引仓库，不只是当前仓库 |

### wiki — 从图谱生成文档

```bash
node .gitnexus/run.cjs wiki
```

用 LLM 从知识图谱生成仓库文档。需要 API key（首次使用会保存到 `~/.gitnexus/config.json`）。

| Flag                | 效果                                    |
| ------------------- | ----------------------------------------- |
| `--force`           | 强制全量重新生成                   |
| `--model <model>`   | LLM 模型（默认：minimax/minimax-m2.5） |
| `--base-url <url>`  | LLM API base URL                          |
| `--api-key <key>`   | LLM API key                               |
| `--concurrency <n>` | 并行 LLM 调用数（默认：3）           |
| `--gist`            | 把 wiki 发布为公开 GitHub Gist      |

### list — 显示所有已索引仓库

```bash
node .gitnexus/run.cjs list
```

列出 `~/.gitnexus/registry.json` 中注册的全部仓库。MCP 的 `list_repos` 工具提供相同信息。

## 索引之后

1. **读取 `gitnexus://repo/{name}/context`** 以确认索引已加载
2. 用其他 GitNexus skills（`exploring`、`debugging`、`impact-analysis`、`refactoring`）完成你的任务

## 故障排查

- **"Not inside a git repository"**：在 git 仓库内的目录运行
- **重新 analyze 后索引仍显示过期**：重启 Claude Code 以重载 MCP server
- **Embeddings 很慢**：省略 `--embeddings`（默认关闭），或设置 `OPENAI_API_KEY` 以使用更快的 API embedding
