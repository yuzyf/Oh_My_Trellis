#!/usr/bin/env python3
"""
任务增删改查（CRUD）操作。

提供:
    ensure_tasks_dir    - 确保 tasks 目录存在
    cmd_create          - 创建新任务
    cmd_archive         - 归档已完成任务
    cmd_set_branch      - 设置任务的 git 分支
    cmd_set_base_branch - 设置 PR 目标分支
    cmd_set_scope       - 设置 PR 标题用的 scope
    cmd_add_subtask     - 将子任务链接到父任务
    cmd_remove_subtask  - 取消子任务与父任务的链接
"""

# 启用延迟注解求值等 future 特性
from __future__ import annotations

# 导入依赖
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from .config import (
    get_codex_dispatch_mode,
    get_packages,
    get_session_auto_commit,
    is_monorepo,
    resolve_package,
    validate_package,
)
from .git import run_git
from .io import read_json, write_json
from .log import Colors, colored
from .paths import (
    DIR_ARCHIVE,
    DIR_TASKS,
    DIR_WORKFLOW,
    FILE_TASK_JSON,
    generate_task_date_prefix,
    get_developer,
    get_repo_root,
    get_tasks_dir,
)
from .safe_commit import (
    print_gitignore_warning,
    safe_archive_paths_to_add,
    safe_git_add,
)
from .task_utils import (
    archive_task_complete,
    find_task_by_name,
    is_within_tasks_dir,
    resolve_task_dir,
    run_task_hooks,
)


# =============================================================================
# Helper Functions
# =============================================================================

# 辅助函数
def _slugify(title: str) -> str:
    """将标题转为 slug（仅支持 ASCII）。"""
    # result ← 调用 title.lower
    result = title.lower()
    # result ← 调用 re.sub
    result = re.sub(r"[^a-z0-9]", "-", result)
    # result ← 调用 re.sub
    result = re.sub(r"-+", "-", result)
    # result ← 调用 result.strip
    result = result.strip("-")
    return result  # 返回 result


def ensure_tasks_dir(repo_root: Path) -> Path:
    """确保 tasks 目录存在。"""
    # tasks_dir ← 调用 get_tasks_dir
    # 创建 task directory with MM-DD-slug format
    tasks_dir = get_tasks_dir(repo_root)
    # 计算后赋给 archive_dir
    archive_dir = tasks_dir / "archive"

    # 若条件不成立：not tasks_dir.exists()
    if not tasks_dir.exists():
        # 创建目录
        tasks_dir.mkdir(parents=True)
        # 输出信息
        print(colored(f"Created tasks directory: {tasks_dir}", Colors.GREEN), file=sys.stderr)

    # 若条件不成立：not archive_dir.exists()
    if not archive_dir.exists():
        # 创建目录
        archive_dir.mkdir(parents=True)

    return tasks_dir  # 返回 tasks_dir


def _find_archived_task_by_dir_name(tasks_dir: Path, dir_name: str) -> Path | None:
    """
查找：Find an archived task directory with the exact active-task dir name.
"""
    # 计算后赋给 archive_dir
    archive_dir = tasks_dir / DIR_ARCHIVE
    # 若条件不成立：not archive_dir.is_dir()
    if not archive_dir.is_dir():
        return None  # 返回 None

    # 遍历：month_dir in sorted(archive_dir.iterdir())
    for month_dir in sorted(archive_dir.iterdir()):
        # 若条件不成立：not month_dir.is_dir()
        if not month_dir.is_dir():
            continue  # 跳过本轮循环
        # 计算后赋给 candidate
        candidate = month_dir / dir_name
        # 条件分支：candidate.is_dir()
        if candidate.is_dir():
            return candidate  # 返回 candidate

    return None


def _repo_relative_path(path: Path, repo_root: Path) -> str:
    """格式化：Format a path relative to the repo root when possible."""
    # try：执行可能失败的逻辑
    try:
        # 返回 path.relative_to(repo_root)… 的调用结果
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        # 返回 str 的调用结果
        return str(path)


# =============================================================================
# Sub-agent platform detection + JSONL seeding
# =============================================================================

# Config directories of platforms that consume implement.jsonl / check.jsonl.
# Keep in sync with src/types/ai-tools.ts AI_TOOLS entries — these are the
# platforms listed in workflow.md's "agent-capable" Skill Routing block.
# Codex is checked separately because default inline mode does not consume
# JSONL. Kilo / Antigravity / Devin are NOT in this list either: they load
# specs through skills instead of JSONL.
# 子 agent 平台检测与 JSONL 种子文件
# 会消费 implement.jsonl / check.jsonl 的平台配置目录。
# 需与 src/types/ai-tools.ts 的 AI_TOOLS 条目保持同步——这些是
# workflow.md「agent-capable」Skill 路由块中列出的平台。
# Codex 单独检查，因为默认 inline 模式不消费
# JSONL。Kilo / Antigravity / Devin 也不在此列表：它们通过
# skills 加载规格，而不是 JSONL。
# 赋值（含类型标注）：_SUBAGENT_CONFIG_DIRS
_SUBAGENT_CONFIG_DIRS: tuple[str, ...] = (
    ".claude",
    ".cursor",
    ".kiro",
    ".gemini",
    ".opencode",
    ".qoder",
    ".codebuddy",
    ".factory",   # Factory Droid
    ".github/copilot",
    ".pi",        # Pi Agent
    ".trae",      # Trae IDE
    ".omp",       # Oh My Pi
    ".zcode",     # ZCode
)
# 初始化 _CODEX_CONFIG_DIR
_CODEX_CONFIG_DIR = ".codex"

