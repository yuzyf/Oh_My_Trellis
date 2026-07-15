#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理脚本（task）。

用法:
    python3 task.py create "<title>" [--slug <name>] [--assignee <dev>] [--priority P0|P1|P2|P3] [--parent <dir>] [--package <pkg>] [--no-start]
    python3 task.py add-context <dir> <file> <path> [reason]
    python3 task.py validate <dir>
    python3 task.py list-context <dir>
    python3 task.py start <dir>
    python3 task.py current [--source]
    python3 task.py finish
    python3 task.py set-branch <dir> <branch>
    python3 task.py set-base-branch <dir> <branch>
    python3 task.py set-scope <dir> <scope>
    python3 task.py archive <task-dir>
    python3 task.py list
    python3 task.py list-archive [month]
    python3 task.py add-subtask <parent-dir> <child-dir>
    python3 task.py remove-subtask <parent-dir> <child-dir>
"""

# 启用延迟注解求值等 future 特性
from __future__ import annotations

# 导入依赖
import argparse
import sys

from common.log import Colors, colored
from common.paths import (
    DIR_WORKFLOW,
    DIR_TASKS,
    FILE_TASK_JSON,
    get_repo_root,
    get_developer,
    get_tasks_dir,
    get_current_task,
)
from common.active_task import (
    clear_active_task,
    resolve_active_task,
    resolve_context_key,
    set_active_task,
)
from common.io import read_json, write_json
from common.task_utils import resolve_task_dir, run_task_hooks
from common.tasks import iter_active_tasks, children_progress

# 从拆分模块导入命令处理函数（并再导出以兼容 plan.py）
from common.task_store import (
    cmd_create,
    cmd_archive,
    cmd_set_branch,
    cmd_set_base_branch,
    cmd_set_scope,
    cmd_add_subtask,
    cmd_remove_subtask,
)
from common.task_context import (
    cmd_add_context,
    cmd_validate,
    cmd_list_context,
)


# =============================================================================
# 命令：start / finish
# =============================================================================

def cmd_start(args: argparse.Namespace) -> int:
    """设置：Set active task."""
    # repo_root ← 调用 get_repo_root
    repo_root = get_repo_root()
    # 读取属性赋给 task_input
    task_input = args.dir

    # 若条件不成立：not task_input
    if not task_input:
        # 输出信息
        print(colored("Error: task directory or name required", Colors.RED))
        # 返回常量 1
        return 1

    # 解析任务目录（支持任务名、相对路径或绝对路径）
    # full_path ← 调用 resolve_task_dir
    full_path = resolve_task_dir(task_input, repo_root)

    # 若条件不成立：not full_path.is_dir()
    if not full_path.is_dir():
        # 输出信息
        print(colored(f"Error: Task not found: {task_input}", Colors.RED))
        # 输出信息
        print("Hint: Use task name (e.g., 'my-task') or full path (e.g., '.trellis/tasks/01-31-my-task')")
        # 返回常量 1
        return 1

    # 转为相对路径以便存储
    # try：执行可能失败的逻辑
    try:
        # task_dir ← 调用 full_path.relative_to(repo_ro…
        task_dir = full_path.relative_to(repo_root).as_posix()
    except ValueError:
        # task_dir ← 调用 str
        task_dir = str(full_path)

    # 计算后赋给 task_json_path
    task_json_path = full_path / FILE_TASK_JSON

    # 若条件不成立：not resolve_context_key()
    if not resolve_context_key():
        # 降级模式：无会话身份可用。
        # Hook 未注入 TRELLIS_CONTEXT_ID（常见于 Windows + Claude Code、
        # --continue 恢复路径、fork 分发、hooks 禁用等）。跳过
        # 每会话指针写入；AI 依据对话上下文继续。
        # 输出信息
        print(colored(
            "ℹ Session identity not available; active-task pointer not persisted "
            "this session (degraded mode). AI continues based on conversation context.",
            Colors.YELLOW,
        ))
        # 输出信息
        print(colored(
            "Hint: run inside an AI IDE/session that exposes session identity, "
            "or set TRELLIS_CONTEXT_ID before running task.py start.",
            Colors.YELLOW,
        ))

        # 仍把 task.json 状态从 planning 改为 in_progress，以便后续阶段继续。
        # 条件分支：task_json_path.is_file()
        if task_json_path.is_file():
            # data ← 调用 read_json
            data = read_json(task_json_path)
            # 条件分支：data and data.get("status") == "planning"
            if data and data.get("status") == "planning":
                # 初始化 data["status"]
                data["status"] = "in_progress"
                # 条件分支：write_json(task_json_path, data)
                if write_json(task_json_path, data):
                    # 输出信息
                    print(colored("✓ Status: planning → in_progress (degraded)", Colors.GREEN))
            # 调用 run_task_hooks
            run_task_hooks("after_start", task_json_path, repo_root)
        return 0  # 返回 0

    # active ← 调用 set_active_task
    active = set_active_task(task_dir, repo_root)
    # 条件分支：active
    if active:
        # 输出信息
        print(colored(f"✓ Current task set to: {task_dir}", Colors.GREEN))
        # 输出信息
        print(f"Source: {active.source}")

        # 条件分支：task_json_path.is_file()
        if task_json_path.is_file():
            # data ← 调用 read_json
            data = read_json(task_json_path)
            # 条件分支：data and data.get("status") == "planning"
            if data and data.get("status") == "planning":
                # 初始化 data["status"]
                data["status"] = "in_progress"
                # 条件分支：write_json(task_json_path, data)
                if write_json(task_json_path, data):
                    # 输出信息
                    print(colored("✓ Status: planning → in_progress", Colors.GREEN))

        # 输出信息
        print()
        # 输出信息
        print(colored("The hook will now inject context from this task's jsonl files.", Colors.BLUE))

        # 调用 run_task_hooks
        run_task_hooks("after_start", task_json_path, repo_root)
        return 0  # 返回 0
    else:
        # 输出信息
        print(colored("Error: Failed to set current task", Colors.RED))
        # 返回常量 1
        return 1


def cmd_finish(args: argparse.Namespace) -> int:
    """清空/重置：Clear active task."""
    # repo_root ← 调用 get_repo_root
    repo_root = get_repo_root()
    # active ← 调用 clear_active_task
    active = clear_active_task(repo_root)
    # 读取属性赋给 current
    current = active.task_path

    # 若条件不成立：not current
    if not current:
        # 输出信息
        print(colored("No current task set", Colors.YELLOW))
        return 0  # 返回 0

    # 解析/定位 task.json path before clearing
    # 计算后赋给 task_json_path
    task_json_path = repo_root / current / FILE_TASK_JSON

    # 输出信息
    print(colored(f"✓ Cleared current task (was: {current})", Colors.GREEN))
    # 输出信息
    print(f"Source: {active.source}")

    # 条件分支：task_json_path.is_file()
    if task_json_path.is_file():
        # 调用 run_task_hooks
        run_task_hooks("after_finish", task_json_path, repo_root)
    return 0  # 返回 0


def cmd_current(args: argparse.Namespace) -> int:
    """显示当前活动任务。"""
    # repo_root ← 调用 get_repo_root
    repo_root = get_repo_root()
    # active ← 调用 resolve_active_task
    active = resolve_active_task(repo_root)

    # 条件分支：args.source
    if args.source:
        # 输出信息
        print(f"Current task: {active.task_path or '(none)'}")
        # 输出信息
        print(f"Source: {active.source}")
        # 条件分支：active.stale
        if active.stale:
            # 输出信息
            print("State: stale")
        # 按条件返回不同值
        return 0 if active.task_path else 1

    # 条件分支：active.task_path
    if active.task_path:
        # 输出信息
        print(active.task_path)
        return 0  # 返回 0

    # 返回常量 1
    return 1


# =============================================================================
# 命令：list
# =============================================================================

def cmd_list(args: argparse.Namespace) -> int:
    """列出/遍历：List active tasks."""
    # repo_root ← 调用 get_repo_root
    repo_root = get_repo_root()
    # tasks_dir ← 调用 get_tasks_dir
    tasks_dir = get_tasks_dir(repo_root)
    # current_task ← 调用 get_current_task
    current_task = get_current_task(repo_root)
    # developer ← 调用 get_developer
    developer = get_developer(repo_root)
    # 读取属性赋给 filter_mine
    filter_mine = args.mine
    # 读取属性赋给 filter_status
    filter_status = args.status

    # 条件分支：filter_mine
    if filter_mine:
        # 若条件不成立：not developer
        if not developer:
            # 输出信息
            print(colored("Error: No developer set. Run init_developer.py first", Colors.RED), file=sys.stderr)
            # 返回常量 1
            return 1
        # 输出信息
        print(colored(f"My tasks (assignee: {developer}):", Colors.BLUE))
    else:
        # 输出信息
        print(colored("All active tasks:", Colors.BLUE))
    # 输出信息
    print()

    # 单次遍历：通过共享迭代器收集全部任务
    # 用推导式生成 all_tasks
    all_tasks = {t.dir_name: t for t in iter_active_tasks(tasks_dir)}
    # 用推导式生成 all_statuses
    all_statuses = {name: t.status for name, t in all_tasks.items()}

    # 按层级展示任务
    # 初始化 count
    count = 0

    # 定义函数 _print_task
    def _print_task(dir_name: str, indent: int = 0) -> None:
        # 声明非局部变量：count
        nonlocal count
        # 按键/下标取值赋给 t
        t = all_tasks[dir_name]

        # 应用 --mine 过滤
        # 条件分支：filter_mine and (t.assignee or "-") != de…
        if filter_mine and (t.assignee or "-") != developer:
            # 返回（无值）
            return

        # 应用 --status 过滤
        # 条件分支：filter_status and t.status != filter_stat…
        if filter_status and t.status != filter_status:
            # 返回（无值）
            return

        # 拼出字符串赋给 relative_path
        relative_path = f"{DIR_WORKFLOW}/{DIR_TASKS}/{dir_name}"
        # 初始化 marker
        marker = ""
        # 条件分支：relative_path == current_task
        if relative_path == current_task:
            # 拼出字符串赋给 marker
            marker = f" {colored('<- current', Colors.GREEN)}"

        # 子任务进度
        # progress ← 调用 children_progress
        progress = children_progress(t.children, all_statuses)

        # 包标签
        # 按条件取值赋给 pkg_tag
        pkg_tag = f" @{t.package}" if t.package else ""

        # 计算后赋给 prefix
        prefix = "  " * indent + "  - "

        # 条件分支：filter_mine
        if filter_mine:
            # 输出信息
            print(f"{prefix}{dir_name}/ ({t.status}){pkg_tag}{progress}{marker}")
        else:
            # 输出信息
            print(f"{prefix}{dir_name}/ ({t.status}){pkg_tag}{progress} [{colored(t.assignee or '-', Colors.CYAN)}]{marker}")
        # 就地更新 count
        count += 1

        # 缩进打印子任务
        for child_name in t.children:
            # 条件分支：child_name in all_tasks
            if child_name in all_tasks:
                # 调用 _print_task
                _print_task(child_name, indent + 1)

    # 只展示无 parent 的顶层任务
    for dir_name in sorted(all_tasks.keys()):
        # 若条件不成立：not all_tasks[dir_name].parent
        if not all_tasks[dir_name].parent:
            # 调用 _print_task
            _print_task(dir_name)

    # 条件分支：count == 0
    if count == 0:
        # 条件分支：filter_mine
        if filter_mine:
            # 输出信息
            print("  (no tasks assigned to you)")
        else:
            # 输出信息
            print("  (no active tasks)")

    # 输出信息
    print()
    # 输出信息
    print(f"Total: {count} task(s)")
    return 0  # 返回 0


# =============================================================================
# 命令：list-archive
# =============================================================================

def cmd_list_archive(args: argparse.Namespace) -> int:
    """列出/遍历：List archived tasks."""
    # repo_root ← 调用 get_repo_root
    repo_root = get_repo_root()
    # tasks_dir ← 调用 get_tasks_dir
    tasks_dir = get_tasks_dir(repo_root)
    # 计算后赋给 archive_dir
    archive_dir = tasks_dir / "archive"
    # 读取属性赋给 month
    month = args.month

    # 输出信息
    print(colored("Archived tasks:", Colors.BLUE))
    # 输出信息
    print()

    # 条件分支：month
    if month:
        # 计算后赋给 month_dir
        month_dir = archive_dir / month
        # 条件分支：month_dir.is_dir()
        if month_dir.is_dir():
            # 输出信息
            print(f"[{month}]")
            # 遍历：d in sorted(month_dir.iterdir())
            for d in sorted(month_dir.iterdir()):
                # 条件分支：d.is_dir()
                if d.is_dir():
                    # 输出信息
                    print(f"  - {d.name}/")
        else:
            # 输出信息
            print(f"  No archives for {month}")
    else:
        # 条件分支：archive_dir.is_dir()
        if archive_dir.is_dir():
            # 遍历：month_dir in sorted(archive_dir.iterdir())
            for month_dir in sorted(archive_dir.iterdir()):
                # 条件分支：month_dir.is_dir()
                if month_dir.is_dir():
                    # 读取属性赋给 month_name
                    month_name = month_dir.name
                    # count ← 调用 sum
                    count = sum(1 for d in month_dir.iterdir() if d.is_dir())
                    # 输出信息
                    print(f"[{month_name}] - {count} task(s)")

    return 0  # 返回 0


# =============================================================================
# 标识：Help
# =============================================================================

def show_usage() -> None:
    """显示用法帮助。"""
    # 输出信息
    print("""Task Management Script

