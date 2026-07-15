#!/usr/bin/env python3
"""
会话上下文（session context）收集与输出。

组装 git、任务、配置等信息为文本或 JSON，供 Agent 使用。
"""

# 启用延迟注解求值等 future 特性
from __future__ import annotations

# 导入依赖
import json
import os
import re
import subprocess
from pathlib import Path

from .active_task import resolve_context_key
from .config import get_git_packages
from .git import run_git
from .packages_context import get_packages_section
from .tasks import iter_active_tasks, load_task, get_all_statuses, children_progress
from .paths import (
    DIR_SCRIPTS,
    DIR_SPEC,
    DIR_TASKS,
    DIR_WORKFLOW,
    DIR_WORKSPACE,
    count_lines,
    get_active_journal_file,
    get_current_task,
    get_current_task_source,
    get_developer,
    get_repo_root,
    get_tasks_dir,
)


# =============================================================================
# Helpers
# =============================================================================

# 说明：=============================================================================
# 辅助函数
# 初始化 _PACKAGE_NAME
_PACKAGE_NAME = "@mindfoldhq/trellis"
# 初始化 _UPDATE_CHECK_TIMEO…
_UPDATE_CHECK_TIMEOUT_SECONDS = 1.0
# _VERSION_RE ← 调用 re.compile
_VERSION_RE = re.compile(
    r"^\s*(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:-([0-9A-Za-z.-]+))?\s*$"
)
# _VERSION_TOKEN_RE ← 调用 re.compile
_VERSION_TOKEN_RE = re.compile(r"\b\d+(?:\.\d+){1,2}(?:-[0-9A-Za-z.-]+)?\b")
# 构造集合赋给 _POLYREPO_IGNORED_D…
_POLYREPO_IGNORED_DIRS = {
    "node_modules",
    "target",
    "dist",
    "build",
    "out",
    "bin",
    "obj",
    "vendor",
    "coverage",
    "tmp",
    "__pycache__",
}
# 初始化 _POLYREPO_SCAN_MAX_…
_POLYREPO_SCAN_MAX_DEPTH = 2


def _is_git_worktree(path: Path) -> bool:
    """返回：Return True when path is inside a Git worktree."""
    # rc, out, _ ← 调用 run_git
    rc, out, _ = run_git(["rev-parse", "--is-inside-work-tree"], cwd=path)
    # 返回 rc == 0 and out.strip().lower() == …
    return rc == 0 and out.strip().lower() == "true"


def _parse_recent_commits(log_output: str) -> list[dict]:
    """解析：Parse `git log --oneline` output into structured commit entries."""
    # commits 初始化为空列表
    commits = []
    # 遍历：line in log_output.splitlines()
    for line in log_output.splitlines():
        # 若条件不成立：not line.strip()
        if not line.strip():
            continue  # 跳过本轮循环
        # parts ← 调用 line.split
        parts = line.split(" ", 1)
        # 条件分支：len(parts) >= 2
        if len(parts) >= 2:
            # 追加到列表
            commits.append({"hash": parts[0], "message": parts[1]})
        # 条件分支：len(parts) == 1
        elif len(parts) == 1:
            # 追加到列表
            commits.append({"hash": parts[0], "message": ""})
    return commits  # 返回 commits


def _collect_git_repo_info(name: str, rel_path: str, repo_dir: Path) -> dict | None:
    """收集：Collect Git status for one known repository directory."""
    # 否定检查：not (repo_dir / ".git").exists()
    if not (repo_dir / ".git").exists():
        return None  # 返回 None

    # _, branch_out, _ ← 调用 run_git
    _, branch_out, _ = run_git(["branch", "--show-current"], cwd=repo_dir)
    # 逻辑运算结果赋给 branch
    branch = branch_out.strip() or "unknown"

    # _, status_out, _ ← 调用 run_git
    _, status_out, _ = run_git(["status", "--porcelain"], cwd=repo_dir)
    # changes ← 调用 len
    changes = len([l for l in status_out.splitlines() if l.strip()])

    # _, log_out, _ ← 调用 run_git
    _, log_out, _ = run_git(["log", "--oneline", "-5"], cwd=repo_dir)

    # 返回 { "name": name, "path": rel_path, "…
    # 返回 { "isRepo": False, "branch": "", "i…
    # 返回 { "isRepo": True, "branch": branch,…
    return {
        "name": name,
        "path": rel_path,
        "branch": branch,
        "isClean": changes == 0,
        "uncommittedChanges": changes,
        "recentCommits": _parse_recent_commits(log_out),
    }


