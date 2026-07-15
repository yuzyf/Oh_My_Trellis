> 中文对照读本（研究用，不替换系统加载入口）
> 源文件：`.claude/skills/python-design/SKILL.md`
> 术语：路径/命令/标识符保留英文；概念词首次「中文（English）」
> 维护：研究快照，不承诺与英文源自动同步

---
name: python-design
description: "面向 CLI 脚本与工具的 Python 设计模式——类型优先开发、深模块、复杂度管理与红旗信号。在阅读、编写、评审或重构 Python 文件时使用，尤其是 .trellis/scripts/ 或任意 CLI/脚本场景。规划模块结构、决定新代码放哪、或做 code review 时也应激活。"
---

# 面向 CLI 脚本的 Python 设计（Python Design for CLI Scripts）

用于编写可维护 Python CLI 工具与实用程序的设计模式与原则。
基于 *A Philosophy of Software Design*（Ousterhout），并适配脚本场景。

## 何时激活（When to Activate）

- 编写或修改 Python 文件
- 规划模块拆分
- 评审 Python 改动
- 重构感觉「很乱」的脚本
- 新增子命令或工具函数

## 核心论点（Core Thesis）

**中心挑战是管理复杂度，而不是堆功能。**

复杂度是任何让代码难以理解或修改的东西。它有三种症状：

1. **变更放大（Change Amplification）** — 一处小改要动很多地方
2. **认知负荷（Cognitive Load）** — 要安全修改必须脑中塞太多上下文
3. **未知的未知（Unknown Unknowns）** — 你不知道自己不知道什么（最危险）

复杂度是渐进的。它由成百上千个小决策累积，而不是一次灾难性错误。因此：**在小处较真（sweat the small stuff）**。

---

## 原则 1：深模块（Deep Modules）

模块的价值 = 隐藏的功能 / 暴露的接口。

```
Deep module (good):          Shallow module (bad):
┌──────────┐                 ┌──────────────────────────┐
│ simple   │                 │ complex interface        │
│ interface│                 │ many params, many methods │
├──────────┤                 ├──────────────────────────┤
│          │                 │                          │
│  rich    │                 │  thin implementation     │
│  impl    │                 │                          │
│          │                 └──────────────────────────┘
│          │
└──────────┘
```

**实用检验**：若调用方必须理解模块内部才能正确使用，模块就太浅。

### 例子：任务数据访问

```python
# Shallow — caller must know JSON structure, file paths, error handling
def _read_json_file(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

# Every caller does this independently:
task_path = tasks_dir / name / "task.json"
data = _read_json_file(task_path)
title = data.get("title") or data.get("name", "")
status = data.get("status", "planning")
assignee = data.get("assignee", "")
```

```python
# Deep — caller gets what they need, module hides JSON/path/parsing
@dataclass(frozen=True)
class TaskInfo:
    name: str
    title: str
    status: str
    assignee: str
    priority: str
    directory: Path

def load_task(tasks_dir: Path, name: str) -> TaskInfo | None:
    """Load task by directory name. Returns None if not found."""
    ...

def list_active_tasks(tasks_dir: Path) -> list[TaskInfo]:
    """List all non-archived tasks, sorted by priority."""
    ...
```

深版本吸收复杂度：JSON 解析、字段默认值、目录扫描、归档过滤。调用方只和带类型的数据打交道。

---

## 原则 2：类型优先开发（Type-First Development）

类型在实现前定义契约。这个工作流能更早抓住设计问题：

1. **先定义数据形状** — dataclass 或 TypedDict
2. **再定义函数签名** — 参数与返回类型
3. **实现去满足类型** — 让类型检查器引导完整性
4. **在边界校验** — 运行时检查只放在数据进入系统处

### 内部数据用 Frozen Dataclass

```python
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class AgentRecord:
    agent_id: str
    task_name: str
    worktree_path: Path
    platform: Literal["claude", "codex", "cursor"]
    status: Literal["running", "done", "failed"]
    branch: str
```

Frozen dataclass 不可变——没有意外修改，可安全传递。

### 外部 JSON 形状用 TypedDict

数据来自文件（task.json、config.yaml、registry.json）时，用 TypedDict 文档化期望形状：

```python
from typing import TypedDict, Required, NotRequired

class TaskData(TypedDict):
    title: Required[str]
    status: Required[str]
    assignee: NotRequired[str]
    priority: NotRequired[str]
    parent: NotRequired[str]
    children: NotRequired[list[str]]
```