Usage:
  python3 task.py create <title>                     Create new task directory
  python3 task.py create <title> --package <pkg>     Create task for a specific package
  python3 task.py create <title> --parent <dir>      Create task as child of parent
  python3 task.py create <title> --no-start          Create without making it active in this session
  python3 task.py add-context <dir> <jsonl> <path> [reason]  Add entry to jsonl
  python3 task.py validate <dir>                     Validate jsonl files
  python3 task.py list-context <dir>                 List jsonl entries
  python3 task.py start <dir>                        Set active task
  python3 task.py current [--source]                 Show active task
  python3 task.py finish                             Clear active task
  python3 task.py set-branch <dir> <branch>          Set git branch
  python3 task.py set-base-branch <dir> <branch>     Set PR target branch
  python3 task.py set-scope <dir> <scope>            Set scope for PR title
  python3 task.py archive <task-dir>                 Archive completed task
  python3 task.py add-subtask <parent> <child>       Link child task to parent
  python3 task.py remove-subtask <parent> <child>    Unlink child from parent
  python3 task.py list [--mine] [--status <status>]  List tasks
  python3 task.py list-archive [YYYY-MM]             List archived tasks

Monorepo options:
  --package <pkg>      Package name (validated against config.yaml packages)

List options:
  --mine, -m           Show only tasks assigned to current developer
  --status, -s <s>     Filter by status (planning, in_progress, review, completed)