def _collect_root_git_info(repo_root: Path) -> dict:
    """收集：Collect root Git info without pretending a non-Git root is clean."""
    # 若条件不成立：not _is_git_worktree(repo_root)
    if not _is_git_worktree(repo_root):
        return {
            "isRepo": False,
            "branch": "",
            "isClean": False,
            "uncommittedChanges": 0,
            "recentCommits": [],
        }

    # _, branch_out, _ ← 调用 run_git
    _, branch_out, _ = run_git(["branch", "--show-current"], cwd=repo_root)
    branch = branch_out.strip() or "unknown"

    # _, status_out, _ ← 调用 run_git
    _, status_out, _ = run_git(["status", "--porcelain"], cwd=repo_root)
    # 用推导式生成 status_lines
    status_lines = [line for line in status_out.splitlines() if line.strip()]

    # _, short_out, _ ← 调用 run_git
    _, short_out, _ = run_git(["status", "--short"], cwd=repo_root)

    # _, log_out, _ ← 调用 run_git
    _, log_out, _ = run_git(["log", "--oneline", "-5"], cwd=repo_root)

    return {
        "isRepo": True,
        "branch": branch,
        "isClean": len(status_lines) == 0,
        "uncommittedChanges": len(status_lines),
        "statusShort": short_out.splitlines(),
        "recentCommits": _parse_recent_commits(log_out),
    }


def _discover_child_git_repos(repo_root: Path) -> list[tuple[str, str]]:
    """
检测/发现：Discover child Git repositories using the init-time polyrepo heuristic.
"""
    # 赋值（含类型标注）：found
    found: list[str] = []

    # 定义函数 is_candidate_dir
    def is_candidate_dir(path: Path) -> bool:
        # 读取属性赋给 name
        name = path.name
        # 返回 not name.startswith(".") and name n…
        return not name.startswith(".") and name not in _POLYREPO_IGNORED_DIRS

    # 定义函数 scan
    def scan(rel_dir: Path, depth: int) -> None:
        # 条件分支：depth >= _POLYREPO_SCAN_MAX_DEPTH
        if depth >= _POLYREPO_SCAN_MAX_DEPTH:
            # 返回（无值）
            return
        # 计算后赋给 abs_dir
        abs_dir = repo_root / rel_dir
        # try：执行可能失败的逻辑
        try:
            # children ← 调用 sorted
            children = sorted(abs_dir.iterdir(), key=lambda p: p.name)
        except OSError:
            return

        # 遍历：child in children
        for child in children:
            # 若条件不成立：not child.is_dir() or not is_candidate_dir(child)
            if not child.is_dir() or not is_candidate_dir(child):
                continue

            # 按条件取值赋给 child_rel
            child_rel = (
                rel_dir / child.name if rel_dir != Path(".") else Path(child.name)
            )
            # 条件分支：(child / ".git").exists()
            if (child / ".git").exists():
                # 追加到列表
                found.append(child_rel.as_posix())
                continue
            # 调用 scan
            scan(child_rel, depth + 1)

    # 调用 scan
    scan(Path("."), 0)
    # 条件分支：len(found) < 2
    if len(found) < 2:
        return []  # 返回列表结果
    return [(path.replace("/", "_"), path) for path in sorted(found)]  # 返回结果


def _collect_package_git_info(
    repo_root: Path,
    discover_unconfigured: bool = False,
) -> list[dict]:
    """
收集：Collect Git status for independent package repositories.

Packages marked with ``git: true`` in config.yaml are authoritative.
When the Trellis root is not a Git repo and no configured package repos are
available, optionally fall back to the bounded polyrepo child scan.


返回:
    List of dicts with keys: name, path, branch, isClean,
    uncommittedChanges, recentCommits.
    Empty list if no git-repo packages are configured.
"""
    # git_pkgs ← 调用 get_git_packages
    git_pkgs = get_git_packages(repo_root)
    # result 初始化为空列表
    result = []
    # 遍历：pkg_name, pkg_path in git_pkgs.items()
    for pkg_name, pkg_path in git_pkgs.items():
        # 计算后赋给 pkg_dir
        pkg_dir = repo_root / pkg_path
        # info ← 调用 _collect_git_repo_info
        info = _collect_git_repo_info(pkg_name, pkg_path, pkg_dir)
        # 若已有值：info is not None
        if info is not None:
            # 追加到列表
            result.append(info)

    # 条件分支：result or not discover_unconfigured
    if result or not discover_unconfigured:
        return result  # 返回 result

    # discovered 初始化为空列表
    discovered = []
    # 遍历：pkg_name, pkg_path in _discover_child_git_repos(re
    for pkg_name, pkg_path in _discover_child_git_repos(repo_root):
        # info ← 调用 _collect_git_repo_info
        info = _collect_git_repo_info(pkg_name, pkg_path, repo_root / pkg_path)
        if info is not None:
            # 追加到列表
            discovered.append(info)
    return discovered  # 返回 discovered


