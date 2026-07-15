#!/usr/bin/env python3
"""
linear_sync 模块：Linear sync hook for Trellis task lifecycle.

Syncs task events to Linear via the `linearis` CLI.

Usage (called automatically by task.py hooks):
python3 .trellis/scripts/hooks/linear_sync.py create
python3 .trellis/scripts/hooks/linear_sync.py start
python3 .trellis/scripts/hooks/linear_sync.py archive

Manual usage:
TASK_JSON_PATH=.trellis/tasks/<name>/task.json python3 .trellis/scripts/hooks/linear_sync.py sync

Environment:
TASK_JSON_PATH  - Absolute path to task.json (set by task.py)

Configuration:
.trellis/hooks.local.json  - Local config (gitignored), example:
{
  "linear": {
    "team": "TEAM_KEY",
    "project": "Project Name",
    "assignees": {
      "dev-name": "linear-user-id"
    }
  }
}
"""

# 启用延迟注解求值等 future 特性
from __future__ import annotations

# 导入依赖
import json
import os
import subprocess
import sys
from pathlib import Path

# ─── 配置 ───

# Trellis 优先级 → Linear 优先级（1=Urgent, 2=High, 3=Medium, 4=Low）
# 构造字典赋给 PRIORITY_MAP
PRIORITY_MAP = {"P0": 1, "P1": 2, "P2": 3, "P3": 4}

# Linear 状态名（须与团队工作流一致）
# 初始化 STATUS_IN_PROGRESS
STATUS_IN_PROGRESS = "In Progress"
# 初始化 STATUS_DONE
STATUS_DONE = "Done"


def _load_config() -> dict:
    """加载/读取：Load local hook config from .trellis/hooks.local.json."""
    # task_json_path ← 调用 os.environ.get
    task_json_path = os.environ.get("TASK_JSON_PATH", "")
    # 条件分支：task_json_path
    if task_json_path:
        # 从 task.json 向上查找 .trellis/
        # 读取属性赋给 trellis_dir
        trellis_dir = Path(task_json_path).parent.parent.parent
    else:
        # trellis_dir ← 调用 Path
        trellis_dir = Path(".trellis")

    # 计算后赋给 config_path
    config_path = trellis_dir / "hooks.local.json"
    # try：执行可能失败的逻辑
    try:
        # with 上下文：open(config_path, enc…
        with open(config_path, encoding="utf-8") as f:
            # 返回 json.load 的调用结果
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}  # 返回字典结果


# CONFIG ← 调用 _load_config
CONFIG = _load_config()
# LINEAR_CFG ← 调用 CONFIG.get
LINEAR_CFG = CONFIG.get("linear", {})

# TEAM ← 调用 LINEAR_CFG.get
TEAM = LINEAR_CFG.get("team", "")
# PROJECT ← 调用 LINEAR_CFG.get
PROJECT = LINEAR_CFG.get("project", "")
# ASSIGNEE_MAP ← 调用 LINEAR_CFG.get
ASSIGNEE_MAP = LINEAR_CFG.get("assignees", {})

# ─── 辅助函数 ───


# 定义函数 _read_task
def _read_task() -> tuple[dict, str]:
    # path ← 调用 os.environ.get
    path = os.environ.get("TASK_JSON_PATH", "")
    # 若条件不成立：not path
    if not path:
        # 输出信息
        print("TASK_JSON_PATH not set", file=sys.stderr)
        # 结束进程/解析：sys.exit
        sys.exit(1)
    # with 上下文：open(path, encoding="…
    with open(path, encoding="utf-8") as f:
        return json.load(f), path  # 返回结果


# 定义函数 _write_task
def _write_task(data: dict, path: str) -> None:
    # with 上下文：open(path, "w", encod…
    with open(path, "w", encoding="utf-8") as f:
        # 调用 json.dump
        json.dump(data, f, indent=2, ensure_ascii=False)
        # 输出信息
        f.write("\n")