这能消掉四处散落的 `.get("field", default)`——形状只文档化一次。

### 领域原语用 NewType

当两个字符串含义不同时，让类型系统强制区分：

```python
from typing import NewType

TaskName = NewType("TaskName", str)    # directory name like "03-10-v040"
BranchName = NewType("BranchName", str)  # git branch like "feat/v0.4.0"

def create_branch(task: TaskName) -> BranchName:
    return BranchName(f"task/{task}")
```

### 状态用可判别联合（Discriminated Unions）

实体可处于不同状态、且各状态数据不同时：

```python
@dataclass(frozen=True)
class Pending:
    status: Literal["pending"] = "pending"

@dataclass(frozen=True)
class Running:
    status: Literal["running"] = "running"
    pid: int
    worktree: Path

@dataclass(frozen=True)
class Completed:
    status: Literal["completed"] = "completed"
    branch: str
    commit: str

AgentState = Pending | Running | Completed

def handle(state: AgentState) -> None:
    match state:
        case Running(pid=pid, worktree=wt):
            check_process(pid)
        case Completed(branch=br):
            create_pr(br)
        case Pending():
            pass
```

类型检查器确保每个状态都被处理。不再是 `if data.get("status") == "running"` 却漏分支。

---

## 原则 3：信息隐藏（Information Hiding）

每个模块应封装设计决策。当同一知识出现在多个模块时，信息已经泄漏。

### 脚本里常见的泄漏模式

**JSON schema 知识散落各处：**
```python
# BAD — 9 files all know how to iterate tasks and parse task.json
for d in sorted(tasks_dir.iterdir()):
    if d.name == "archive" or not d.is_dir():
        continue
    task_json = d / "task.json"
    if task_json.exists():
        data = json.loads(task_json.read_text())
        title = data.get("title") or data.get("name", "")
        ...
```

```python
# GOOD — one module owns task iteration
# common/tasks.py
def iter_active_tasks(tasks_dir: Path) -> Iterator[TaskInfo]:
    """Yield all active (non-archived) tasks."""
    for d in sorted(tasks_dir.iterdir()):
        if d.name == "archive" or not d.is_dir():
            continue
        info = _load_task_json(d)
        if info:
            yield info
```

**文件格式细节穿透多层：**
```python
# BAD — caller knows it's JSON, knows the path convention
registry_path = trellis_dir / "registry.json"
data = json.loads(registry_path.read_text())
data["agents"][agent_id] = {...}
registry_path.write_text(json.dumps(data, indent=2))

# GOOD — module hides storage format
registry = AgentRegistry(trellis_dir)
registry.add(agent_id, task=task_name, platform="claude")
```

---

## 原则 4：把复杂度往下拉（Pull Complexity Downward）

当复杂度不可避免时，应由模块在内部吸收，而不是推给调用方。模块作者少、用户多——模块作者处理一次，好过每个调用方各自处理。

```python
# BAD — pushes complexity to every caller
def run_git(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["git"] + args, capture_output=True, text=True)

# Every caller must: check returncode, decode stderr, handle encoding,
# strip whitespace, handle repo not found, etc.

# GOOD — absorbs complexity
def run_git(args: list[str], *, cwd: Path | None = None) -> str:
    """Run git command, return stdout. Raises GitError on failure."""
    ...
```

---

## 原则 5：定义错误使之不存在（Define Errors Out of Existence）

与其到处处理特殊情况，不如设计 API 让特殊情况消失。

| 方法 | 例子 |
|------|------|
| **返回安全默认** | 找不到时返回空列表，而不是抛异常 |
| **合并操作** | `mkdir -p` 风格：存在也不报错 |
| **消除非法状态** | 用类型使非法组合不可表示 |
| **在构造时校验** | 坏对象根本创建不出来 |

```python
# BAD — caller must handle FileNotFoundError everywhere
def read_config(path: Path) -> dict:
    return json.loads(path.read_text())

# GOOD — missing config is a valid empty state
def read_config(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())
```

---

## 原则 6：战略 vs 战术编程；Rule of Three

**战术编程**只想「让它现在能跑」。**战略编程**投资于能降低未来修改成本的设计。

**Rule of Three**：在出现第三次之前，容忍一点重复；第三次出现就立刻抽取。过早抽象往往更糟：
- 它通过共享抽象耦合本不相关的实例
- 让每个实例更难独立理解
- 会迫使未来案例硬塞进不适配的抽象

