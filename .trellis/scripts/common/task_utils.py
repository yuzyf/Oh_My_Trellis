#!/usr/bin/env python3
"""
task_utils 模块：Task utility functions.


提供:
is_safe_task_path   - Validate task path is safe to operate on
find_task_by_name   - Find task directory by name
resolve_task_dir    - Resolve task directory from name, relative, or absolute path
archive_task_dir    - Archive task to monthly directory
run_task_hooks      - Run lifecycle hooks for task events
"""

# 启用延迟注解求值等 future 特性
from __future__ import annotations

# 导入依赖
import shutil
import sys
from datetime import datetime
from pathlib import Path

from .paths import get_repo_root, get_tasks_dir


# 说明：=============================================================================
# 路径安全
# 说明：=============================================================================

def is_safe_task_path(task_path: str, repo_root: Path | None = None) -> bool:
    """
    检查/校验：Check if a relative task path is safe to operate on.


    参数:
        task_path: Task path (relative to repo_root).
        repo_root: Repository root path. Defaults to auto-detected.


    返回:
        True if safe, False if dangerous.
    """
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # normalized ← 调用 task_path.replace
    normalized = task_path.replace("\\", "/")

    # 检查空或 null
    if not normalized or normalized == "null":
        # 输出信息
        print("Error: empty or null task path", file=sys.stderr)
        return False  # 返回 False

    # 拒绝绝对路径
    # 条件分支：Path(task_path).is_absolute()
    if Path(task_path).is_absolute():
        # 输出信息
        print(f"Error: absolute path not allowed: {task_path}", file=sys.stderr)
        return False  # 返回 False

    # 拒绝 "."、".."、以 "./" 或 "../" 开头或含 ".." 的路径
    # 条件分支：normalized in (".", "..") or normalized.s…
    if normalized in (".", "..") or normalized.startswith("./") or normalized.startswith("../") or ".." in normalized:
        # 输出信息
        print(f"Error: path traversal not allowed: {task_path}", file=sys.stderr)
        return False  # 返回 False

    # 最终检查：解析后路径不能是仓库根
    # 计算后赋给 abs_path
    abs_path = repo_root / Path(normalized)
    # 条件分支：abs_path.exists()
    if abs_path.exists():
        # try：执行可能失败的逻辑
        try:
            # resolved ← 调用 abs_path.resolve
            resolved = abs_path.resolve()
            # root_resolved ← 调用 repo_root.resolve
            root_resolved = repo_root.resolve()
            # 条件分支：resolved == root_resolved
            if resolved == root_resolved:
                # 输出信息
                print(f"Error: path resolves to repo root: {task_path}", file=sys.stderr)
                return False  # 返回 False
        except (OSError, IOError):
            # 占位（无操作）
            pass

    return True  # 返回 True


def is_within_tasks_dir(task_dir_abs: Path, repo_root: Path | None = None) -> bool:
    """
    检查/校验：Check that a resolved task directory really is a task under the tasks dir.

    A real task lives directly at ``.trellis/tasks/<name>``. This returns True
    only when ``task_dir_abs`` is an immediate child of the tasks directory.

    Guards archive: ``resolve_task_dir`` falls back to ``repo_root/<name>`` for
    an unknown name, so a mistyped ``task.py archive src`` resolves to the real
    ``src/`` source directory. Without this check archive would ``shutil.move``
    it out of the repo. Also rejects the tasks dir itself and anything nested
    under ``archive/`` (already-archived tasks).
    """
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()
    # try：执行可能失败的逻辑
    try:
        # resolved ← 调用 task_dir_abs.resolve
        resolved = task_dir_abs.resolve()
        # tasks_resolved ← 调用 get_tasks_dir(repo_root).reso…
        tasks_resolved = get_tasks_dir(repo_root).resolve()
    except (OSError, RuntimeError):
        return False  # 返回 False
    # 返回 resolved.parent == tasks_resolved
    return resolved.parent == tasks_resolved


# 说明：=============================================================================
# 任务查找
# 说明：=============================================================================