def _append_root_git_context(lines: list[str], root_git_info: dict) -> None:
    """添加：Append root Git status without misleading non-Git roots."""
    # 追加到列表
    lines.append("## GIT STATUS")
    # 若条件不成立：not root_git_info["isRepo"]
    if not root_git_info["isRepo"]:
        # 追加到列表
        lines.append("Root is not a Git repository.")
        # 追加到列表
        lines.append("Run Git commands from the package repository paths listed below.")
    else:
        # 追加到列表
        lines.append(f"Branch: {root_git_info['branch']}")
        # 条件分支：root_git_info["isClean"]
        if root_git_info["isClean"]:
            # 追加到列表
            lines.append("Working directory: Clean")
        else:
            # 追加到列表
            lines.append(
                f"Working directory: {root_git_info['uncommittedChanges']} "
                "uncommitted change(s)"
            )
            # 追加到列表
            lines.append("")
            # 追加到列表
            lines.append("Changes:")
            # 遍历：line in root_git_info.get("statusShort", [])[:10]
            for line in root_git_info.get("statusShort", [])[:10]:
                # 追加到列表
                lines.append(line)
    lines.append("")

    # 追加到列表
    lines.append("## RECENT COMMITS")
    if not root_git_info["isRepo"]:
        lines.append(
            "Root has no Git commit history because it is not a Git repository."
        )
    # 条件分支：root_git_info["recentCommits"]
    elif root_git_info["recentCommits"]:
        # 遍历：commit in root_git_info["recentCommits"]
        for commit in root_git_info["recentCommits"]:
            # 追加到列表
            lines.append(f"{commit['hash']} {commit['message']}")
    else:
        # 追加到列表
        lines.append("(no commits)")
    lines.append("")


def _append_package_git_context(lines: list[str], package_git_info: list[dict]) -> None:
    """添加：Append Git status and recent commits for package repositories."""
    # 遍历：pkg in package_git_info
    for pkg in package_git_info:
        # 追加到列表
        lines.append(f"## GIT STATUS ({pkg['name']}: {pkg['path']})")
        # 追加到列表
        lines.append(f"Branch: {pkg['branch']}")
        # 条件分支：pkg["isClean"]
        if pkg["isClean"]:
            lines.append("Working directory: Clean")
        else:
            lines.append(
                f"Working directory: {pkg['uncommittedChanges']} uncommitted change(s)"
            )
        lines.append("")
        # 追加到列表
        lines.append(f"## RECENT COMMITS ({pkg['name']}: {pkg['path']})")
        # 条件分支：pkg["recentCommits"]
        if pkg["recentCommits"]:
            # 遍历：commit in pkg["recentCommits"]
            for commit in pkg["recentCommits"]:
                lines.append(f"{commit['hash']} {commit['message']}")
        else:
            lines.append("(no commits)")
        lines.append("")


# 定义函数 _read_project_version
def _read_project_version(repo_root: Path) -> str | None:
    try:
        # version ← 调用 (repo_root / DIR_WORKFLOW / "…
        version = (repo_root / DIR_WORKFLOW / ".version").read_text(
            encoding="utf-8"
        ).strip()
    except OSError:
        return None
    # 返回 version or None
    return version or None


