<!-- 研究用中文对照读本 -->
<!-- 源文件: .claude/skills/trellis-meta/references/claude-code/worktree-config.md -->
<!-- 术语约定: 首次出现用「中文（English）」；路径/命令/标识符/URL 保持英文原文 -->
<!-- 不自动同步: 英文源更新后需人工对照修订本文件 -->

# worktree.yaml 配置参考（worktree.yaml Configuration Reference）

`.trellis/worktree.yaml` 的完整配置指南。

---

## 概述（Overview）

`worktree.yaml` 同时配置 **Multi-Session**（worktree 隔离）以及部分 **Multi-Agent** 行为（如 Ralph Loop）。

```yaml
# .trellis/worktree.yaml

# Multi-Session only
worktree_dir: ../worktrees    # Default value
copy:
  - .trellis/.developer
  - .env
post_create:
  - npm install

# Both Multi-Session AND Multi-Agent
verify:
  - pnpm lint
  - pnpm typecheck
```

**Note**: Trellis 使用自定义 YAML 解析器（不是 PyYAML）。支持基本键值对与数组；复杂嵌套结构可能不可用。

---

## 配置章节（Configuration Sections）

### 哪项配置影响什么？（Which Config Affects What?）

| Config | Multi-Agent (current dir) | Multi-Session (worktree) |
|--------|---------------------------|--------------------------|
| `worktree_dir` | ❌ 不使用 | ✅ Worktree 位置 |
| `copy` | ❌ 不使用 | ✅ 复制到 worktree 的文件 |
| `post_create` | ❌ 不使用 | ✅ 创建 worktree 后的命令 |
| `verify` | ✅ 被 Ralph Loop 使用 | ✅ 被 Ralph Loop 使用 |

**关键点**：`verify` 配置对两种模式都生效！

---

## 完整配置（Full Configuration）

```yaml
# =============================================================================
# MULTI-SESSION ONLY - Only used in worktree mode
# =============================================================================

# Worktree creation location (relative to project root)
# Default: ../worktrees
worktree_dir: ../worktrees

# Files to copy to each worktree
# These files are not in git, need manual copy
# Default: [] (empty array)
copy:
  - .trellis/.developer      # Developer identity
  - .env                      # Environment variables
  - .env.local                # Local overrides
  # - .npmrc                  # npm config
  # - credentials.json        # Credential files

# Commands to run after worktree creation
# Runs in order, stops on first failure
# Default: [] (empty array)
post_create:
  - npm install               # or pnpm install
  # - pnpm install --frozen-lockfile
  # - cp .env.example .env
  # - npm run db:migrate

# =============================================================================
# BOTH MODES - Used in both Multi-Agent and Multi-Session
# =============================================================================

# Verification commands - Used by Ralph Loop
# Runs when Check Agent stops
# All must pass to allow stop
# Default: [] (empty array)
verify:
  - pnpm lint
  - pnpm typecheck
  # - pnpm test
  # - pnpm build
```

### 默认值（Default Values）

| Config | Default | Notes |
|--------|---------|-------|
| `worktree_dir` | `../worktrees` | 相对项目根 |
| `copy` | `[]` | 空数组，不复制文件 |
| `post_create` | `[]` | 空数组，不运行命令 |
| `verify` | `[]` | 空数组，Ralph Loop 使用完成标记 |

---

## 场景：当前目录 Multi-Agent（Scenario: Multi-Agent in Current Directory）

**Requirement**: 在当前目录跑 dispatch → implement → check，无 worktree

**worktree.yaml config**:
```yaml
# These can be omitted (not used in current directory mode)
# worktree_dir: ...
# copy: ...
# post_create: ...

# This is needed! Ralph Loop uses it
verify:
  - pnpm lint
  - pnpm typecheck
```

**Workflow**:
1. 设置会话作用域活动任务
2. 调用 `Task(subagent_type="implement")`
3. 调用 `Task(subagent_type="check")`
4. Check Agent 完成时，Ralph Loop 运行 `verify` 命令
5. 人类提交

---

## 场景：自定义工作流（Scenario: Custom Workflows）

### 加入测试验证（Add test verification）

```yaml
verify:
  - pnpm lint
  - pnpm typecheck
  - pnpm test          # Add tests
```

### 加入构建验证（Add build verification）

```yaml
verify:
  - pnpm lint
  - pnpm typecheck
  - pnpm build         # Add build check
```

### Go 项目（Go projects）

```yaml
verify:
  - go fmt ./...
  - go vet ./...
  - go test ./...
```

### Python 项目（Python projects）

```yaml
verify:
  - ruff check .
  - mypy .
  - pytest
```

### Rust 项目（Rust projects）

```yaml
verify:
  - cargo fmt --check
  - cargo clippy
  - cargo test
```

---

## 场景：自定义 Worktree 创建（Scenario: Custom Worktree Creation）

### 不同包管理器（Different package managers）

```yaml
post_create:
  # npm
  - npm install

  # or pnpm
  # - pnpm install --frozen-lockfile

  # or yarn
  # - yarn install --frozen-lockfile

  # or bun
  # - bun install
```

### 需要数据库迁移（Database migrations required）

```yaml
post_create:
  - pnpm install
  - pnpm db:migrate
  - pnpm db:seed
```

### 需要代码生成（Code generation required）