# 初始化 _SEED_EXAMPLE
_SEED_EXAMPLE = (
    "Fill with {\"file\": \"<path>\", \"reason\": \"<why>\"}. "
    "Put spec/research files only — no code paths. "
    "Run `python3 .trellis/scripts/get_context.py --mode packages` to list available specs. "
    "Delete this line once real entries are added."
)


def _has_subagent_platform(repo_root: Path) -> bool:
    """
返回：Return True if any sub-agent-capable platform is configured.

Detected by probing well-known config directories at the repo root. Codex
only counts when ``codex.dispatch_mode`` explicitly opts into
``sub-agent``; inline mode loads context through skills, not JSONL.
"""
    # 遍历：config_dir in _SUBAGENT_CONFIG_DIRS
    for config_dir in _SUBAGENT_CONFIG_DIRS:
        # 条件分支：(repo_root / config_dir).is_dir()
        if (repo_root / config_dir).is_dir():
            return True  # 返回 True
    # 条件分支：(repo_root / _CODEX_CONFIG_DIR).is_dir()
    if (repo_root / _CODEX_CONFIG_DIR).is_dir():
        # 返回 get_codex_dispatch_mode(repo_root) …
        return get_codex_dispatch_mode(repo_root) == "sub-agent"
    return False  # 返回 False


def _write_seed_jsonl(path: Path) -> None:
    """
写入/保存：Write a one-line seed JSONL file with a self-describing ``_example``.

The seed row has no ``file`` field, so downstream consumers (hooks +
preludes) that iterate entries via ``item.get("file")`` naturally skip
it. The row exists purely as an in-file prompt for the AI curator.
"""
    # 构造字典赋给 seed
    seed = {"_example": _SEED_EXAMPLE}
    # 写入文件
    path.write_text(json.dumps(seed, ensure_ascii=False) + "\n", encoding="utf-8")


def _default_prd_content(title: str, description: str | None = None) -> str:
    """返回：Return the default PRD skeleton created with every task."""
    # 逻辑运算结果赋给 goal
    goal = (description or "").strip() or "TBD."
    # 逻辑运算结果赋给 heading
    heading = title.strip() or "Untitled task"
    # 返回格式化文本
    return f"""# {heading}

## Goal

{goal}

## Requirements

- TBD

## Acceptance Criteria

- [ ] TBD

## Notes

- Keep `prd.md` focused on requirements, constraints, and acceptance criteria.
- Lightweight tasks can remain PRD-only.
- For complex tasks, add `design.md` for technical design and `implement.md` for execution planning before `task.py start`.
"""


# =============================================================================
# Command: create
# =============================================================================

