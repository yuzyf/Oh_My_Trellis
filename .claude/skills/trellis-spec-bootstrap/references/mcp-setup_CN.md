> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.claude/skills/trellis-spec-bootstrap/references/mcp-setup.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

# MCP 配置（MCP Setup）

可选但推荐：配置 GitNexus 与 ABCoder，加速仓库分析。

## GitNexus

GitNexus 构建本地代码智能图谱。对执行流、模块簇、依赖枢纽与影响敏感区域最有用。

### 安装与索引

```bash
# Index the current repository.
npx gitnexus analyze

# Check index status.
npx gitnexus status

# Re-index after code changes when the analysis is stale.
npx gitnexus analyze
```

索引写入 `.gitnexus/`。仅当项目已使用 embeddings 时再保留它们；否则普通索引对 spec bootstrap 已够用。

### MCP Server 命令

在宿主的 MCP 配置中使用：

```bash
npx -y gitnexus mcp
```

### 有用工具

| 工具 | 用途 |
|------|---------|
| `gitnexus_query` | 按概念找执行流与功能区域 |
| `gitnexus_context` | 检查符号的调用方、被调用方、引用与进程参与 |
| `gitnexus_impact` | 改符号前理解爆炸半径 |
| `gitnexus_detect_changes` | 结束前检查变更符号与受影响流 |
| `gitnexus_cypher` | 直接跑图查询 |
| `gitnexus_list_repos` | 列出已索引仓库 |

## ABCoder

ABCoder 把代码解析为 UniAST，提供精确的包、文件与节点级结构。用于签名、类型形状、实现、依赖与反向引用。

### 安装

```bash
go install github.com/cloudwego/abcoder@latest
abcoder --help
```

### 解析仓库

```bash
abcoder parse /absolute/path/to/package \
  --lang typescript \
  --name package-name \
  --output ~/abcoder-asts
```

对 monorepo，用稳定的 `--name` 解析每个包，以便任务笔记引用同一仓库名。

### MCP Server 命令

在宿主的 MCP 配置中使用：

```bash
abcoder mcp ~/abcoder-asts
```

### 有用工具

| 工具 | 层 | 用途 |
|------|-------|---------|
| `list_repos` | 1 | 列出已解析仓库 |
| `get_repo_structure` | 2 | 检查包与文件 |
| `get_package_structure` | 3 | 检查包内节点 |
| `get_file_structure` | 3 | 检查文件中的函数、类、类型与签名 |
| `get_ast_node` | 4 | 取代码、依赖、引用与实现 |

## 校验

配置后，从 agent 宿主确认两个 MCP server 可见。然后在开始写 spec 前，对每个 server 跑一个简单查询。

```bash
ls .gitnexus/meta.json
ls ~/abcoder-asts/*.json
```