**但是**：一旦到了三次，立刻抽取。别拖到九次。

---

## 原则 7：单一职责与模块边界

每个模块应有 **一个变更理由**。当模块超过约 300 行，检查它是否承担了多种职责。

### 拆分信号

出现这些情况就拆：
- 文件被注释标题分成多个「区块」
- 你只需要从一个大模块导入一个函数
- 模块不同部分的测试没有共享 setup
- 改一种职责不需要理解另一种

### 如何拆

按 **信息隐藏**（封装了什么知识）拆，不要按执行顺序（什么时候跑）拆。

```python
# BAD — split by execution order (temporal decomposition)
# step1_parse_args.py, step2_validate.py, step3_execute.py
# All three must know the command structure

# GOOD — split by responsibility
# task_store.py    — owns task.json read/write, schema, iteration
# task_cli.py      — owns argparse, subcommand routing
# task_display.py  — owns formatting, colors, table output
```

---

## 原则 8：一致的共享基础设施

多个脚本需要同一能力时，在 `common/` 提供一次。

| 能力 | 应放在 | 不要放在 |
|-----------|---------------|--------|
| JSON 文件读写 | `common/io.py` | 每个脚本的 `_read_json_file` |
| 终端颜色 + 日志 | `common/log.py` | 每个脚本的 `Colors` 类 |
| Git 命令执行 | `common/git.py` | 带 `_` 前缀的私有 `_run_git_command` |
| 任务数据访问 | `common/tasks.py` | 临时解析 task.json |
| 路径常量 | `common/paths.py`（已有） | 硬编码字符串 |

**命名**：若函数被其他模块使用，它就是公共 API——不要加 `_` 前缀。

---

## 原则 9：结构化 CLI 输出解析

解析 shell 命令输出（git、grep 等）时，尊重语义空白：

```python
# BAD — .strip() destroys semantic whitespace
# git submodule status prefix: ' ' = initialized, '-' = uninitialized, '+' = changed
line = output_line.strip()  # Loses the prefix character!

# GOOD — strip only trailing newlines
line = output_line.rstrip("\n\r")
prefix = line[0] if line else " "
```

解析结构化命令输出时，务必文档化每个字段位置的含义。

---

## 红旗速查（Red Flags Quick Reference）

用于 code review 与自审：

| 信号 | 含义 |
|--------|--------------|
| **Shallow Module** | 接口几乎和实现一样复杂 |
| **Information Leakage** | 同一 JSON schema / 文件格式知识出现在多个模块 |
| **Duplicated Utility** | 同一 helper 复制到多个文件 |
| **God Module** | 文件 > 500 行且职责不相关 |
| **Pass-Through Function** | 函数只是把参数转给签名类似的另一个函数 |
| **Magic `.get()` Chains** | `data.get("x") or data.get("y", "")` — 缺少类型定义 |
| **sys.path Hacking** | `sys.path.insert(0, ...)` — 应修包结构 |
| **Private-Named Public API** | `_function` 被 3+ 外部模块导入 |
| **Raw Dict Threading** | `dict` 穿过 4+ 次函数调用 — 用 dataclass |
| **Repeated Iteration** | 同一目录扫描 / 文件解析模式出现在 3+ 处 |
| **Broad Exception Catch** | `except Exception:` 且不 re-raise — 藏 bug |
| **Temporal Decomposition** | 按「何时运行」拆模块，而不是「知道什么」 |

---

## 设计清单（写代码前）

1. **类型优先**：写逻辑前先定义数据形状
2. **模块深度检查**：接口会比实现更简单吗？
3. **重复扫描**：新建工具前 `grep -r "pattern" .`
4. **职责检查**：它是否属于已有模块？
5. **错误设计**：能否把错误定义到不存在？
6. **命名精确**：名字不看实现也能传达含义吗？

## 设计清单（Code Review 时）

1. **红旗扫描**：用上表对照 diff
2. **类型安全**：新数据形状是否用类型文档化？
3. **信息隐藏**：改动是否泄漏实现细节？
4. **一致性**：是否遵循模块既有模式？
5. **深度**：调用方的常见路径是否简单？

---

## 战略投资（Strategic Investment）

大约把每次改动的 **10-20%** 花在改善周边设计上。

能跑只是必要非充分。软件开发的增量应是 **抽象**，而不只是功能。每次改动都应让代码库比你找到时略好一点。

这不是完美主义——这是复利。小的设计改进会累积成一个长期好得多的系统。
