> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.claude/skills/trellis-spec-bootstrap/SKILL.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

---
name: trellis-spec-bootstrap
description: "从真实仓库结构引导生成项目专属 `.trellis/spec/`。在用户想初始化、刷新或用真实代码模式重建 specs，而不是留下模板占位时使用。"
---

# Trellis Spec Bootstrap

从仓库证据写出项目专属 `.trellis/spec/` 指南。不要从通用模板填空开始。先读代码，再让规范结构跟上。

## 目标

- 发现真实包边界、运行时层与本地模式
- 用具体例子与反模式替换模板占位
- 产出未来 agent 能直接执行的 specs

## 流程

1. 阅读既有 `.trellis/spec/`，标出模板、过时与已项目化的文件
2. 检查包清单、构建脚本、workspace 配置与顶层文档
3. 用 GitNexus / ABCoder（若可用）找执行流、签名与依赖枢纽——见 `references/mcp-setup.md` 与 `references/repository-analysis.md`
4. 直接读代表性源码与测试
5. 围绕真实所有权边界规划 spec 工作——见 `references/spec-task-planning.md`
6. 从证据写 specs——见 `references/spec-writing.md`
7. 最终检查：去掉占位、对齐 index、用源文件/测试/文档支撑断言

## 规则

- 按真实代码库调整 spec 文件集合
- 用带文件路径的真实源码例子
- 删除不适用的仅模板小节
- 除非任务明确要求，否则不要改产品源码
- 不要编码某一 agent 宿主专属的工具仪式

## 验收

- [ ] Specs 含来自本仓库的具体例子与反模式
- [ ] 无占位文字残留
- [ ] index 文件与最终 spec 文件一致
- [ ] 断言有源文件、测试或项目文档支撑