# 命令：create
def cmd_create(args: argparse.Namespace) -> int:
    """创建：Create a new task."""
    # repo_root ← 调用 get_repo_root
    repo_root = get_repo_root()

    # 若条件不成立：not args.title
    if not args.title:
        # 输出信息
        print(colored("Error: title is required", Colors.RED), file=sys.stderr)
        # 返回常量 1
        return 1

    # Validate --package (CLI source: fail-fast)
    # 校验 --package (CLI source: fail-fast)
    # package ← 调用 getattr
    package: str | None = getattr(args, "package", None)
    # 若条件不成立：not is_monorepo(repo_root)
    if not is_monorepo(repo_root):
        # Single-repo: ignore --package, no package prefix
        # 单仓：忽略 --package，无 package 前缀
        # 条件分支：package
        if package:
            # 输出信息
            print(colored(f"Warning: --package ignored in single-repo project", Colors.YELLOW), file=sys.stderr)
        # 初始化 package
        package = None
    # 条件分支：package
    elif package:
        # 若条件不成立：not validate_package(package, repo_root)
        if not validate_package(package, repo_root):
            # packages ← 调用 get_packages
            packages = get_packages(repo_root)
            # 按条件取值赋给 available
            available = ", ".join(sorted(packages.keys())) if packages else "(none)"
            # 输出信息
            print(colored(f"Error: unknown package '{package}'. Available: {available}", Colors.RED), file=sys.stderr)
            return 1
    else:
        # Inferred: default_package → None (no task.json yet for create)
        # 推断：default_package → None（create 时还没有 task.json）
        # package ← 调用 resolve_package
        package = resolve_package(repo_root=repo_root)

    # Default assignee to current developer
    # 默认指派人为当前 developer
    # 读取属性赋给 assignee
    assignee = args.assignee
    # 若条件不成立：not assignee
    if not assignee:
        # assignee ← 调用 get_developer
        assignee = get_developer(repo_root)
        if not assignee:
            # 输出信息
            print(colored("Error: No developer set. Run init_developer.py first or use --assignee", Colors.RED), file=sys.stderr)
            return 1

    # 调用 ensure_tasks_dir
    ensure_tasks_dir(repo_root)

    # Get current developer as creator
    # 获取 current developer as creator
    # 逻辑运算结果赋给 creator
    creator = get_developer(repo_root) or assignee

    # Generate slug if not provided
    # 未提供时生成 slug
    # 逻辑运算结果赋给 slug
    slug = args.slug or _slugify(args.title)
    # 若条件不成立：not slug
    if not slug:
        # 输出信息
        print(colored("Error: could not generate slug from title", Colors.RED), file=sys.stderr)
        return 1

    # Create task directory with MM-DD-slug format
    tasks_dir = get_tasks_dir(repo_root)
    # date_prefix ← 调用 generate_task_date_prefix
    date_prefix = generate_task_date_prefix()

    # Guard against date-prefixed --slug (e.g. a full task dir name pasted in),
    # which would otherwise produce MM-DD-MM-DD-slug (issue #377). Only an
    # explicit --slug is guarded; title-derived slugs are left untouched.
    # 防止带日期前缀的 --slug（例如粘贴了完整任务目录名），
    # 否则会生成 MM-DD-MM-DD-slug（issue #377）。仅对
    # 显式 --slug 做防护；由标题派生的 slug 不动。
    # 条件分支：args.slug
    if args.slug:
        # m ← 调用 re.match
        m = re.match(r"^(\d{2})-(\d{2})-(.+)$", slug)
        # 条件分支：m and 1 <= int(m.group(1)) <= 12 and 1 <=…
        if m and 1 <= int(m.group(1)) <= 12 and 1 <= int(m.group(2)) <= 31:
            # 拼出字符串赋给 slug_prefix
            slug_prefix = f"{m.group(1)}-{m.group(2)}"
            # 条件分支：slug_prefix == date_prefix
            if slug_prefix == date_prefix:
                # slug ← 调用 m.group
                slug = m.group(3)
                # 输出信息
                print(
                    colored(
                        f'warning: --slug should not include the MM-DD prefix; normalized to "{slug}"',
                        Colors.YELLOW,
                    ),
                    file=sys.stderr,
                )
            else:
                print(
                    colored(
                        f"Error: --slug starts with a date prefix ({slug_prefix}-), but task.py create always uses today's date ({date_prefix}).",
                        Colors.RED,
                    ),
                    file=sys.stderr,
                )
                # 输出信息
                print(f"Pass only the slug body, e.g. --slug {m.group(3)}", file=sys.stderr)
                return 1

    # 拼出字符串赋给 dir_name
    dir_name = f"{date_prefix}-{slug}"
    # 计算后赋给 task_dir
    task_dir = tasks_dir / dir_name
    # 计算后赋给 task_json_path
    task_json_path = task_dir / FILE_TASK_JSON

    # archived_task_dir ← 调用 _find_archived_task_by_dir_na…
    archived_task_dir = _find_archived_task_by_dir_name(tasks_dir, dir_name)
    # 条件分支：archived_task_dir
    if archived_task_dir:
        # 输出信息
        print(colored(f"Error: Task already archived: {dir_name}", Colors.RED), file=sys.stderr)
        # 输出信息
        print(f"Archived at: {_repo_relative_path(archived_task_dir, repo_root)}", file=sys.stderr)
        # 输出信息
        print("Use a new slug if you intend to create a new task.", file=sys.stderr)
        return 1

    # 条件分支：task_dir.exists()
    if task_dir.exists():
        # 输出信息
        print(colored(f"Warning: Task directory already exists: {dir_name}", Colors.YELLOW), file=sys.stderr)
    else:
        # 创建目录
        task_dir.mkdir(parents=True)

    # today ← 调用 datetime.now().strftime
    # 更新 status before archiving
    today = datetime.now().strftime("%Y-%m-%d")

    # Record current branch as base_branch (PR target)
    # 把当前分支记为 base_branch（PR 目标）
    # _, branch_out, _ ← 调用 run_git
    _, branch_out, _ = run_git(["branch", "--show-current"], cwd=repo_root)
    # 逻辑运算结果赋给 current_branch
    current_branch = branch_out.strip() or "main"

    # description ← 调用 (args.description or "").strip
    description = (args.description or "").strip()
    # 若条件不成立：not description.strip()
    if not description.strip():
        print(
            colored(
                "warning: task description is empty; pass --description to improve search and later audits.",
                Colors.YELLOW,
            ),
            file=sys.stderr,
        )

    # 构造字典赋给 task_data
    task_data = {
        "id": slug,
        "name": slug,
        "title": args.title,
        "description": description,
        "status": "planning",
        "dev_type": None,
        "scope": None,
        "package": package,
        "priority": args.priority,
        "creator": creator,
        "assignee": assignee,
        "createdAt": today,
        "completedAt": None,
        "branch": None,
        "base_branch": current_branch,
        "worktree_path": None,
        "commit": None,
        "pr_url": None,
        "subtasks": [],
        "children": [],
        "parent": None,
        "relatedFiles": [],
        "notes": "",
        "meta": {},
    }

    # 写入文件
    write_json(task_json_path, task_data)

    # 计算后赋给 prd_path
    prd_path = task_dir / "prd.md"
    # 若条件不成立：not prd_path.exists()
    if not prd_path.exists():
        # 写入文件
        prd_path.write_text(
            _default_prd_content(args.title, description),
            encoding="utf-8",
        )

    # Seed implement.jsonl / check.jsonl for sub-agent-capable platforms.
    # Agent curates real entries during planning when the task needs them.
    # Agent-less platforms (Kilo / Antigravity / Devin) skip this — they
    # load specs via the trellis-before-dev skill instead of JSONL.
    # 为支持子 agent 的平台播种 implement.jsonl / check.jsonl。
    # 规划阶段若任务需要，由 agent 再写入真实条目。
    # 无 agent 平台（Kilo / Antigravity / Devin）跳过——它们
    # 通过 trellis-before-dev skill 加载规格，而不是 JSONL。
    # 初始化 seeded_jsonl
    seeded_jsonl = False
    # 条件分支：_has_subagent_platform(repo_root)
    if _has_subagent_platform(repo_root):
        # 遍历：jsonl_name in ("implement.jsonl", "check.jsonl")
        for jsonl_name in ("implement.jsonl", "check.jsonl"):
            # 计算后赋给 jsonl_path
            jsonl_path = task_dir / jsonl_name
            # 若条件不成立：not jsonl_path.exists()
            if not jsonl_path.exists():
                # 调用 _write_seed_jsonl
                _write_seed_jsonl(jsonl_path)
        # 初始化 seeded_jsonl
        seeded_jsonl = True

    # Handle --parent: establish bidirectional link
    # 处理 --parent: establish bidirectional link
    # 条件分支：args.parent
    if args.parent:
        # parent_dir ← 调用 resolve_task_dir
        parent_dir = resolve_task_dir(args.parent, repo_root)
        # 计算后赋给 parent_json_path
        parent_json_path = parent_dir / FILE_TASK_JSON
        # 若条件不成立：not parent_json_path.is_file()
        if not parent_json_path.is_file():
            # 输出信息
            print(colored(f"Warning: Parent task.json not found: {args.parent}", Colors.YELLOW), file=sys.stderr)
        else:
            # parent_data ← 调用 read_json
            parent_data = read_json(parent_json_path)
            # 条件分支：parent_data
            if parent_data:
                # Add child to parent's children list
                # 把子任务加入父任务的 children 列表
                # parent_children ← 调用 parent_data.get
                # 移除 child from parent's children list
                parent_children = parent_data.get("children", [])
                # 条件分支：dir_name not in parent_children
                if dir_name not in parent_children:
                    # 追加到列表
                    parent_children.append(dir_name)
                    parent_data["children"] = parent_children  # 下标项 ← parent_children
                    # 写入文件
                    # 两者都写入
                    write_json(parent_json_path, parent_data)

                # Set parent in child's task.json
                # 在子任务 task.json 中写入 parent
                # 读取属性赋给 task_data["parent"]
                task_data["parent"] = parent_dir.name
                write_json(task_json_path, task_data)

                # 输出信息
                print(colored(f"Linked as child of: {parent_dir.name}", Colors.GREEN), file=sys.stderr)

    # Auto-activate the new task so the per-turn breadcrumb fires planning
    # state. Best-effort: gracefully degrade if no session identity (CLI run
    # outside an AI session) — the task is still created, the user can run
    # task.py start later. Pointer is session-scoped so this never affects
    # other AI sessions.
    # 自动激活新任务，使每轮 breadcrumb 进入 planning
    # 状态。尽力而为：若无会话身份（CLI 在
    # AI 会话外运行）则优雅降级——任务仍会创建，用户可稍后执行
    # task.py start。指针是会话作用域，不会影响
    # 其它 AI 会话。
    # 条件分支：getattr(args, "no_start", False)
    if getattr(args, "no_start", False):
        print(
            colored(
                "Skipped session activation (--no-start); run task.py start when ready.",
                Colors.YELLOW,
            ),
            file=sys.stderr,
        )
    else:
        try:
            # 局部导入 active_task
            from .active_task import resolve_context_key, set_active_task
            # 条件分支：resolve_context_key()
            if resolve_context_key():
                try:
                    # rel_dir ← 调用 task_dir.relative_to(repo_roo…
                    rel_dir = task_dir.relative_to(repo_root).as_posix()
                except ValueError:
                    # rel_dir ← 调用 str
                    rel_dir = str(task_dir)
                # active ← 调用 set_active_task
                active = set_active_task(rel_dir, repo_root)
                # 条件分支：active
                if active:
                    print(
                        colored(f"Activated task for this session: {active.task_path}", Colors.GREEN),
                        file=sys.stderr,
                    )
                    # 输出信息
                    print(f"Source: {active.source}", file=sys.stderr)
        except Exception:
            # 占位（无操作）
            pass

    # 输出信息
    print(colored(f"Created task: {dir_name}", Colors.GREEN), file=sys.stderr)
    # 输出信息
    print("", file=sys.stderr)
    # 输出信息
    print(colored("Next steps:", Colors.BLUE), file=sys.stderr)
    # 输出信息
    print("  - Fill prd.md with requirements and acceptance criteria", file=sys.stderr)
    # 输出信息
    print("  - Lightweight task: PRD-only is valid", file=sys.stderr)
    # 输出信息
    print("  - Complex task: add design.md and implement.md before task.py start", file=sys.stderr)
    # 条件分支：seeded_jsonl
    if seeded_jsonl:
        print(
            "  - Curate implement.jsonl / check.jsonl as spec/research manifests when sub-agents need context",
            file=sys.stderr,
        )
    # 输出信息
    print("  - Use /trellis:continue or phase context to decide the next step", file=sys.stderr)
    print("", file=sys.stderr)

    # Output relative path for script chaining
    # 输出相对路径供脚本串联
    # 输出信息
    print(f"{DIR_WORKFLOW}/{DIR_TASKS}/{dir_name}")

    # 调用 run_task_hooks
    run_task_hooks("after_create", task_json_path, repo_root)
    return 0  # 返回 0