Examples:
  python3 task.py create "Add login feature" --slug add-login
  python3 task.py create "Add login feature" --slug add-login --package cli
  python3 task.py create "Child task" --slug child --parent .trellis/tasks/01-21-parent
  python3 task.py add-context <dir> implement .trellis/spec/cli/backend/auth.md "Auth guidelines"
  python3 task.py set-branch <dir> task/add-login
  python3 task.py start .trellis/tasks/01-21-add-login
  python3 task.py current --source
  python3 task.py finish
  python3 task.py archive add-login
  python3 task.py add-subtask parent-task child-task  # Link existing tasks
  python3 task.py remove-subtask parent-task child-task
  python3 task.py list                               # List all active tasks
  python3 task.py list --mine                        # List my tasks only
  python3 task.py list --mine --status in_progress   # List my in-progress tasks
""")


# =============================================================================
# 主入口
# =============================================================================

def main() -> int:
    """入口：CLI entry point."""
    # 废弃防护：`init-context` 已在 v0.5.0-beta.12 移除。
    # 尽早检测，避免 argparse 用泛化的
    # "invalid choice" 错误掩盖真实原因。
    # 条件分支：len(sys.argv) >= 2 and sys.argv[1] == "in…
    if len(sys.argv) >= 2 and sys.argv[1] == "init-context":
        # 输出信息
        print(
            colored(
                "Error: `task.py init-context` was removed in v0.5.0-beta.12.",
                Colors.RED,
            ),
            file=sys.stderr,
        )
        # 输出信息
        print(
            "implement.jsonl / check.jsonl are now seeded on `task.py create` for",
            file=sys.stderr,
        )
        # 输出信息
        print(
            "sub-agent-capable platforms and curated by the AI during planning when needed.",
            file=sys.stderr,
        )
        # 输出信息
        print("See .trellis/workflow.md planning artifact guidance or run:", file=sys.stderr)
        # 输出信息
        print(
            "  python3 ./.trellis/scripts/get_context.py --mode phase --step 1",
            file=sys.stderr,
        )
        # 输出信息
        print(
            "Use `task.py add-context <dir> implement|check <path> <reason>` to append entries.",
            file=sys.stderr,
        )
        # 返回常量 2
        return 2

    # parser ← 调用 argparse.ArgumentParser
    parser = argparse.ArgumentParser(
        description="Task Management Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    # subparsers ← 调用 parser.add_subparsers
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # 标识：create
    # p_create ← 调用 subparsers.add_parser
    p_create = subparsers.add_parser("create", help="Create new task")
    # 注册 CLI 参数/子命令
    p_create.add_argument("title", help="Task title")
    # 注册 CLI 参数/子命令
    p_create.add_argument("--slug", "-s", help="Task slug without the MM-DD date prefix")
    # 注册 CLI 参数/子命令
    p_create.add_argument("--assignee", "-a", help="Assignee developer")
    # 注册 CLI 参数/子命令
    p_create.add_argument("--priority", "-p", default="P2", help="Priority (P0-P3)")
    # 注册 CLI 参数/子命令
    p_create.add_argument("--description", "-d", help="Task description")
    # 注册 CLI 参数/子命令
    p_create.add_argument("--parent", help="Parent task directory (establishes subtask link)")
    # 注册 CLI 参数/子命令
    p_create.add_argument("--package", help="Package name for monorepo projects")
    # 注册 CLI 参数/子命令
    p_create.add_argument(
        "--no-start",
        action="store_true",
        help="Create the task without making it active in this session",
    )

    # 标识：add-context
    # p_add ← 调用 subparsers.add_parser
    p_add = subparsers.add_parser("add-context", help="Add context entry")
    # 注册 CLI 参数/子命令
    p_add.add_argument("dir", help="Task directory")
    # 注册 CLI 参数/子命令
    p_add.add_argument("file", help="JSONL file (implement|check)")
    # 注册 CLI 参数/子命令
    p_add.add_argument("path", help="File path to add")
    # 注册 CLI 参数/子命令
    p_add.add_argument("reason", nargs="?", help="Reason for adding")

    # 标识：validate
    # p_validate ← 调用 subparsers.add_parser
    p_validate = subparsers.add_parser("validate", help="Validate context files")
    # 注册 CLI 参数/子命令
    p_validate.add_argument("dir", help="Task directory")

    # 标识：list-context
    # p_listctx ← 调用 subparsers.add_parser
    p_listctx = subparsers.add_parser("list-context", help="List context entries")
    # 注册 CLI 参数/子命令
    p_listctx.add_argument("dir", help="Task directory")

    # 标识：start
    # p_start ← 调用 subparsers.add_parser
    p_start = subparsers.add_parser("start", help="Set active task")
    # 注册 CLI 参数/子命令
    p_start.add_argument("dir", help="Task directory")

    # 标识：current
    # p_current ← 调用 subparsers.add_parser
    p_current = subparsers.add_parser("current", help="Show active task")
    # 注册 CLI 参数/子命令
    p_current.add_argument("--source", action="store_true",
                           help="Show active task source")

    # 标识：finish
    # 注册 CLI 参数/子命令
    subparsers.add_parser("finish", help="Clear active task")

    # 标识：set-branch
    # p_branch ← 调用 subparsers.add_parser
    p_branch = subparsers.add_parser("set-branch", help="Set git branch")
    # 注册 CLI 参数/子命令
    p_branch.add_argument("dir", help="Task directory")
    # 注册 CLI 参数/子命令
    p_branch.add_argument("branch", help="Branch name")

    # 标识：set-base-branch
    # p_base ← 调用 subparsers.add_parser
    p_base = subparsers.add_parser("set-base-branch", help="Set PR target branch")
    # 注册 CLI 参数/子命令
    p_base.add_argument("dir", help="Task directory")
    # 注册 CLI 参数/子命令
    p_base.add_argument("base_branch", help="Base branch name (PR target)")

    # 标识：set-scope
    # p_scope ← 调用 subparsers.add_parser
    p_scope = subparsers.add_parser("set-scope", help="Set scope")
    # 注册 CLI 参数/子命令
    p_scope.add_argument("dir", help="Task directory")
    # 注册 CLI 参数/子命令
    p_scope.add_argument("scope", help="Scope name")

    # 标识：archive
    # p_archive ← 调用 subparsers.add_parser
    p_archive = subparsers.add_parser("archive", help="Archive task")
    # 注册 CLI 参数/子命令
    p_archive.add_argument("name", help="Task directory or name")
    # 注册 CLI 参数/子命令
    p_archive.add_argument("--no-commit", action="store_true", help="Skip auto git commit after archive")

    # 标识：list
    # p_list ← 调用 subparsers.add_parser
    p_list = subparsers.add_parser("list", help="List tasks")
    # 注册 CLI 参数/子命令
    p_list.add_argument("--mine", "-m", action="store_true", help="My tasks only")
    # 注册 CLI 参数/子命令
    p_list.add_argument("--status", "-s", help="Filter by status")

    # 标识：add-subtask
    # p_addsub ← 调用 subparsers.add_parser
    p_addsub = subparsers.add_parser("add-subtask", help="Link child task to parent")
    # 注册 CLI 参数/子命令
    p_addsub.add_argument("parent_dir", help="Parent task directory")
    # 注册 CLI 参数/子命令
    p_addsub.add_argument("child_dir", help="Child task directory")

    # 标识：remove-subtask
    # p_rmsub ← 调用 subparsers.add_parser
    p_rmsub = subparsers.add_parser("remove-subtask", help="Unlink child task from parent")
    # 注册 CLI 参数/子命令
    p_rmsub.add_argument("parent_dir", help="Parent task directory")
    # 注册 CLI 参数/子命令
    p_rmsub.add_argument("child_dir", help="Child task directory")

    # 标识：list-archive
    # p_listarch ← 调用 subparsers.add_parser
    p_listarch = subparsers.add_parser("list-archive", help="List archived tasks")
    # 注册 CLI 参数/子命令
    p_listarch.add_argument("month", nargs="?", help="Month (YYYY-MM)")

    # args ← 调用 parser.parse_args
    args = parser.parse_args()

    # 若条件不成立：not args.command
    if not args.command:
        # 调用 show_usage
        show_usage()
        # 返回常量 1
        return 1

    # 构造字典赋给 commands
    commands = {
        "create": cmd_create,
        "add-context": cmd_add_context,
        "validate": cmd_validate,
        "list-context": cmd_list_context,
        "start": cmd_start,
        "current": cmd_current,
        "finish": cmd_finish,
        "set-branch": cmd_set_branch,
        "set-base-branch": cmd_set_base_branch,
        "set-scope": cmd_set_scope,
        "archive": cmd_archive,
        "add-subtask": cmd_add_subtask,
        "remove-subtask": cmd_remove_subtask,
        "list": cmd_list,
        "list-archive": cmd_list_archive,
    }

    # 条件分支：args.command in commands
    if args.command in commands:
        # 返回 commands[args.command] 的调用结果
        return commands[args.command](args)
    else:
        # 调用 show_usage
        show_usage()
        # 返回常量 1
        return 1


# 条件分支：__name__ == "__main__"
# 直接运行本文件时进入入口
if __name__ == "__main__":
    # 结束进程/解析：sys.exit
    sys.exit(main())
