> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.agents/skills/trellis-before-dev/SKILL.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

---
name: trellis-before-dev
description: "在开始实现前，从 .trellis/spec/ 发现并注入项目专属编码规范。读取目标包的规范索引、开发前检查清单与共享思考指南。在启动新编码任务、写任何代码前、切换到不同包，或需要刷新项目约定与标准时使用。"
---

在开始任务前，先阅读相关开发规范。

执行下列步骤：

1. **读取当前任务产物**：
   - `prd.md`：需求与验收标准
   - 若有 `design.md`：技术设计
   - 若有 `implement.md`：执行顺序与验证计划

2. **发现包及其规范层**：
   ```bash
   python3 ./.trellis/scripts/get_context.py --mode packages
   ```

3. **根据任务判断适用哪些规范**，依据包括：
   - 你在改哪个包（例如 `cli/`、`docs-site/`）
   - 工作类型（backend、frontend、unit-test、docs 等）
   - 任务产物中引用的任何 spec/research 路径

4. **阅读每个相关模块的规范索引**：
   ```bash
   cat .trellis/spec/<package>/<layer>/index.md
   ```
   跟随索引里的 **“Pre-Development Checklist”（开发前检查清单）** 部分。

5. **阅读开发前检查清单中与本任务相关的具体规范文件**。索引本身不是目标 —— 它指向真正的规范文件（例如 `error-handling.md`、`conventions.md`、`mock-strategies.md`）。读这些文件，弄清编码标准与模式。

6. **始终阅读共享指南**：
   ```bash
   cat .trellis/spec/guides/index.md
   ```

7. 理解你需要遵循的编码标准与模式，然后继续你的开发计划。

写任何代码前，这一步**强制**。

> 译注：在 Codex inline 路径里，这是阶段 2 的“注入规范”入口；子代理分派路径则更多靠 `implement.jsonl` / `check.jsonl` 注入上下文。