# =============================================================================
# Command: archive
# =============================================================================

# 命令：archive
def cmd_archive(args: argparse.Namespace) -> int:
    """归档已完成的任务。"""
    repo_root = get_repo_root()
    # 读取属性赋给 task_name
    task_name = args.name

    # 若条件不成立：not task_name
    if not task_name:
        # 输出信息
        print(colored("Error: Task name is required", Colors.RED), file=sys.stderr)
        return 1

    tasks_dir = get_tasks_dir(repo_root)

    # Resolve task directory (supports task name, relative path, or absolute path)
    # 解析任务目录（支持任务名、相对路径或绝对路径）
    # task_dir ← 调用 resolve_task_dir
    task_dir = resolve_task_dir(task_name, repo_root)

    # 若条件不成立：not task_dir or not task_dir.is_dir()
    if not task_dir or not task_dir.is_dir():
        # 输出信息
        print(colored(f"Error: Task not found: {task_name}", Colors.RED), file=sys.stderr)
        # 输出信息
        print("Active tasks:", file=sys.stderr)
        # Import lazily to avoid circular dependency
        # 惰性导入以避免循环依赖
        # 局部导入 tasks
        from .tasks import iter_active_tasks
        # 遍历：t in iter_active_tasks(tasks_dir)
        for t in iter_active_tasks(tasks_dir):
            # 输出信息
            print(f"  - {t.dir_name}/", file=sys.stderr)
        return 1

    # Refuse to archive anything that isn't a real task directly under
    # .trellis/tasks/. A mistyped name (e.g. "src") resolves to repo_root/src,
    # which is a dir but not a task — without this guard archive would move the
    # user's source directory out of the repo.
    # 拒绝归档任何不是 .trellis/tasks/ 下真实任务的路径
    # 。误输入名称（如 "src"）会解析到 repo_root/src，
    # 它是目录但不是任务——若无此防护，archive 会把用户的
    # 源码目录移出仓库。
    if not is_within_tasks_dir(task_dir, repo_root):
        # 输出信息
        print(colored(
            f"Error: refusing to archive '{task_name}': "
            f"{task_dir} is not a task under {tasks_dir}",
            Colors.RED), file=sys.stderr)
        return 1

    # 读取属性赋给 dir_name
    dir_name = task_dir.name
    task_json_path = task_dir / FILE_TASK_JSON

    # Update status before archiving
    today = datetime.now().strftime("%Y-%m-%d")
    # Names of child task dirs whose task.json gets modified below; passed
    # into safe_archive_paths_to_add so they're staged in this commit.
    # 下方会改写 task.json 的子任务目录名；传给
    # 传入 safe_archive_paths_to_add，以便纳入本次提交暂存。
    # 赋值（含类型标注）：modified_children
    modified_children: list[str] = []
    # 条件分支：task_json_path.is_file()
    if task_json_path.is_file():
        # data ← 调用 read_json
        data = read_json(task_json_path)
        # 条件分支：data
        if data:
            # 初始化 data["status"]
            data["status"] = "completed"
            data["completedAt"] = today  # 下标项 ← today
            # 写入文件
            write_json(task_json_path, data)

            # Handle subtask relationships on archive.
            # Keep this task in its parent's children list so progress
            # counters (children_progress) stay consistent — children
            # missing from the active set are treated as completed.
            # 处理 subtask relationships on archive.
            # 把本任务保留在父任务 children 列表中，使进度
            # 计数（children_progress）保持一致——活动集合中缺失的
            # 子任务视为已完成。
            # task_children ← 调用 data.get
            task_children = data.get("children", [])

            # If this is a parent, clear parent field in all children
            # 若自身是父任务，则清除所有子任务的 parent 字段
            # 条件分支：task_children
            if task_children:
                # 遍历：child_name in task_children
                for child_name in task_children:
                    # child_dir_path ← 调用 find_task_by_name
                    child_dir_path = find_task_by_name(child_name, tasks_dir)
                    # 条件分支：child_dir_path
                    if child_dir_path:
                        # 计算后赋给 child_json
                        child_json = child_dir_path / FILE_TASK_JSON
                        # 条件分支：child_json.is_file()
                        if child_json.is_file():
                            # child_data ← 调用 read_json
                            child_data = read_json(child_json)
                            # 条件分支：child_data
                            if child_data:
                                # 初始化 child_data["parent"]
                                # 清除子任务 task.json 中的 parent
                                child_data["parent"] = None
                                # 写入文件
                                write_json(child_json, child_data)
                                # 追加到列表
                                modified_children.append(child_dir_path.name)

    # Clear any session that still points at this task before the path moves.
    # 在路径移动前，清除仍指向本任务的会话指针。
    # 局部导入 active_task
    from .active_task import clear_task_from_sessions
    # 调用 clear_task_from_sessions
    clear_task_from_sessions(str(task_dir), repo_root)

    # Archive
    # 标识：Archive
    # result ← 调用 archive_task_complete
    result = archive_task_complete(task_dir, repo_root)
    # 条件分支："archived_to" in result
    if "archived_to" in result:
        # archive_dest ← 调用 Path
        archive_dest = Path(result["archived_to"])
        # 读取属性赋给 year_month
        year_month = archive_dest.parent.name
        # 输出信息
        print(colored(f"Archived: {dir_name} -> archive/{year_month}/", Colors.GREEN), file=sys.stderr)

        # Auto-commit unless --no-commit
        # 除非指定 --no-commit，否则自动提交
        if not getattr(args, "no_commit", False):
            # 若条件不成立：not _auto_commit_archive(dir_name, repo_root, modi
            if not _auto_commit_archive(dir_name, repo_root, modified_children):
                print(
                    colored(
                        "Archive moved on disk, but git auto-commit did not complete. "
                        "Resolve `git status` before continuing.",
                        Colors.RED,
                    ),
                    file=sys.stderr,
                )
                return 1

        # Return the archive path
        # 返回 the archive path
        # 输出信息
        print(f"{DIR_WORKFLOW}/{DIR_TASKS}/{DIR_ARCHIVE}/{year_month}/{dir_name}")

        # Run hooks with the archived path
        # 使用归档后路径运行钩子
        # 计算后赋给 archived_json
        archived_json = archive_dest / FILE_TASK_JSON
        # 调用 run_task_hooks
        run_task_hooks("after_archive", archived_json, repo_root)
        return 0

    return 1