```yaml
post_create:
  - pnpm install
  - pnpm codegen
  - pnpm prisma generate
```

### 复制额外文件（Copy additional files）

```yaml
copy:
  - .trellis/.developer
  - .env
  - .env.local
  - .npmrc                    # npm private registry config
  - firebase-credentials.json # Firebase credentials
  - google-cloud-key.json     # GCP credentials
```

---

## 缺少 worktree.yaml 时（When worktree.yaml is Missing）

若 `worktree.yaml` 不存在：

| Feature | Behavior |
|---------|----------|
| Multi-Session | ❌ 无法启动（start.py 需要配置） |
| Multi-Agent | ⚠️ 可用，但 Ralph Loop 使用完成标记 |

**Ralph Loop 回退行为**:
- 没有 `verify` 配置时，使用完成标记
- 从 `check.jsonl` 的 reason 字段生成标记
- 示例：`{"reason": "typecheck"}` → 期望 `TYPECHECK_FINISH`

---

## 最小配置（Minimal Configuration）

### 仅 Multi-Agent（当前目录）

```yaml
# .trellis/worktree.yaml
verify:
  - pnpm lint
  - pnpm typecheck
```

### 仅 Multi-Session（worktree）

```yaml
# .trellis/worktree.yaml
worktree_dir: ../worktrees
copy:
  - .trellis/.developer
post_create:
  - npm install
verify:
  - pnpm lint
  - pnpm typecheck
```

---

## 完整示例（Complete Examples）

### Node.js/TypeScript 项目

```yaml
worktree_dir: ../worktrees

copy:
  - .trellis/.developer
  - .env
  - .env.local

post_create:
  - pnpm install --frozen-lockfile

verify:
  - pnpm lint
  - pnpm typecheck
  - pnpm test
```

### Python 项目

```yaml
worktree_dir: ../worktrees

copy:
  - .trellis/.developer
  - .env
  - venv/              # or recreate venv

post_create:
  - python -m venv venv
  - ./venv/bin/pip install -r requirements.txt

verify:
  - ./venv/bin/ruff check .
  - ./venv/bin/mypy .
  - ./venv/bin/pytest
```

### Go 项目

```yaml
worktree_dir: ../worktrees

copy:
  - .trellis/.developer
  - .env

post_create:
  - go mod download

verify:
  - go fmt ./...
  - go vet ./...
  - golangci-lint run
  - go test ./...
```

### Monorepo 项目

```yaml
worktree_dir: ../worktrees

copy:
  - .trellis/.developer
  - .env
  - .npmrc

post_create:
  - pnpm install --frozen-lockfile
  - pnpm -r build  # Build all packages

verify:
  - pnpm -r lint
  - pnpm -r typecheck
  - pnpm -r test
```

---

## 验证命令说明（Verification Command Notes）

### Ralph Loop 常量（Ralph Loop Constants）

| Constant | Value | Description |
|----------|-------|-------------|
| `MAX_ITERATIONS` | 5 | 最大循环次数 |
| `STATE_TIMEOUT_MINUTES` | 30 | 状态超时（分钟） |
| Command timeout | 120s | 每条验证命令超时 |

### 超时（Timeout）

每条验证命令有 **120 秒**（2 分钟）超时。长时间测试可能需要：
- 拆分测试
- 只跑快速测试
- 修改 `ralph-loop.py` 中的 `COMMAND_TIMEOUT` 常量

### 退出码（Exit Codes）

- 退出码 0 = 通过
- 非零 = 失败，阻塞 Check Agent 停止

### 顺序（Order）

命令按配置顺序运行，第一次失败即停止。

推荐顺序：快 → 慢
```yaml
verify:
  - pnpm lint        # Fast (seconds)
  - pnpm typecheck   # Medium (seconds-minutes)
  - pnpm test        # Slow (minutes)
```

---

## YAML 解析器说明（YAML Parser Notes）

Trellis 使用自定义 YAML 解析器（不是 PyYAML），有这些限制：

### 支持的语法（Supported Syntax）

```yaml
# Simple key-value
worktree_dir: ../worktrees

# Arrays (2-space indent, starts with -)
copy:
  - .trellis/.developer
  - .env

# Quoted values
worktree_dir: "../worktrees with spaces"
```

### 不支持的语法（Unsupported Syntax）

```yaml
# ❌ Inline arrays
copy: [.env, .npmrc]

# ❌ Complex nesting
nested:
  key:
    subkey: value

# ❌ Multi-line strings
description: |
  Multiple
  lines
```

---

## 调试配置（Debugging Configuration）

### 查看当前配置（View current config）

```bash
cat .trellis/worktree.yaml
```

### 测试验证命令（Test verify commands）

```bash
# Manual run
pnpm lint && pnpm typecheck

# Or view Ralph Loop state
cat .trellis/.ralph-state.json
```

### 查看 worktree 状态（View worktree status）

```bash
git worktree list
```

### Ralph Loop 调试（Ralph Loop debugging）

```bash
# View state file
cat .trellis/.ralph-state.json

# Example output
# {
#   "task": ".trellis/tasks/01-31-add-login",
#   "iteration": 2,
#   "started_at": "2026-01-31T10:30:00"
# }

# Ralph Loop auto-stops when exceeding MAX_ITERATIONS (5) or STATE_TIMEOUT_MINUTES (30)
```
