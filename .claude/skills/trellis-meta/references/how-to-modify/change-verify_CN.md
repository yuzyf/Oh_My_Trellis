<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/how-to-modify/change-verify.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# How To: 修改 Verify 命令

增加或修改 Ralph Loop 校验命令。

**Platform**：仅 Claude Code（Ralph Loop）

---

## 要修改的文件（Files to Modify）

| File | Action | Required |
|------|--------|----------|
| `.trellis/worktree.yaml` | Modify | Yes |

---

## Step 1: 编辑 worktree.yaml

打开 `.trellis/worktree.yaml` 并修改 `verify` 段：

```yaml
verify:
  - pnpm lint
  - pnpm typecheck
  - pnpm test          # Add this
```

---

## 常见场景（Common Scenarios）

### 添加测试校验

```yaml
verify:
  - pnpm lint
  - pnpm typecheck
  - pnpm test
```

### 添加构建校验

```yaml
verify:
  - pnpm lint
  - pnpm typecheck
  - pnpm build
```

### 添加特定测试套件

```yaml
verify:
  - pnpm lint
  - pnpm typecheck
  - pnpm test:unit        # Fast unit tests only
```

### 不同语言

**Go:**
```yaml
verify:
  - go fmt ./...
  - go vet ./...
  - golangci-lint run
  - go test ./...
```

**Python:**
```yaml
verify:
  - ruff check .
  - mypy .
  - pytest -x
```

**Rust:**
```yaml
verify:
  - cargo fmt --check
  - cargo clippy
  - cargo test
```

---

## 执行细节（Execution Details）

### 顺序

命令按序运行。第一次失败即停止。

**推荐顺序**：快 → 慢

```yaml
verify:
  - pnpm lint        # ~2 seconds
  - pnpm typecheck   # ~10 seconds
  - pnpm test:unit   # ~30 seconds
  - pnpm build       # ~60 seconds
```

### 超时

每条命令超时 120 秒。

对长时命令：
- 拆成更小块
- Ralph Loop 用更快子集
- 全量套件手动跑

### 退出码

- Exit 0 = Pass
- Non-zero = Fail，agent 继续

---

## 测试（Testing）

### 手动测试

```bash
# Run commands manually
pnpm lint && pnpm typecheck && pnpm test

# Should all pass for Ralph Loop to allow stop
```

### 集成测试

1. 做一次会让 lint 失败的改动
2. 运行 check agent
3. 验证 Ralph Loop 阻塞并显示错误
4. 修复问题
5. 验证 Ralph Loop 允许停止

---

## 排障（Troubleshooting）

### 命令找不到

确保命令可用：

```bash
which pnpm  # or npm, yarn, etc.
```

### 超时问题

在 `ralph-loop.py` 中增加超时：

```python
COMMAND_TIMEOUT = 180  # Default is 120
```

### 临时跳过 Verify

注释掉命令：

```yaml
verify:
  - pnpm lint
  # - pnpm typecheck  # Skip temporarily
```

---

## 检查清单（Checklist）

- [ ] 命令已加入 worktree.yaml
- [ ] 命令已手动测试
- [ ] 顺序为 快 → 慢
- [ ] 无超时问题