def _auto_commit_archive(
    task_name: str,
    repo_root: Path,
    modified_children: list[str] | None = None,
) -> bool:
    """归档后暂存 Trellis 管辖的任务路径并提交。"""
    # 若条件不成立：not get_session_auto_commit(repo_root)
    if not get_session_auto_commit(repo_root):
        print(
            "[OK] session_auto_commit: false — skipping git stage/commit.",
            file=sys.stderr,
        )
        return True

    # 拼出字符串赋给 source_rel
    source_rel = f"{DIR_WORKFLOW}/{DIR_TASKS}/{task_name}"
    # rc, tracked_out, _ ← 调用 run_git
    rc, tracked_out, _ = run_git(
        ["ls-files", "--", source_rel],
        cwd=repo_root,
    )
    # 逻辑运算结果赋给 source_was_tracked
    source_was_tracked = rc == 0 and bool(tracked_out.strip())

    # paths ← 调用 safe_archive_paths_to_add
    paths = safe_archive_paths_to_add(
        repo_root, task_name=task_name, modified_children=modified_children
    )
    # 若条件不成立：not paths
    if not paths:
        # 输出信息
        print("[OK] No task changes to commit.", file=sys.stderr)
        return True

    # success, _, err ← 调用 safe_git_add
    success, _, err = safe_git_add(paths, repo_root)
    # 若条件不成立：not success
    if not success:
        # 条件分支：err and "ignored by" in err.lower()
        if err and "ignored by" in err.lower():
            # 调用 print_gitignore_warning
            print_gitignore_warning(paths)
        else:
            print(
                f"[WARN] git add failed: {err.strip() if err else 'unknown error'}",
                file=sys.stderr,
            )
        # 返回 not source_was_tracked
        return not source_was_tracked

    # Belt-and-suspenders for the phantom-delete bug: `safe_git_add` uses
    # `git add` (no -A) which only stages additions/modifications. The
    # source task directory was moved away by `shutil.move`, so its files
    # need an explicit `git rm --cached` to stage the deletions in this
    # same commit — otherwise they sit as uncommitted "phantom deletes"
    # against HEAD until something later picks them up.
    #
    # `--ignore-unmatch` makes this a no-op when the task was never tracked
    # (e.g. archiving a task that lived only in working tree).
    # 针对幽灵删除问题的双保险：`safe_git_add` 使用
    # `git add`（无 -A），只暂存新增/修改。
    # 源任务目录已被 `shutil.move` 移走，因此其文件
    # 需要显式 `git rm --cached` 才能在本
    # 次提交中暂存删除——否则会变成未提交的“幽灵删除”
    # 相对 HEAD 挂着，直到后续某次操作处理。
    # 任务从未被跟踪时，`--ignore-unmatch` 使该操作为空操作
    # （例如归档仅存在于工作区的任务）。
    # 调用 run_git
    run_git(
        ["rm", "-r", "--cached", "--ignore-unmatch", "--", source_rel],
        cwd=repo_root,
    )

    # rc, _, _ ← 调用 run_git
    rc, _, _ = run_git(
        ["diff", "--cached", "--quiet", "--", *paths, source_rel],
        cwd=repo_root,
    )
    # 条件分支：rc == 0
    if rc == 0:
        print("[OK] No task changes to commit.", file=sys.stderr)
        return True

    # 拼出字符串赋给 commit_msg
    commit_msg = f"chore(task): archive {task_name}"
    # rc, _, err ← 调用 run_git
    rc, _, err = run_git(["commit", "-m", commit_msg], cwd=repo_root)
    if rc == 0:
        # 输出信息
        print(f"[OK] Auto-committed: {commit_msg}", file=sys.stderr)
        return True
    else:
        # 输出信息
        print(f"[WARN] Auto-commit failed: {err.strip()}", file=sys.stderr)
        return not source_was_tracked


