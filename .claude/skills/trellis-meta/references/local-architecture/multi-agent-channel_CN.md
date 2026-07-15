<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/local-architecture/multi-agent-channel.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# 本地多智能体通道运行时（Local Multi-Agent Channel Runtime）

`trellis channel` 是随 Trellis CLI 发布的本地多智能体协作运行时。它让主 AI 会话生成对等 worker（Claude Code、Codex，或 `.trellis/agents/` 下的任意 agent 定义），通过事件日志交换持久消息，并协调评审或 brainstorm 循环，而不必手拼 shell 管道。

本参考说明通道如何接入用户项目，好让定制项目的 AI 知道改哪里。运行时用法（命令、forum/thread 模式、worker 生成标志）请交给捆绑的 `trellis-channel` 能力 skill。

## 本地系统模型（Local System Model）

通道运行时覆盖三块本地表面：

1. **存储层**，在用户主目录：持久事件日志与 worker 状态文件。
2. **Agent 定义**，在项目内 `.trellis/agents/`：平台无关的角色卡，供 `trellis channel spawn --agent <name>` 消费。
3. **项目配置**，在 `.trellis/config.yaml`：worker 防护阈值与其它 channel 旋钮。

## 核心路径（Core Paths）

| Path | Purpose |
| --- | --- |
| `~/.trellis/channels/<project>/<channel>/events.jsonl` | 每通道追加式事件日志。带序列锁，可安全回放。 |
| `~/.trellis/channels/<project>/<channel>/<channel>.lock` | 通道级写锁。 |
| `~/.trellis/channels/<project>/<channel>/<worker>.spawnlock` | 每 worker 的生成锁，供 OOM 防护使用。 |
| `~/.trellis/channels/<project>/<channel>/.seq` | 用于有序事件分配的序列侧车文件。 |
| `~/.trellis/channels/_global/<channel>/...` | 用 `--scope global` 创建的通道。项目桶被共享键替换。 |
| `.trellis/agents/check.md` | 默认 Check Agent 角色定义，供 `--agent check` 使用。 |
| `.trellis/agents/implement.md` | 默认 Implement Agent 角色定义，供 `--agent implement` 使用。 |
| `.trellis/config.yaml`（`channel.*` 块） | Worker 防护阈值与通道默认值。 |

项目桶名由绝对项目路径派生（斜杠展平，非字母数字替换为 `-`），与 Claude Code 的 `~/.claude/projects/<sanitized-cwd>/` 约定一致。测试或沙箱可用 `TRELLIS_CHANNEL_ROOT`（根目录）或 `TRELLIS_CHANNEL_PROJECT`（桶名）覆盖。

## 何时使用通道运行时（When To Reach For The Channel Runtime）

通道比单次 Bash 调用或一次性 sub-agent 派发更重。仅当至少满足下列之一时使用：

- 工作需要**两个或更多 agent 多轮对话**（跨 AI brainstorm、对等评审、调度器 + worker）。
- Worker 应以**对等进程**运行，主会话可中断、观察进度或异步等待。
- 对话必须**可持久、可事后检查**（forum/thread 通道、issue 板、决策轨迹）。
- 多个 worker 必须**共享同一事件日志**，才能看到彼此报告。

在这些情况下优先用更轻的原语：

- 一次 Bash 命令或一次 Agent 工具调用就够 -> 直接做。
- 用户只需要对某个文件做静态评审 -> 读文件后内联回复。
- 需要「记住上周讨论过什么」-> 用 `trellis mem`，而不是 channel。

## 可定制点（Customization Points）

| Need | Edit location |
| --- | --- |
| 修改默认通道 worker 空闲超时 | `.trellis/config.yaml` 中的 `channel.worker_guard.idle_timeout`。接受 `5m`、`30s` 等。设为 `0` 禁用空闲清理。 |
| 修改在线 worker 预算 | `.trellis/config.yaml` 中的 `channel.worker_guard.max_live_workers`。设为 `0` 禁用生成时预算检查。 |
| 按次覆盖 worker 防护 | 在 `trellis channel spawn` 上传 `--idle-timeout` / `--max-live-workers`，或设置环境变量 `TRELLIS_CHANNEL_WORKER_IDLE_TIMEOUT` / `TRELLIS_CHANNEL_MAX_LIVE_WORKERS`。 |
| 修改默认 Check 或 Implement worker 行为 | 编辑 `.trellis/agents/check.md` 或 `.trellis/agents/implement.md`。这些是平台无关角色卡；传入 `--agent check|implement` 时由通道运行时注入。 |
| 新增角色卡 | 把 `<name>.md` 放入 `.trellis/agents/`。`trellis channel spawn --agent <name>` 会拾取它。 |
| 迁移通道存储（CI 沙箱、临时运行） | 设置 `TRELLIS_CHANNEL_ROOT=/path/to/dir`。通道事件随之移动；已有通道仍留在旧根。 |
| 切换存储作用域 | 每个 channel 子命令传 `--scope project`（默认）或 `--scope global`。只改桶目录，其它不变。 |

Worker 防护优先级为：CLI 标志 > 环境变量 > `.trellis/config.yaml` > 内置默认。内置默认是 `idle_timeout: 5m` 与 `max_live_workers: 6`。

## 与其它本地层的关系（Relationship To Other Local Layers）

- **工作流层**：使用通道派发的工作流（如 `channel-driven-subagent-dispatch`）会指示主 agent 调用 `trellis channel spawn --agent check` 或 `--agent implement`，而不是平台 sub-agent。若缺少 `.trellis/agents/check.md` 或 `implement.md`，`trellis workflow --template <id>` 在安装时打印非阻塞警告。误删可用 `trellis update` 恢复。
- **任务层**：通道 worker 不拥有任务状态。监督用的主会话通过 worker inbox 传入活动任务路径；worker 从磁盘解析任务产物。
- **Spec 层**：worker 与主会话一样读取 `.trellis/spec/`。通道运行时不会绕过 spec 上下文加载。
- **平台集成层**：通道运行时是平台中立的，不依赖 `.claude/`、`.codex/` 或其它平台目录。规范化提供方输出的适配器（Claude `stream-json`、Codex `app-server`）在 Trellis CLI 二进制内部，不在项目里。
- **平台 sub-agent 文件 vs. 通道 worker**：编辑 `.claude/agents/trellis-implement.md`（及其它平台 `.X/agents/` 中的对等文件）**不会**改变通道运行时 worker 行为——通道 worker 加载的是 `.trellis/agents/<name>.md`。平台专属 agent 文件用于主 AI 会话直接派发 sub-agent，而不是通道生成的 worker。各平台 agent 表面见 `platform-files/agents.md`，以及 `trellis-meta/SKILL.md` 中固化该拆分的规则。

## 运行时用法（Runtime Usage）

命令语法、forum/thread 模式、worker 句柄、进度检查，以及 `--kind done` / `--kind turn_finished` 调度器等待模式，请加载捆绑的 `trellis-channel` skill（`trellis init` / `trellis update` 后会自动安装到各平台 skills 目录）。本参考只覆盖本地文件布局与定制旋钮；不重复可能随版本变化的命令语法。