def find_task_by_name(task_name: str, tasks_dir: Path) -> Path | None:
    """
    查找：Find task directory by name (exact or suffix match).


    参数:
        task_name: Task name to find.
        tasks_dir: Tasks directory path.


    返回:
        Absolute path to task directory, or None if not found.
    """
    # 若条件不成立：not task_name or not tasks_dir or not tasks_dir.is
    if not task_name or not tasks_dir or not tasks_dir.is_dir():
        return None  # 返回 None

    # 先精确匹配
    # 计算后赋给 exact_match
    exact_match = tasks_dir / task_name
    # 条件分支：exact_match.is_dir()
    if exact_match.is_dir():
        return exact_match  # 返回 exact_match

    # 再后缀匹配（如 "my-task" 匹配 "01-21-my-task"）
    for d in tasks_dir.iterdir():
        # 条件分支：d.is_dir() and d.name.endswith(f"-{task_n…
        if d.is_dir() and d.name.endswith(f"-{task_name}"):
            return d  # 返回 d

    return None  # 返回 None


# 说明：=============================================================================
# 归档操作
# 说明：=============================================================================

def archive_task_dir(task_dir_abs: Path, repo_root: Path | None = None) -> Path | None:
    """
    archive_task_dir：Archive a task directory to archive/{YYYY-MM}/.


    参数:
        task_dir_abs: Absolute path to task directory.
        repo_root: Repository root path. Defaults to auto-detected.


    返回:
        Path to archived directory, or None on error.
    """
    # 若条件不成立：not task_dir_abs.is_dir()
    if not task_dir_abs.is_dir():
        # 输出信息
        print(f"Error: task directory not found: {task_dir_abs}", file=sys.stderr)
        return None  # 返回 None

    # 取任务父级 tasks 目录
    # 读取属性赋给 tasks_dir
    tasks_dir = task_dir_abs.parent
    # 计算后赋给 archive_dir
    archive_dir = tasks_dir / "archive"
    # year_month ← 调用 datetime.now().strftime
    year_month = datetime.now().strftime("%Y-%m")
    # 计算后赋给 month_dir
    month_dir = archive_dir / year_month

    # 创建 archive 目录
    # try：执行可能失败的逻辑
    try:
        # 创建目录
        month_dir.mkdir(parents=True, exist_ok=True)
    except (OSError, IOError) as e:
        # 输出信息
        print(f"Error: Failed to create archive directory: {e}", file=sys.stderr)
        return None  # 返回 None

    # 把任务移入 archive
    # 读取属性赋给 task_name
    task_name = task_dir_abs.name
    # 计算后赋给 dest
    dest = month_dir / task_name

    # try：执行可能失败的逻辑
    try:
        # 调用 shutil.move
        shutil.move(str(task_dir_abs), str(dest))
    except (OSError, IOError, shutil.Error) as e:
        # 输出信息
        print(f"Error: Failed to move task to archive: {e}", file=sys.stderr)
        return None  # 返回 None

    return dest  # 返回 dest


def archive_task_complete(
    task_dir_abs: Path,
    repo_root: Path | None = None
) -> dict[str, str]:
    """
    archive_task_complete：Complete archive workflow: archive directory.


    参数:
        task_dir_abs: Absolute path to task directory.
        repo_root: Repository root path. Defaults to auto-detected.


    返回:
        Dict with archive result info.
    """
    # 若条件不成立：not task_dir_abs.is_dir()
    if not task_dir_abs.is_dir():
        # 输出信息
        print(f"Error: task directory not found: {task_dir_abs}", file=sys.stderr)
        return {}  # 返回字典结果

    # archive_dest ← 调用 archive_task_dir
    archive_dest = archive_task_dir(task_dir_abs, repo_root)
    # 条件分支：archive_dest
    if archive_dest:
        # 返回 {"archived_to": str(archive_dest)}
        return {"archived_to": str(archive_dest)}

    return {}  # 返回字典结果


# 说明：=============================================================================
# 任务目录解析
# 说明：=============================================================================