# =============================================================================
# Command: add-subtask
# =============================================================================

# 命令：add-subtask
def cmd_add_subtask(args: argparse.Namespace) -> int:
    """把子任务关联到父任务。"""
    repo_root = get_repo_root()

    # parent_dir ← 调用 resolve_task_dir
    parent_dir = resolve_task_dir(args.parent_dir, repo_root)
    # child_dir ← 调用 resolve_task_dir
    child_dir = resolve_task_dir(args.child_dir, repo_root)

    parent_json_path = parent_dir / FILE_TASK_JSON
    # 计算后赋给 child_json_path
    child_json_path = child_dir / FILE_TASK_JSON

    if not parent_json_path.is_file():
        # 输出信息
        print(colored(f"Error: Parent task.json not found: {args.parent_dir}", Colors.RED), file=sys.stderr)
        return 1

    # 若条件不成立：not child_json_path.is_file()
    if not child_json_path.is_file():
        # 输出信息
        print(colored(f"Error: Child task.json not found: {args.child_dir}", Colors.RED), file=sys.stderr)
        return 1

    parent_data = read_json(parent_json_path)
    # child_data ← 调用 read_json
    child_data = read_json(child_json_path)

    # 若条件不成立：not parent_data or not child_data
    if not parent_data or not child_data:
        # 输出信息
        print(colored("Error: Failed to read task.json", Colors.RED), file=sys.stderr)
        return 1

    # Check if child already has a parent
    # 检查是否child already has a parent
    # existing_parent ← 调用 child_data.get
    existing_parent = child_data.get("parent")
    # 条件分支：existing_parent
    if existing_parent:
        # 输出信息
        print(colored(f"Error: Child task already has a parent: {existing_parent}", Colors.RED), file=sys.stderr)
        return 1

    # Add child to parent's children list
    parent_children = parent_data.get("children", [])
    # 读取属性赋给 child_dir_name
    child_dir_name = child_dir.name
    # 条件分支：child_dir_name not in parent_children
    if child_dir_name not in parent_children:
        # 追加到列表
        parent_children.append(child_dir_name)
        parent_data["children"] = parent_children

    # Set parent in child's task.json
    # 在子任务 task.json 中写入 parent
    # 读取属性赋给 child_data["parent"]
    child_data["parent"] = parent_dir.name

    # Write both
    write_json(parent_json_path, parent_data)
    # 写入文件
    write_json(child_json_path, child_data)

    # 输出信息
    print(colored(f"Linked: {child_dir.name} -> {parent_dir.name}", Colors.GREEN), file=sys.stderr)
    return 0


