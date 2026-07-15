#!/usr/bin/env python3
"""
task_queue 模块：Task queue utility functions.


提供:
list_tasks_by_status   - List tasks by status
list_pending_tasks     - List tasks with pending status
list_tasks_by_assignee - List tasks by assignee
list_my_tasks          - List tasks assigned to current developer
get_task_stats         - Get P0/P1/P2/P3 counts
"""

# 启用延迟注解求值等 future 特性
from __future__ import annotations

# 导入依赖
from pathlib import Path

from .paths import (
    get_repo_root,
    get_developer,
    get_tasks_dir,
)
from .tasks import iter_active_tasks


# 说明：=============================================================================
# 内部辅助
# 说明：=============================================================================

def _task_to_dict(t) -> dict:
    """转换：Convert TaskInfo to the dict format callers expect."""
    # 返回 { "priority": t.priority, "id": t.r…
    return {
        "priority": t.priority,
        "id": t.raw.get("id", ""),
        "title": t.title,
        "status": t.status,
        "assignee": t.assignee or "-",
        "dir": t.dir_name,
        "children": list(t.children),
        "parent": t.parent,
    }


# 说明：=============================================================================
# 公开函数
# 说明：=============================================================================

def list_tasks_by_status(
    filter_status: str | None = None,
    repo_root: Path | None = None
) -> list[dict]:
    """
    列出/遍历：List tasks by status.


    参数:
        filter_status: Optional status filter.
        repo_root: Repository root path. Defaults to auto-detected.


    返回:
        List of task info dicts with keys: priority, id, title, status, assignee.
    """
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # tasks_dir ← 调用 get_tasks_dir
    tasks_dir = get_tasks_dir(repo_root)
    # results 初始化为空列表
    results = []

    # 遍历：t in iter_active_tasks(tasks_dir)
    for t in iter_active_tasks(tasks_dir):
        # 条件分支：filter_status and t.status != filter_stat…
        if filter_status and t.status != filter_status:
            continue  # 跳过本轮循环
        # 追加到列表
        results.append(_task_to_dict(t))

    return results  # 返回 results


def list_pending_tasks(repo_root: Path | None = None) -> list[dict]:
    """
    列出/遍历：List pending tasks.


    参数:
        repo_root: Repository root path. Defaults to auto-detected.


    返回:
        List of task info dicts.
    """
    # 返回 list_tasks_by_status 的调用结果
    return list_tasks_by_status("planning", repo_root)


def list_tasks_by_assignee(
    assignee: str,
    filter_status: str | None = None,
    repo_root: Path | None = None
) -> list[dict]:
    """
    列出/遍历：List tasks assigned to a specific developer.


    参数:
        assignee: Developer name.
        filter_status: Optional status filter.
        repo_root: Repository root path. Defaults to auto-detected.


    返回:
        List of task info dicts.
    """
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # tasks_dir ← 调用 get_tasks_dir
    tasks_dir = get_tasks_dir(repo_root)
    # results 初始化为空列表
    results = []

    # 遍历：t in iter_active_tasks(tasks_dir)
    for t in iter_active_tasks(tasks_dir):
        # 条件分支：(t.assignee or "-") != assignee
        if (t.assignee or "-") != assignee:
            continue  # 跳过本轮循环
        # 条件分支：filter_status and t.status != filter_stat…
        if filter_status and t.status != filter_status:
            continue  # 跳过本轮循环
        # 追加到列表
        results.append(_task_to_dict(t))

    return results  # 返回 results


def list_my_tasks(
    filter_status: str | None = None,
    repo_root: Path | None = None
) -> list[dict]:
    """
    列出/遍历：List tasks assigned to current developer.


    参数:
        filter_status: Optional status filter.
        repo_root: Repository root path. Defaults to auto-detected.


    返回:
        List of task info dicts.


    异常:
        ValueError: If developer not set.
    """
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # developer ← 调用 get_developer
    developer = get_developer(repo_root)
    # 若条件不成立：not developer
    if not developer:
        # 抛出异常：ValueError("Developer not set")
        raise ValueError("Developer not set")

    # 返回 list_tasks_by_assignee 的调用结果
    return list_tasks_by_assignee(developer, filter_status, repo_root)


def get_task_stats(repo_root: Path | None = None) -> dict[str, int]:
    """
    获取：Get task statistics.


    参数:
        repo_root: Repository root path. Defaults to auto-detected.


    返回:
        Dict with keys: P0, P1, P2, P3, Total.
    """
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # tasks_dir ← 调用 get_tasks_dir
    tasks_dir = get_tasks_dir(repo_root)
    # 构造字典赋给 stats
    stats = {"P0": 0, "P1": 0, "P2": 0, "P3": 0, "Total": 0}

    # 遍历：t in iter_active_tasks(tasks_dir)
    for t in iter_active_tasks(tasks_dir):
        # 条件分支：t.priority in stats
        if t.priority in stats:
            # 就地更新 stats[t.priority]
            stats[t.priority] += 1
        # 就地更新 stats["Total"]
        stats["Total"] += 1

    return stats  # 返回 stats


def format_task_stats(stats: dict[str, int]) -> str:
    """
    格式化：Format task stats as string.


    参数:
        stats: Stats dict from get_task_stats.


    返回:
        Formatted string like "P0:0 P1:1 P2:2 P3:0 Total:3".
    """
    # 返回格式化字符串
    return f"P0:{stats['P0']} P1:{stats['P1']} P2:{stats['P2']} P3:{stats['P3']} Total:{stats['Total']}"


# 说明：=============================================================================
# 测试用主入口
# 说明：=============================================================================

# 条件分支：__name__ == "__main__"
# 直接运行本文件时进入入口
if __name__ == "__main__":
    # stats ← 调用 get_task_stats
    stats = get_task_stats()
    # 输出信息
    print(format_task_stats(stats))
    # 输出信息
    print()
    # 输出信息
    print("Pending tasks:")
    # 遍历：task in list_pending_tasks()
    for task in list_pending_tasks():
        # 输出信息
        print(f"  {task['priority']}|{task['id']}|{task['title']}|{task['status']}|{task['assignee']}")
