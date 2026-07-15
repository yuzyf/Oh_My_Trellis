> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.claude/skills/trellis-spec-bootstrap/references/repository-analysis.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

# 仓库分析（Repository Analysis）

目标是在写规则前发现项目的真实架构。不要从通用 spec 模板填空开始。从代码出发，再让规范结构跟上。

## 分析顺序

1. 阅读既有 `.trellis/spec/` 树，标出哪些是模板、过时或已项目化。
2. 检查包清单、构建脚本、workspace 配置与顶层文档，识别包与运行时层。
3. 用 GitNexus 找执行流、模块簇、依赖枢纽与影响敏感区域。
4. 用 ABCoder 或语言原生工具拿精确签名、类型、类边界与实现例子。
5. 在把任何发现变成 spec 规则前，直接读代表性源码与测试文件。

## 要捕获什么

| 区域 | 问题 |
|------|-----------|
| 包边界 | 每个包拥有什么？哪些导入跨边界？ |
| 运行时层 | 哪些代码是 CLI、backend、frontend、worker、共享库、仅测试或工具链？ |
| 核心抽象 | 哪些类型、服务、store、命令、路由或适配器定义系统形状？ |
| 数据流 | 用户输入从哪进入、如何校验、状态在哪持久化？ |
| 错误处理 | 失败如何表示、记录、上浮与测试？ |
| 配置 | 默认值、环境配置、生成文件与模板在哪？ |
| 测试 | 哪些测试风格是新工作可信赖的范例？ |

## GitNexus 用法

先广后深，再检查具体符号：

```text
gitnexus_query({query: "CLI command execution flow"})
gitnexus_query({query: "template generation and migration"})
gitnexus_context({name: "SymbolName"})
gitnexus_cypher({query: "MATCH (n)-[r]->(m) RETURN n.name, type(r), m.name LIMIT 30"})
```

用 GitNexus 结果找重要文件与流。在核对相关源文件之前，不要把图输出当最终权威引用。

## ABCoder 用法

当 spec 需要精确代码形状时用 ABCoder：

```text
list_repos()
get_repo_structure({repo_name: "package-name"})
get_file_structure({repo_name: "package-name", file_path: "src/example.ts"})
get_ast_node({repo_name: "package-name", node_ids: [{mod_path: "...", pkg_path: "...", name: "SymbolName"}]})
```

ABCoder 最适合文档化构造模式、函数签名、类型契约与引用链。

## 分析笔记

分析时保持短笔记，应包括：

- 包或层名。
- 定义本地模式的文件。
- spec 应教的规则。
- 在旧代码、注释、测试或迁移路径中发现的反模式。
- 应创建、删除、重命名或合并的 spec 文件。