# =============================================================================
# Command: remove-subtask
# =============================================================================

# 命令：remove-subtask
def cmd_remove_subtask(args: argparse.Namespace) -> int:
    """解除子任务与父任务的关联。"""
    repo_root = get_repo_root()

    parent_dir = resolve_task_dir(args.parent_dir, repo_root)
    child_dir = resolve_task_dir(args.child_dir, repo_root)

    parent_json_path = parent_dir / FILE_TASK_JSON
    child_json_path = child_dir / FILE_TASK_JSON

    if not parent_json_path.is_file():
        print(colored(f"Error: Parent task.json not found: {args.parent_dir}", Colors.RED), file=sys.stderr)
        return 1

    if not child_json_path.is_file():
        print(colored(f"Error: Child task.json not found: {args.child_dir}", Colors.RED), file=sys.stderr)
        return 1

    parent_data = read_json(parent_json_path)
    child_data = read_json(child_json_path)

    if not parent_data or not child_data:
        print(colored("Error: Failed to read task.json", Colors.RED), file=sys.stderr)
        return 1

    # Remove child from parent's children list
    parent_children = parent_data.get("children", [])
    child_dir_name = child_dir.name
    # 条件分支：child_dir_name in parent_children
    if child_dir_name in parent_children:
        # 从集合/列表移除
        parent_children.remove(child_dir_name)
        parent_data["children"] = parent_children

    # Clear parent in child's task.json
    child_data["parent"] = None

    # Write both
    write_json(parent_json_path, parent_data)
    write_json(child_json_path, child_data)

    # 输出信息
    print(colored(f"Unlinked: {child_dir.name} from {parent_dir.name}", Colors.GREEN), file=sys.stderr)
    return 0