# 定义函数 _fetch_trellis_version_output
def _fetch_trellis_version_output() -> str | None:
    try:
        # result ← 调用 subprocess.run
        result = subprocess.run(
            ["trellis", "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=_UPDATE_CHECK_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError, TimeoutError):
        return None

    # 条件分支：result.returncode != 0
    if result.returncode != 0:
        return None
    # output ← 调用 f"{result.stdout}\n{result.st…
    output = f"{result.stdout}\n{result.stderr}".strip()
    # 返回 output or None
    return output or None


# 定义函数 _extract_available_update_version
def _extract_available_update_version(output: str) -> str | None:
    # update_match ← 调用 re.search
    update_match = re.search(
        r"Trellis update available:\s*"
        r"(?P<current>\S+)\s*(?:→|->)\s*(?P<latest>\S+)",
        output,
    )
    # 条件分支：update_match
    if update_match:
        # 返回 update_match.group("latest"… 的调用结果
        return update_match.group("latest").strip()
    # candidates ← 调用 _VERSION_TOKEN_RE.findall
    candidates = _VERSION_TOKEN_RE.findall(output)
    # 按条件返回不同值
    return candidates[-1] if candidates else None


# 定义函数 _resolve_available_update_version
def _resolve_available_update_version() -> str | None:
    # output ← 调用 _fetch_trellis_version_output
    output = _fetch_trellis_version_output()
    # 若条件不成立：not output
    if not output:
        return None
    # 返回 _extract_available_update_v… 的调用结果
    return _extract_available_update_version(output)


# 定义函数 _parse_version
def _parse_version(version: str) -> tuple[tuple[int, int, int], tuple[str, ...] | None] | None:
    # match ← 调用 _VERSION_RE.match
    match = _VERSION_RE.match(version)
    # 若条件不成立：not match
    if not match:
        return None
    # major, minor, patch… ← 调用 match.groups
    major, minor, patch, prerelease = match.groups()
    # 打包元组赋给 numbers
    numbers = (int(major), int(minor or "0"), int(patch or "0"))
    # 按条件取值赋给 prerelease_parts
    prerelease_parts = tuple(prerelease.split(".")) if prerelease else None
    return numbers, prerelease_parts  # 返回结果


# 定义函数 _compare_prerelease
def _compare_prerelease(
    left: tuple[str, ...] | None,
    right: tuple[str, ...] | None,
) -> int:
    # 若为 None：left is None and right is None
    if left is None and right is None:
        return 0  # 返回 0
    # 若为 None：left is None
    if left is None:
        # 返回常量 1
        return 1
    # 若为 None：right is None
    if right is None:
        return -1  # 返回计算结果

    # 遍历：left_part, right_part in zip(left, right)
    for left_part, right_part in zip(left, right):
        # 条件分支：left_part == right_part
        if left_part == right_part:
            continue
        # left_numeric ← 调用 left_part.isdigit
        left_numeric = left_part.isdigit()
        # right_numeric ← 调用 right_part.isdigit
        right_numeric = right_part.isdigit()
        # 条件分支：left_numeric and right_numeric
        if left_numeric and right_numeric:
            # left_int ← 调用 int
            left_int = int(left_part)
            # right_int ← 调用 int
            right_int = int(right_part)
            # 返回 (left_int > right_int) - (left_int …
            return (left_int > right_int) - (left_int < right_int)
        # 条件分支：left_numeric
        if left_numeric:
            return -1
        # 条件分支：right_numeric
        if right_numeric:
            return 1
        # 返回 (left_part > right_part) - (left_pa…
        return (left_part > right_part) - (left_part < right_part)

    # 返回 (len(left) > len(right)) - (len(lef…
    return (len(left) > len(right)) - (len(left) < len(right))


# 定义函数 _compare_versions
def _compare_versions(left: str, right: str) -> int | None:
    # parsed_left ← 调用 _parse_version
    parsed_left = _parse_version(left)
    # parsed_right ← 调用 _parse_version
    parsed_right = _parse_version(right)
    # 若为 None：parsed_left is None or parsed_right is No…
    if parsed_left is None or parsed_right is None:
        return None

    left_numbers, left_prerelease = parsed_left  # 元组解包 ← parsed_left
    right_numbers, right_prerelease = parsed_right  # 元组解包 ← parsed_right
    # 条件分支：left_numbers != right_numbers
    if left_numbers != right_numbers:
        # 返回 (left_numbers > right_numbers) - (l…
        return (left_numbers > right_numbers) - (left_numbers < right_numbers)
    # 返回 _compare_prerelease 的调用结果
    return _compare_prerelease(left_prerelease, right_prerelease)


# 定义函数 _update_marker_path
def _update_marker_path(repo_root: Path) -> Path:
    # context_key ← 调用 resolve_context_key
    context_key = resolve_context_key()
    # 若条件不成立：not context_key
    if not context_key:
        # terminal_key ← 调用 os.environ.get("TERM_SESSION_…
        terminal_key = os.environ.get("TERM_SESSION_ID", "").strip()
        # 逻辑运算结果赋给 context_key
        context_key = terminal_key or f"ppid-{os.getppid()}"
    # safe_key ← 调用 re.sub(r"[^A-Za-z0-9._-]+", "…
    safe_key = re.sub(r"[^A-Za-z0-9._-]+", "_", context_key).strip("._-")
    # 若条件不成立：not safe_key
    if not safe_key:
        # 初始化 safe_key
        safe_key = "session"
    # 返回 repo_root / DIR_WORKFLOW / ".runtim…
    return (  # 返回格式化字符串
        repo_root
        / DIR_WORKFLOW
        / ".runtime"
        / f"update-check-{safe_key[:160]}.marker"
    )


# 定义函数 _mark_update_check_attempted
def _mark_update_check_attempted(repo_root: Path) -> bool:
    # marker_path ← 调用 _update_marker_path
    marker_path = _update_marker_path(repo_root)
    # 条件分支：marker_path.exists()
    if marker_path.exists():
        return False  # 返回 False
    try:
        # 创建目录
        marker_path.parent.mkdir(parents=True, exist_ok=True)
        # 写入文件
        marker_path.write_text("checked\n", encoding="utf-8")
    except OSError:
        # 占位（无操作）
        pass
    return True  # 返回 True


# 定义函数 _get_update_hint
def _get_update_hint(repo_root: Path) -> str | None:
    marker_path = _update_marker_path(repo_root)
    if marker_path.exists():
        return None

    # current_version ← 调用 _read_project_version
    current_version = _read_project_version(repo_root)
    # 若条件不成立：not current_version
    if not current_version:
        return None

    # latest_version ← 调用 _resolve_available_update_ver…
    latest_version = _resolve_available_update_version()
    # 若条件不成立：not latest_version
    if not latest_version:
        return None

    # 调用 _mark_update_check_attempted
    _mark_update_check_attempted(repo_root)
    # comparison ← 调用 _compare_versions
    comparison = _compare_versions(current_version, latest_version)
    # 若为 None：comparison is None or comparison >= 0
    if comparison is None or comparison >= 0:
        return None

    return (
        f"Trellis update available: {current_version} -> {latest_version}, "
        "run trellis update"
    )


# =============================================================================
# JSON Output
# =============================================================================

# 说明：=============================================================================
# JSON 输出
def get_context_json(repo_root: Path | None = None) -> dict:
    """
获取：Get context as a dictionary.


参数:
    repo_root: Repository root path. Defaults to auto-detected.


返回:
    Context dictionary.
"""
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # developer ← 调用 get_developer
    developer = get_developer(repo_root)
    # tasks_dir ← 调用 get_tasks_dir
    tasks_dir = get_tasks_dir(repo_root)
    # journal_file ← 调用 get_active_journal_file
    journal_file = get_active_journal_file(repo_root)

    # 初始化 journal_lines
    journal_lines = 0
    # 初始化 journal_relative
    journal_relative = ""
    # 条件分支：journal_file and developer
    if journal_file and developer:
        # journal_lines ← 调用 count_lines
        journal_lines = count_lines(journal_file)
        # 拼出字符串赋给 journal_relative
        journal_relative = (
            f"{DIR_WORKFLOW}/{DIR_WORKSPACE}/{developer}/{journal_file.name}"
        )

    # root_git_info ← 调用 _collect_root_git_info
    root_git_info = _collect_root_git_info(repo_root)

    # Tasks
    # 任务
    # 用推导式生成 tasks
    tasks = [
        {
            "dir": t.dir_name,
            "name": t.name,
            "status": t.status,
            "children": list(t.children),
            "parent": t.parent,
        }
        for t in iter_active_tasks(tasks_dir)
    ]

    # Package git repos (independent sub-repositories)
    # 包级 git 仓库（独立子仓库）
    # pkg_git_info ← 调用 _collect_package_git_info
    # 包级 git 仓库
    pkg_git_info = _collect_package_git_info(
        repo_root,
        discover_unconfigured=not root_git_info["isRepo"],
    )

    # 构造字典赋给 result
    result = {
        "developer": developer or "",
        "git": {
            "isRepo": root_git_info["isRepo"],
            "branch": root_git_info["branch"],
            "isClean": root_git_info["isClean"],
            "uncommittedChanges": root_git_info["uncommittedChanges"],
            "recentCommits": root_git_info["recentCommits"],
        },
        "tasks": {
            "active": tasks,
            "directory": f"{DIR_WORKFLOW}/{DIR_TASKS}",
        },
        "journal": {
            "file": journal_relative,
            "lines": journal_lines,
            "nearLimit": journal_lines > 1800,
        },
    }

    # 条件分支：pkg_git_info
    if pkg_git_info:
        result["packageGit"] = pkg_git_info  # 下标项 ← pkg_git_info

    return result


def output_json(repo_root: Path | None = None) -> None:
    """
打印/输出：Output context in JSON format.


参数:
    repo_root: Repository root path. Defaults to auto-detected.
"""
    # context ← 调用 get_context_json
    context = get_context_json(repo_root)
    # 输出信息
    print(json.dumps(context, indent=2, ensure_ascii=False))


# =============================================================================
# Text Output
# =============================================================================

# 说明：=============================================================================
# 文本输出
def get_context_text(repo_root: Path | None = None) -> str:
    """
获取：Get context as formatted text.


参数:
    repo_root: Repository root path. Defaults to auto-detected.


返回:
    Formatted text output.
"""
    if repo_root is None:
        repo_root = get_repo_root()

    # lines 初始化为空列表
    lines = []
    # 追加到列表
    lines.append("========================================")
    # 追加到列表
    lines.append("SESSION CONTEXT")
    lines.append("========================================")
    lines.append("")

    developer = get_developer(repo_root)

    # Developer section
    # 开发者分区
    # 追加到列表
    lines.append("## DEVELOPER")
    # 若条件不成立：not developer
    if not developer:
        lines.append(
            f"ERROR: Not initialized. Run: python3 ./{DIR_WORKFLOW}/{DIR_SCRIPTS}/init_developer.py <name>"
        )
        return "\n".join(lines)  # 返回 join(...) 的结果

    # 追加到列表
    lines.append(f"Name: {developer}")
    lines.append("")

    root_git_info = _collect_root_git_info(repo_root)
    # 调用 _append_root_git_context
    _append_root_git_context(lines, root_git_info)

    # Package git repos — independent sub-repositories
    # 包级 git 仓库——独立子仓库
    # 调用 _append_package_git_context
    _append_package_git_context(
        lines,
        _collect_package_git_info(
            repo_root,
            discover_unconfigured=not root_git_info["isRepo"],
        ),
    )

    # Current task
    # 当前任务
    # 追加到列表
    lines.append("## CURRENT TASK")
    # current_task ← 调用 get_current_task
    current_task = get_current_task(repo_root)
    # 条件分支：current_task
    if current_task:
        # 计算后赋给 current_task_dir
        current_task_dir = repo_root / current_task
        # source_type, contex… ← 调用 get_current_task_source
        source_type, context_key, _ = get_current_task_source(repo_root)
        # 追加到列表
        lines.append(f"Path: {current_task}")
        lines.append(
            f"Source: {source_type}" + (f":{context_key}" if context_key else "")
        )

        # ct ← 调用 load_task
        ct = load_task(current_task_dir)
        # 条件分支：ct
        if ct:
            # 追加到列表
            lines.append(f"Name: {ct.name}")
            # 追加到列表
            lines.append(f"Status: {ct.status}")
            # 追加到列表
            lines.append(f"Created: {ct.raw.get('createdAt', 'unknown')}")
            # 条件分支：ct.description
            if ct.description:
                # 追加到列表
                lines.append(f"Description: {ct.description}")

        # Check for prd.md
        # 检查 prd.md
        # 计算后赋给 prd_file
        prd_file = current_task_dir / "prd.md"
        # 条件分支：prd_file.is_file()
        if prd_file.is_file():
            lines.append("")
            # 追加到列表
            lines.append("[!] This task has prd.md - read it for task details")
    else:
        # 追加到列表
        lines.append("(none)")
    lines.append("")

    # Active tasks
    # 活动任务
    # 追加到列表
    lines.append("## ACTIVE TASKS")
    tasks_dir = get_tasks_dir(repo_root)
    # 初始化 task_count
    task_count = 0

    # Collect all task data for hierarchy display
    # 收集全部任务数据用于层级展示
    # 用推导式生成 all_tasks
    all_tasks = {t.dir_name: t for t in iter_active_tasks(tasks_dir)}
    # 用推导式生成 all_statuses
    all_statuses = {name: t.status for name, t in all_tasks.items()}

    # 定义函数 _print_task_tree
    def _print_task_tree(name: str, indent: int = 0) -> None:
        # 声明非局部变量：task_count
        nonlocal task_count
        # 按键/下标取值赋给 t
        t = all_tasks[name]
        # progress ← 调用 children_progress
        progress = children_progress(t.children, all_statuses)
        # 计算后赋给 prefix
        prefix = "  " * indent
        # 追加到列表
        lines.append(f"{prefix}- {name}/ ({t.status}){progress} @{t.assignee or '-'}")
        # 就地更新 task_count
        task_count += 1
        # 遍历：child in t.children
        for child in t.children:
            # 条件分支：child in all_tasks
            if child in all_tasks:
                # 调用 _print_task_tree
                _print_task_tree(child, indent + 1)

    # 遍历：dir_name in sorted(all_tasks.keys())
    for dir_name in sorted(all_tasks.keys()):
        # 若条件不成立：not all_tasks[dir_name].parent
        if not all_tasks[dir_name].parent:
            # 调用 _print_task_tree
            _print_task_tree(dir_name)

    # 条件分支：task_count == 0
    if task_count == 0:
        # 追加到列表
        lines.append("(no active tasks)")
    # 追加到列表
    lines.append(f"Total: {task_count} active task(s)")
    lines.append("")

    # My tasks
    # 我的任务
    # 追加到列表
    lines.append("## MY TASKS (Assigned to me)")
    # 初始化 my_task_count
    my_task_count = 0

    # 遍历：t in all_tasks.values()
    for t in all_tasks.values():
        # 条件分支：t.assignee == developer and t.status != "…
        if t.assignee == developer and t.status != "done":
            progress = children_progress(t.children, all_statuses)
            # 追加到列表
            lines.append(f"- [{t.priority}] {t.title} ({t.status}){progress}")
            # 就地更新 my_task_count
            my_task_count += 1

    # 条件分支：my_task_count == 0
    if my_task_count == 0:
        # 追加到列表
        lines.append("(no tasks assigned to you)")
    lines.append("")

    # Journal file
    # Journal 文件
    # 追加到列表
    lines.append("## JOURNAL FILE")
    journal_file = get_active_journal_file(repo_root)
    # 条件分支：journal_file
    if journal_file:
        journal_lines = count_lines(journal_file)
        # 拼出字符串赋给 relative
        relative = f"{DIR_WORKFLOW}/{DIR_WORKSPACE}/{developer}/{journal_file.name}"
        # 追加到列表
        lines.append(f"Active file: {relative}")
        # 追加到列表
        lines.append(f"Line count: {journal_lines} / 2000")
        # 条件分支：journal_lines > 1800
        if journal_lines > 1800:
            # 追加到列表
            lines.append("[!] WARNING: Approaching 2000 line limit!")
    else:
        # 追加到列表
        lines.append("No journal file found")
    lines.append("")

    # Packages
    # 包
    # packages_text ← 调用 get_packages_section
    packages_text = get_packages_section(repo_root)
    # 条件分支：packages_text
    if packages_text:
        # 追加到列表
        lines.append(packages_text)
        lines.append("")

    # Paths
    # 路径
    # 追加到列表
    lines.append("## PATHS")
    # 追加到列表
    lines.append(f"Workspace: {DIR_WORKFLOW}/{DIR_WORKSPACE}/{developer}/")
    # 追加到列表
    lines.append(f"Tasks: {DIR_WORKFLOW}/{DIR_TASKS}/")
    # 追加到列表
    lines.append(f"Spec: {DIR_WORKFLOW}/{DIR_SPEC}/")
    lines.append("")

    lines.append("========================================")

    return "\n".join(lines)


# =============================================================================
# Record Mode
# =============================================================================

# 说明：=============================================================================
# 记录模式
def get_context_record_json(repo_root: Path | None = None) -> dict:
    """
获取：Get record-mode context as a dictionary.

Focused on: my active tasks, git status, current task.
"""
    if repo_root is None:
        repo_root = get_repo_root()

    developer = get_developer(repo_root)
    tasks_dir = get_tasks_dir(repo_root)

    root_git_info = _collect_root_git_info(repo_root)

    # My tasks (single pass — collect statuses and filter by assignee)
    # 我的任务（单次遍历——收集状态并按指派人过滤）
    # all_tasks_list ← 调用 list
    all_tasks_list = list(iter_active_tasks(tasks_dir))
    # 用推导式生成 all_statuses
    all_statuses = {t.dir_name: t.status for t in all_tasks_list}

    # my_tasks 初始化为空列表
    my_tasks = []
    # 遍历：t in all_tasks_list
    for t in all_tasks_list:
        # 条件分支：t.assignee == developer
        if t.assignee == developer:
            # done ← 调用 sum
            done = sum(
                1 for c in t.children
                if all_statuses.get(c) in ("completed", "done")
            )
            # 追加到列表
            my_tasks.append({
                "dir": t.dir_name,
                "title": t.title,
                "status": t.status,
                "priority": t.priority,
                "children": list(t.children),
                "childrenDone": done,
                "parent": t.parent,
                "meta": t.meta,
            })

    # Current task
    # 当前任务
    # 初始化 current_task_info
    current_task_info = None
    current_task = get_current_task(repo_root)
    if current_task:
        source_type, context_key, _ = get_current_task_source(repo_root)
        # ct ← 调用 load_task
        ct = load_task(repo_root / current_task)
        if ct:
            # 构造字典赋给 current_task_info
            current_task_info = {
                "path": current_task,
                "name": ct.name,
                "status": ct.status,
                "source": source_type,
                "contextKey": context_key,
            }

    # Package git repos
    pkg_git_info = _collect_package_git_info(
        repo_root,
        discover_unconfigured=not root_git_info["isRepo"],
    )

    result = {
        "developer": developer or "",
        "git": {
            "isRepo": root_git_info["isRepo"],
            "branch": root_git_info["branch"],
            "isClean": root_git_info["isClean"],
            "uncommittedChanges": root_git_info["uncommittedChanges"],
            "recentCommits": root_git_info["recentCommits"],
        },
        "myTasks": my_tasks,
        "currentTask": current_task_info,
    }

    if pkg_git_info:
        result["packageGit"] = pkg_git_info

    return result


def get_context_text_record(repo_root: Path | None = None) -> str:
    """
获取：Get context as formatted text for record-session mode.

Focused output: MY ACTIVE TASKS first (with [!!!] emphasis),
then GIT STATUS, RECENT COMMITS, CURRENT TASK.
"""
    if repo_root is None:
        repo_root = get_repo_root()

    # 赋值（含类型标注）：lines
    lines: list[str] = []
    lines.append("========================================")
    # 追加到列表
    lines.append("SESSION CONTEXT (RECORD MODE)")
    lines.append("========================================")
    lines.append("")

    developer = get_developer(repo_root)
    if not developer:
        lines.append(
            f"ERROR: Not initialized. Run: python3 ./{DIR_WORKFLOW}/{DIR_SCRIPTS}/init_developer.py <name>"
        )
        return "\n".join(lines)

    # MY ACTIVE TASKS — first and prominent
    # 我的活动任务——优先突出显示
    # 追加到列表
    lines.append(f"## [!!!] MY ACTIVE TASKS (Assigned to {developer})")
    # 追加到列表
    lines.append("[!] Review whether any should be archived before recording this session.")
    lines.append("")

    tasks_dir = get_tasks_dir(repo_root)
    my_task_count = 0

    # Single pass — collect all tasks and filter by assignee
    # 单次遍历——收集全部任务并按指派人过滤
    # all_statuses ← 调用 get_all_statuses
    all_statuses = get_all_statuses(tasks_dir)

    # 遍历：t in iter_active_tasks(tasks_dir)
    for t in iter_active_tasks(tasks_dir):
        if t.assignee == developer:
            progress = children_progress(t.children, all_statuses)
            # 追加到列表
            lines.append(f"- [{t.priority}] {t.title} ({t.status}){progress} — {t.dir_name}")
            my_task_count += 1

    if my_task_count == 0:
        # 追加到列表
        lines.append("(no active tasks assigned to you)")
    lines.append("")

    root_git_info = _collect_root_git_info(repo_root)
    _append_root_git_context(lines, root_git_info)

    # Package git repos — independent sub-repositories
    _append_package_git_context(
        lines,
        _collect_package_git_info(
            repo_root,
            discover_unconfigured=not root_git_info["isRepo"],
        ),
    )

    # CURRENT TASK
    lines.append("## CURRENT TASK")
    current_task = get_current_task(repo_root)
    if current_task:
        source_type, context_key, _ = get_current_task_source(repo_root)
        lines.append(f"Path: {current_task}")
        lines.append(
            f"Source: {source_type}" + (f":{context_key}" if context_key else "")
        )
        ct = load_task(repo_root / current_task)
        if ct:
            lines.append(f"Name: {ct.name}")
            lines.append(f"Status: {ct.status}")
    else:
        lines.append("(none)")
    lines.append("")

    lines.append("========================================")

    return "\n".join(lines)


def output_text(repo_root: Path | None = None) -> None:
    """
打印/输出：Output context in text format.


参数:
    repo_root: Repository root path. Defaults to auto-detected.
"""
    if repo_root is None:
        repo_root = get_repo_root()
    # update_hint ← 调用 _get_update_hint
    update_hint = _get_update_hint(repo_root)
    # 条件分支：update_hint
    if update_hint:
        # 输出信息
        print(update_hint)
        # 输出信息
        print("")
    # 输出信息
    print(get_context_text(repo_root))
