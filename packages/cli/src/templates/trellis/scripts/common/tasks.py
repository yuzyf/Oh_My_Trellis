"""
tasks 模块：Task data access layer.

Single source of truth for loading and iterating task directories.
Replaces scattered task.json parsing across 9+ files.


提供:
load_task          — Load a single task by directory path
iter_active_tasks  — Iterate all non-archived tasks (sorted)
get_all_statuses   — Get {dir_name: status} map for children progress
"""

# 启用延迟注解求值等 future 特性
from __future__ import annotations

# 导入依赖
from collections.abc import Iterator
from pathlib import Path

from .io import read_json
from .paths import FILE_TASK_JSON
from .types import TaskInfo


def load_task(task_dir: Path) -> TaskInfo | None:
    """
    加载/读取：Load task from a directory containing task.json.


    参数:
        task_dir: Absolute path to the task directory.


    返回:
        TaskInfo if task.json exists and is valid, None otherwise.
    """
    # 计算后赋给 task_json
    task_json = task_dir / FILE_TASK_JSON
    # 若条件不成立：not task_json.is_file()
    if not task_json.is_file():
        return None  # 返回 None

    # data ← 调用 read_json
    data = read_json(task_json)
    # 若条件不成立：not data
    if not data:
        return None  # 返回 None

    # 返回 TaskInfo 的调用结果
    return TaskInfo(
        dir_name=task_dir.name,
        directory=task_dir,
        title=data.get("title") or data.get("name") or "unknown",
        status=data.get("status", "unknown"),
        assignee=data.get("assignee", ""),
        priority=data.get("priority", "P2"),
        children=tuple(data.get("children", [])),
        parent=data.get("parent"),
        package=data.get("package"),
        raw=data,
    )


def iter_active_tasks(tasks_dir: Path) -> Iterator[TaskInfo]:
    """
    列出/遍历：Iterate all active (non-archived) tasks, sorted by directory name.

    Skips the "archive" directory and directories without valid task.json.


    参数:
        tasks_dir: Path to the tasks directory.

    Yields:
        TaskInfo for each valid task.
    """
    # 若条件不成立：not tasks_dir.is_dir()
    if not tasks_dir.is_dir():
        # 返回（无值）
        return

    # 遍历：d in sorted(tasks_dir.iterdir())
    for d in sorted(tasks_dir.iterdir()):
        # 若条件不成立：not d.is_dir() or d.name == "archive"
        if not d.is_dir() or d.name == "archive":
            continue  # 跳过本轮循环
        # info ← 调用 load_task
        info = load_task(d)
        # 若已有值：info is not None
        if info is not None:
            yield info  # 产出已成功加载的 TaskInfo


def get_all_statuses(tasks_dir: Path) -> dict[str, str]:
    """返回所有活动任务的 {dir_name: status} 映射。

用于在不加载完整 TaskInfo 时计算子任务进度。

参数:
    tasks_dir: 任务目录路径。

返回:
    目录名到状态字符串的字典。
"""
    return {t.dir_name: t.status for t in iter_active_tasks(tasks_dir)}  # 返回结果


def children_progress(
    children: tuple[str, ...] | list[str],
    all_statuses: dict[str, str],
) -> str:
    """格式化子任务进度字符串，形如 " [2/3 done]"。

参数:
    children: 子任务目录名列表。
    all_statuses: 来自 get_all_statuses() 的状态表。

返回:
    格式化字符串；无子任务时返回 ""。
"""
    # 若条件不成立：not children
    if not children:
        return ""  # 返回空字符串
    # 活动状态表中缺失的子任务视为已归档（cmd_archive
    # 在移动目录前会把 status 设为 completed）。计为完成，
    # 避免子任务归档后父任务进度回退。
    # done ← 调用 sum
    done = sum(
        1 for c in children
        if c not in all_statuses or all_statuses.get(c) in ("completed", "done")
    )
    return f" [{done}/{len(children)} done]"  # 返回格式化字符串
