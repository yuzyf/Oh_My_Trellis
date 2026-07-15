<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/claude-code/ralph-loop.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# Ralph Loop

面向 Check Agent 的质量强制机制。

---

## 概述（Overview）

Ralph Loop 在全部验证命令通过前，阻止 Check Agent 停止。

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           RALPH LOOP                                     │
│                                                                          │
│  Check Agent completes                                                   │
│         │                                                                │
│         ▼                                                                │
│  SubagentStop hook fires ──► ralph-loop.py runs                         │
│         │                                                                │
│         ▼                                                                │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Run verify commands from worktree.yaml:                         │    │
│  │                                                                  │    │
│  │    pnpm lint        → exit 0 ✓                                   │    │
│  │    pnpm typecheck   → exit 0 ✓                                   │    │
│  │    pnpm test        → exit 1 ✗                                   │    │
│  │                                                                  │    │
│  │  Result: FAIL (test failed)                                      │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│         │                                                                │
│         ▼                                                                │
│  ┌─────────────────┐              ┌─────────────────┐                   │
│  │   All pass?     │──── YES ────►│  Allow stop     │                   │
│  └────────┬────────┘              └─────────────────┘                   │
│           │ NO                                                           │
│           ▼                                                              │
│  ┌─────────────────┐                                                    │
│  │  Block stop     │ ◄─── Agent continues to fix issues                 │
│  │  Inject errors  │                                                    │
│  └─────────────────┘                                                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 配置（Configuration）

### `worktree.yaml`

```yaml
verify:
  - pnpm lint
  - pnpm typecheck
  # - pnpm test
  # - pnpm build
```

---

## 常量（Constants）

| Constant | Value | Description |
|----------|-------|-------------|
| `MAX_ITERATIONS` | 5 | 最大循环次数 |
| `STATE_TIMEOUT_MINUTES` | 30 | 状态文件超时 |
| `COMMAND_TIMEOUT` | 120s | 每条命令超时 |

---

## 状态文件（State File）

### `.trellis/.ralph-state.json`

跨迭代跟踪循环状态。

```json
{
  "task": ".trellis/tasks/01-31-add-login",
  "iteration": 2,
  "started_at": "2026-01-31T10:30:00"
}
```

---

## 流程（Flow）

### 第 1 次迭代（Iteration 1）

1. Check Agent 完成工作
2. SubagentStop hook 触发
3. `ralph-loop.py` 创建状态文件（iteration=1）
4. 运行验证命令
5. 若失败：阻塞停止，注入错误信息
6. Check Agent 继续修复

### 第 2–5 次迭代（Iteration 2-5）

1. Check Agent 再次尝试停止
2. Hook 读取状态文件并递增 iteration
3. 再次运行验证命令
4. 直到通过或达到最大迭代次数

### 达到最大迭代（Max Iterations Reached）

1. 第 5 次仍失败
2. Hook 允许停止（防止无限循环）
3. 记录关于未解决问题的警告

### 超时（Timeout）

1. 状态文件超过 30 分钟
2. Hook 重置状态（重新开始）
3. 当作第 1 次迭代处理

---

## 验证命令（Verify Commands）

### 执行顺序（Execution Order）

命令按配置顺序运行。第一次失败即停止后续执行。

```yaml
verify:
  - pnpm lint        # Runs first (fast)
  - pnpm typecheck   # Runs second
  - pnpm test        # Runs third (slow)
```

**建议**：按 快 → 慢 排序

### 退出码（Exit Codes）

- Exit 0 = 通过
- 非零 = 失败

### 超时（Timeout）

每条命令 120 秒超时。长时间测试可能需要：
- 拆成更小的测试套件
- 在 Ralph Loop 中只跑快速测试
- 调整脚本中的 `COMMAND_TIMEOUT`

---

## 回退：完成标记（Fallback: Completion Markers）

若 `worktree.yaml` 没有 `verify` 配置，Ralph Loop 使用完成标记。

### 工作方式（How It Works）

1. 读取 `check.jsonl` 的 reason 字段
2. 生成期望标记：`{REASON}_FINISH`
3. 在 agent 输出中检查全部标记
4. 缺少标记 = 阻塞停止

### 示例（Example）

```jsonl
{"file": "...", "reason": "typecheck"}
{"file": "...", "reason": "lint"}
```

期望标记：
- `TYPECHECK_FINISH`
- `LINT_FINISH`

---

## 调试（Debugging）

### 查看状态（Check State）

```bash
cat .trellis/.ralph-state.json
```

### 手动验证（Manual Verify）

```bash
# Run verify commands manually
pnpm lint && pnpm typecheck && pnpm test
```

### 重置状态（Reset State）

```bash
rm .trellis/.ralph-state.json
```

### 查看 Hook 输出（View Hook Output）

在 agent 输出中查找 Ralph Loop 消息：
- "Verification passed" = 全部命令成功
- "Verification failed" = 阻塞中，显示错误
- "Max iterations reached" = 放弃

---

## 定制（Customizing）

### 加入测试验证（Add Test Verification）

```yaml
verify:
  - pnpm lint
  - pnpm typecheck
  - pnpm test
```

### 加入构建验证（Add Build Verification）

```yaml
verify:
  - pnpm lint
  - pnpm typecheck
  - pnpm build
```

### 不同语言（Different Languages）

**Go：**
```yaml
verify:
  - go fmt ./...
  - go vet ./...
  - go test ./...
```

**Python：**
```yaml
verify:
  - ruff check .
  - mypy .
  - pytest
```

**Rust：**
```yaml
verify:
  - cargo fmt --check
  - cargo clippy
  - cargo test
```

---

## 禁用 Ralph Loop（Disabling Ralph Loop）

要在项目中禁用：

1. 从 `worktree.yaml` 移除 `verify`
2. 或从 settings.json 移除 SubagentStop hook

**警告**：没有 Ralph Loop 时，代码质量不会被自动强制。