# 定义函数 _linearis
def _linearis(*args: str) -> dict | None:
    # result ← 调用 subprocess.run
    result = subprocess.run(
        ["linearis", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    # 条件分支：result.returncode != 0
    if result.returncode != 0:
        # 输出信息
        print(f"linearis error: {result.stderr.strip()}", file=sys.stderr)
        # 结束进程/解析：sys.exit
        sys.exit(1)
    # stdout ← 调用 result.stdout.strip
    stdout = result.stdout.strip()
    # 条件分支：stdout
    if stdout:
        # 返回 json.loads 的调用结果
        return json.loads(stdout)
    return None  # 返回 None


# 定义函数 _get_linear_issue
def _get_linear_issue(task: dict) -> str | None:
    # meta ← 调用 task.get
    meta = task.get("meta")
    # 条件分支：isinstance(meta, dict)
    if isinstance(meta, dict):
        # 返回 meta.get 的调用结果
        return meta.get("linear_issue")
    return None  # 返回 None


# ─── 动作 ───


# 定义函数 cmd_create
def cmd_create() -> None:
    # 若条件不成立：not TEAM
    if not TEAM:
        # 输出信息
        print("No linear.team configured in hooks.local.json", file=sys.stderr)
        # 结束进程/解析：sys.exit
        sys.exit(1)

    # task, path ← 调用 _read_task
    task, path = _read_task()

    # 已关联则跳过
    # 条件分支：_get_linear_issue(task)
    if _get_linear_issue(task):
        # 输出信息
        print(f"Already linked: {_get_linear_issue(task)}")
        # 返回（无值）
        return

    # 逻辑运算结果赋给 title
    title = task.get("title") or task.get("name") or "Untitled"
    # 构造列表赋给 args
    args = ["issues", "create", title, "--team", TEAM]

    # 映射优先级
    # priority ← 调用 PRIORITY_MAP.get
    priority = PRIORITY_MAP.get(task.get("priority", ""), 0)
    # 条件分支：priority
    if priority:
        # 扩展列表
        args.extend(["-p", str(priority)])

    # 设置项目
    # 条件分支：PROJECT
    if PROJECT:
        # 扩展列表
        args.extend(["--project", PROJECT])

    # 指派给 Linear 用户
    # assignee ← 调用 task.get
    assignee = task.get("assignee", "")
    # linear_user_id ← 调用 ASSIGNEE_MAP.get
    linear_user_id = ASSIGNEE_MAP.get(assignee)
    # 条件分支：linear_user_id
    if linear_user_id:
        # 扩展列表
        args.extend(["--assignee", linear_user_id])

    # 若有则关联父任务的 Linear issue
    # parent_issue ← 调用 _resolve_parent_linear_issue
    parent_issue = _resolve_parent_linear_issue(task)
    # 条件分支：parent_issue
    if parent_issue:
        # 扩展列表
        args.extend(["--parent-ticket", parent_issue])

    # result ← 调用 _linearis
    result = _linearis(*args)
    # 条件分支：result and "identifier" in result
    if result and "identifier" in result:
        # 若条件不成立：not isinstance(task.get("meta"), dict)
        if not isinstance(task.get("meta"), dict):
            # task["meta"] 初始化为空字典
            task["meta"] = {}
        # 按键/下标取值赋给 task["meta"]["linea…
        task["meta"]["linear_issue"] = result["identifier"]
        # 调用 _write_task
        _write_task(task, path)
        # 输出信息
        print(f"Created Linear issue: {result['identifier']}")


# 定义函数 cmd_start
def cmd_start() -> None:
    # task, _ ← 调用 _read_task
    task, _ = _read_task()
    # issue ← 调用 _get_linear_issue
    issue = _get_linear_issue(task)
    # 若条件不成立：not issue
    if not issue:
        # 返回（无值）
        return
    # 调用 _linearis
    _linearis("issues", "update", issue, "-s", STATUS_IN_PROGRESS)
    # 输出信息
    print(f"Updated {issue} -> {STATUS_IN_PROGRESS}")
    # 调用 cmd_sync
    cmd_sync()


# 定义函数 cmd_archive
def cmd_archive() -> None:
    # task, _ ← 调用 _read_task
    task, _ = _read_task()
    # issue ← 调用 _get_linear_issue
    issue = _get_linear_issue(task)
    # 若条件不成立：not issue
    if not issue:
        # 返回（无值）
        return
    # 调用 _linearis
    _linearis("issues", "update", issue, "-s", STATUS_DONE)
    # 输出信息
    print(f"Updated {issue} -> {STATUS_DONE}")


def cmd_sync() -> None:
    """把 prd.md 内容同步到 Linear issue 描述。"""
    # task, _ ← 调用 _read_task
    task, _ = _read_task()
    # issue ← 调用 _get_linear_issue
    issue = _get_linear_issue(task)
    # 若条件不成立：not issue
    if not issue:
        # 输出信息
        print("No linear_issue in meta, run create first", file=sys.stderr)
        # 结束进程/解析：sys.exit
        sys.exit(1)

    # 在 task.json 旁查找 prd.md
    # task_json_path ← 调用 os.environ.get
    task_json_path = os.environ.get("TASK_JSON_PATH", "")
    # 计算后赋给 prd_path
    prd_path = Path(task_json_path).parent / "prd.md"
    # 若条件不成立：not prd_path.is_file()
    if not prd_path.is_file():
        # 输出信息
        print(f"No prd.md found at {prd_path}", file=sys.stderr)
        # 结束进程/解析：sys.exit
        sys.exit(1)

    # description ← 调用 prd_path.read_text(encoding="…
    description = prd_path.read_text(encoding="utf-8").strip()
    # 调用 _linearis
    _linearis("issues", "update", issue, "-d", description)
    # 输出信息
    print(f"Synced prd.md to {issue} description")


# ─── 父 Issue 解析 ───


def _resolve_parent_linear_issue(task: dict) -> str | None:
    """查找：Find parent task's Linear issue identifier."""
    # parent_name ← 调用 task.get
    parent_name = task.get("parent")
    # 若条件不成立：not parent_name
    if not parent_name:
        return None  # 返回 None

    # task_json_path ← 调用 os.environ.get
    task_json_path = os.environ.get("TASK_JSON_PATH", "")
    # 若条件不成立：not task_json_path
    if not task_json_path:
        return None  # 返回 None

    # 读取属性赋给 current_task_dir
    current_task_dir = Path(task_json_path).parent
    # 读取属性赋给 tasks_dir
    tasks_dir = current_task_dir.parent
    # 计算后赋给 parent_json
    parent_json = tasks_dir / parent_name / "task.json"

    # 条件分支：parent_json.exists()
    if parent_json.exists():
        # try：执行可能失败的逻辑
        try:
            # with 上下文：open(parent_json, enc…
            with open(parent_json, encoding="utf-8") as f:
                # parent_task ← 调用 json.load
                parent_task = json.load(f)
            # 返回 _get_linear_issue 的调用结果
            return _get_linear_issue(parent_task)
        except (json.JSONDecodeError, OSError):
            # 占位（无操作）
            pass
    return None  # 返回 None


# ─── 主流程 ───

# 条件分支：__name__ == "__main__"
# 直接运行本文件时进入入口
if __name__ == "__main__":
    # 按条件取值赋给 action
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    # 构造字典赋给 actions
    actions = {
        "create": cmd_create,
        "start": cmd_start,
        "archive": cmd_archive,
        "sync": cmd_sync,
    }
    # fn ← 调用 actions.get
    fn = actions.get(action)
    # 条件分支：fn
    if fn:
        # 调用 fn
        fn()
    else:
        # 输出信息
        print(f"Unknown action: {action}", file=sys.stderr)
        # 输出信息
        print(f"Valid actions: {', '.join(actions)}", file=sys.stderr)
        # 结束进程/解析：sys.exit
        sys.exit(1)