# =============================================================================
# Command: set-branch
# =============================================================================

# 命令：set-branch
def cmd_set_branch(args: argparse.Namespace) -> int:
    """设置：Set git branch for task."""
    repo_root = get_repo_root()
    # target_dir ← 调用 resolve_task_dir
    target_dir = resolve_task_dir(args.dir, repo_root)
    # 读取属性赋给 branch
    branch = args.branch

    # 若条件不成立：not branch
    if not branch:
        # 输出信息
        print(colored("Error: Missing arguments", Colors.RED))
        # 输出信息
        print("Usage: python3 task.py set-branch <task-dir> <branch-name>")
        return 1

    # 计算后赋给 task_json
    task_json = target_dir / FILE_TASK_JSON
    # 若条件不成立：not task_json.is_file()
    if not task_json.is_file():
        # 输出信息
        print(colored(f"Error: task.json not found at {target_dir}", Colors.RED))
        return 1

    # data ← 调用 read_json
    data = read_json(task_json)
    # 若条件不成立：not data
    if not data:
        return 1

    data["branch"] = branch  # 下标项 ← branch
    # 写入文件
    write_json(task_json, data)

    # 输出信息
    print(colored(f"✓ Branch set to: {branch}", Colors.GREEN))
    return 0


# =============================================================================
# Command: set-base-branch
# =============================================================================

# 命令：set-base-branch
def cmd_set_base_branch(args: argparse.Namespace) -> int:
    """设置：Set the base branch (PR target) for task."""
    repo_root = get_repo_root()
    target_dir = resolve_task_dir(args.dir, repo_root)
    # 读取属性赋给 base_branch
    base_branch = args.base_branch

    # 若条件不成立：not base_branch
    if not base_branch:
        print(colored("Error: Missing arguments", Colors.RED))
        # 输出信息
        print("Usage: python3 task.py set-base-branch <task-dir> <base-branch>")
        # 输出信息
        print("Example: python3 task.py set-base-branch <dir> develop")
        # 输出信息
        print()
        # 输出信息
        print("This sets the target branch for PR (the branch your feature will merge into).")
        return 1

    task_json = target_dir / FILE_TASK_JSON
    if not task_json.is_file():
        print(colored(f"Error: task.json not found at {target_dir}", Colors.RED))
        return 1

    data = read_json(task_json)
    if not data:
        return 1

    data["base_branch"] = base_branch  # 下标项 ← base_branch
    write_json(task_json, data)

    # 输出信息
    print(colored(f"✓ Base branch set to: {base_branch}", Colors.GREEN))
    # 输出信息
    print(f"  PR will target: {base_branch}")
    return 0


# =============================================================================
# Command: set-scope
# =============================================================================

# 命令：set-scope
def cmd_set_scope(args: argparse.Namespace) -> int:
    """设置：Set scope for PR title."""
    repo_root = get_repo_root()
    target_dir = resolve_task_dir(args.dir, repo_root)
    # 读取属性赋给 scope
    scope = args.scope

    # 若条件不成立：not scope
    if not scope:
        print(colored("Error: Missing arguments", Colors.RED))
        # 输出信息
        print("Usage: python3 task.py set-scope <task-dir> <scope>")
        return 1

    task_json = target_dir / FILE_TASK_JSON
    if not task_json.is_file():
        print(colored(f"Error: task.json not found at {target_dir}", Colors.RED))
        return 1

    data = read_json(task_json)
    if not data:
        return 1

    data["scope"] = scope  # 下标项 ← scope
    write_json(task_json, data)

    # 输出信息
    print(colored(f"✓ Scope set to: {scope}", Colors.GREEN))
    return 0