def resolve_task_dir(target_dir: str, repo_root: Path) -> Path:
    """
    解析/解析出：Resolve task directory to absolute path.

    Supports:
    - Absolute path: /path/to/task
    - Relative path: .trellis/tasks/01-31-my-task
    - Task name: my-task (uses find_task_by_name for lookup)


    参数:
        target_dir: Task directory specification.
        repo_root: Repository root path.


    返回:
        Resolved absolute path.
    """
    # 若条件不成立：not target_dir
    if not target_dir:
        # 返回 Path 的调用结果
        return Path()

    # normalized ← 调用 target_dir.replace
    normalized = target_dir.replace("\\", "/")
    # while 循环：normalized.startswith("./")
    while normalized.startswith("./"):
        # 按键/下标取值赋给 normalized
        normalized = normalized[2:]

    # 绝对路径
    # 条件分支：Path(target_dir).is_absolute()
    if Path(target_dir).is_absolute():
        # 返回 Path 的调用结果
        return Path(target_dir)

    # 相对路径（含路径分隔符或以 .trellis 开头）
    # 条件分支："/" in normalized or normalized.startswit…
    if "/" in normalized or normalized.startswith(".trellis"):
        # 返回 repo_root / Path(normalized)
        return repo_root / Path(normalized)

    # 任务名——在 tasks 目录中查找
    # tasks_dir ← 调用 get_tasks_dir
    tasks_dir = get_tasks_dir(repo_root)
    # found ← 调用 find_task_by_name
    found = find_task_by_name(target_dir, tasks_dir)
    # 条件分支：found
    if found:
        return found  # 返回 found

    # 回退为按相对路径处理
    # 返回 repo_root / Path(normalized)
    return repo_root / Path(normalized)


# 说明：=============================================================================
# 生命周期钩子
# 说明：=============================================================================

def run_task_hooks(event: str, task_json_path: Path, repo_root: Path) -> None:
    """
    执行：Run lifecycle hooks for a task event.


    参数:
        event: Event name (e.g. "after_create").
        task_json_path: Absolute path to the task's task.json.
        repo_root: Repository root for cwd and config lookup.
    """
    # 局部导入 os
    import os
    # 局部导入 subprocess
    import subprocess

    # 局部导入 config
    from .config import get_hooks
    # 局部导入 log
    from .log import Colors, colored

    # commands ← 调用 get_hooks
    commands = get_hooks(event, repo_root)
    # 若条件不成立：not commands
    if not commands:
        # 返回（无值）
        return

    # 构造字典赋给 env
    env = {**os.environ, "TASK_JSON_PATH": str(task_json_path)}

    # 遍历：cmd in commands
    for cmd in commands:
        # try：执行可能失败的逻辑
        try:
            # result ← 调用 subprocess.run
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=repo_root,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            # 条件分支：result.returncode != 0
            if result.returncode != 0:
                # 输出信息
                print(
                    colored(f"[WARN] Hook failed ({event}): {cmd}", Colors.YELLOW),
                    file=sys.stderr,
                )
                # 条件分支：result.stderr.strip()
                if result.stderr.strip():
                    # 输出信息
                    print(f"  {result.stderr.strip()}", file=sys.stderr)
        except Exception as e:
            # 输出信息
            print(
                colored(f"[WARN] Hook error ({event}): {cmd} — {e}", Colors.YELLOW),
                file=sys.stderr,
            )


# 说明：=============================================================================
# 测试用主入口
# 说明：=============================================================================

# 条件分支：__name__ == "__main__"
# 直接运行本文件时进入入口
if __name__ == "__main__":
    # repo ← 调用 get_repo_root
    repo = get_repo_root()
    # tasks ← 调用 get_tasks_dir
    tasks = get_tasks_dir(repo)

    # 输出信息
    print(f"Tasks dir: {tasks}")
    # 输出信息
    print(f"is_safe_task_path('.trellis/tasks/test'): {is_safe_task_path('.trellis/tasks/test', repo)}")
    # 输出信息
    print(f"is_safe_task_path('../test'): {is_safe_task_path('../test', repo)}")
