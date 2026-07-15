#!/usr/bin/env python3
"""
Trellis 工作流公共路径工具。

提供:
    get_repo_root           - 获取仓库根目录
    get_developer           - 获取开发者名称
    get_workspace_dir       - 获取开发者 workspace 目录
    get_tasks_dir           - 获取 tasks 目录
    get_active_journal_file - 获取当前 journal 文件
"""

# 启用延迟注解求值等 future 特性
from __future__ import annotations

# 导入依赖
import re
from datetime import datetime
from pathlib import Path


# 说明：=============================================================================
# 路径常量（改目录名只改此处）
# 说明：=============================================================================

# 目录名
# 工作流根目录名（.trellis）
DIR_WORKFLOW = ".trellis"
# 开发者 workspace 目录名
DIR_WORKSPACE = "workspace"
# 任务目录名
DIR_TASKS = "tasks"
# 归档目录名
DIR_ARCHIVE = "archive"
# 规格目录名
DIR_SPEC = "spec"
# 脚本目录名
DIR_SCRIPTS = "scripts"

# 文件名
# 开发者标记文件名
FILE_DEVELOPER = ".developer"
# 当前任务指针文件名（兼容）
FILE_CURRENT_TASK = ".current-task"
# 任务元数据文件名
FILE_TASK_JSON = "task.json"
# journal 文件名前缀
FILE_JOURNAL_PREFIX = "journal-"


# 说明：=============================================================================
# 仓库根目录
# 说明：=============================================================================

def get_repo_root(start_path: Path | None = None) -> Path:
    """
    查找：Find the nearest directory containing .trellis/ folder.

    This handles nested git repos correctly (e.g., test project inside another repo).


    参数:
        start_path: Starting directory to search from. Defaults to current directory.


    返回:
        Path to repository root, or current directory if no .trellis/ found.
    """
    # current ← 调用 (start_path or Path.cwd()).re…
    current = (start_path or Path.cwd()).resolve()

    # while 循环：current != current.parent
    while current != current.parent:
        # 条件分支：(current / DIR_WORKFLOW).is_dir()
        if (current / DIR_WORKFLOW).is_dir():
            return current  # 返回 current
        # 读取属性赋给 current
        current = current.parent

    # 找不到 .trellis/ 时回退到当前目录
    # 返回 Path.cwd().resolve 的调用结果
    return Path.cwd().resolve()


# 说明：=============================================================================
# 开发者
# 说明：=============================================================================

def get_developer(repo_root: Path | None = None) -> str | None:
    """
    获取：Get developer name from .developer file.


    参数:
        repo_root: Repository root path. Defaults to auto-detected.


    返回:
        Developer name or None if not initialized.
    """
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # 计算后赋给 dev_file
    dev_file = repo_root / DIR_WORKFLOW / FILE_DEVELOPER

    # 若条件不成立：not dev_file.is_file()
    if not dev_file.is_file():
        return None  # 返回 None

    # try：执行可能失败的逻辑
    try:
        # content ← 调用 dev_file.read_text
        content = dev_file.read_text(encoding="utf-8")
        # 遍历：line in content.splitlines()
        for line in content.splitlines():
            # 条件分支：line.startswith("name=")
            if line.startswith("name="):
                # 返回 line.split("=", 1)[1].strip 的调用结果
                return line.split("=", 1)[1].strip()
    except (OSError, IOError):
        # 占位（无操作）
        pass

    return None  # 返回 None


def check_developer(repo_root: Path | None = None) -> bool:
    """
    检查/校验：Check if developer is initialized.


    参数:
        repo_root: Repository root path. Defaults to auto-detected.


    返回:
        True if developer is initialized.
    """
    # 返回 get_developer(repo_root) is not None
    return get_developer(repo_root) is not None


# 说明：=============================================================================
# 任务目录
# 说明：=============================================================================

def get_tasks_dir(repo_root: Path | None = None) -> Path:
    """
    获取：Get tasks directory path.


    参数:
        repo_root: Repository root path. Defaults to auto-detected.


    返回:
        Path to tasks directory.
    """
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()
    # 返回 repo_root / DIR_WORKFLOW / DIR_TASKS
    return repo_root / DIR_WORKFLOW / DIR_TASKS


# 说明：=============================================================================
# 工作区目录
# 说明：=============================================================================

def get_workspace_dir(repo_root: Path | None = None) -> Path | None:
    """
    获取：Get developer workspace directory.


    参数:
        repo_root: Repository root path. Defaults to auto-detected.


    返回:
        Path to workspace directory or None if developer not set.
    """
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # developer ← 调用 get_developer
    developer = get_developer(repo_root)
    # 条件分支：developer
    if developer:
        # 返回 repo_root / DIR_WORKFLOW / DIR_WORK…
        return repo_root / DIR_WORKFLOW / DIR_WORKSPACE / developer
    return None  # 返回 None


# 说明：=============================================================================
# 日志（journal）文件
# 说明：=============================================================================

def get_active_journal_file(repo_root: Path | None = None) -> Path | None:
    """
    获取：Get the current active journal file.


    参数:
        repo_root: Repository root path. Defaults to auto-detected.


    返回:
        Path to active journal file or None if not found.
    """
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # workspace_dir ← 调用 get_workspace_dir
    workspace_dir = get_workspace_dir(repo_root)
    # 若为 None：workspace_dir is None or not workspace_di…
    if workspace_dir is None or not workspace_dir.is_dir():
        return None  # 返回 None

    # latest 置为 None（带类型）
    latest: Path | None = None
    # 初始化 highest
    highest = 0

    # 遍历：f in workspace_dir.glob(f"{FILE_JOURNAL_PREFIX}*.m
    for f in workspace_dir.glob(f"{FILE_JOURNAL_PREFIX}*.md"):
        # 若条件不成立：not f.is_file()
        if not f.is_file():
            continue  # 跳过本轮循环

        # 从文件名提取编号
        # 读取属性赋给 name
        name = f.stem  # 例如 "journal-1"
        # match ← 调用 re.search
        match = re.search(r"(\d+)$", name)
        # 条件分支：match
        if match:
            # num ← 调用 int
            num = int(match.group(1))
            # 条件分支：num > highest
            if num > highest:
                highest = num  # 将 num 赋给 highest
                latest = f  # 将 f 赋给 latest

    return latest  # 返回 latest


def count_lines(file_path: Path) -> int:
    """
    count_lines：Count lines in a file.


    参数:
        file_path: Path to file.


    返回:
        Number of lines, or 0 if file doesn't exist.
    """
    # 若条件不成立：not file_path.is_file()
    if not file_path.is_file():
        return 0  # 返回 0

    # try：执行可能失败的逻辑
    try:
        # 返回 len 的调用结果
        return len(file_path.read_text(encoding="utf-8").splitlines())
    except (OSError, IOError):
        return 0  # 返回 0


# 说明：=============================================================================
# 当前任务管理
# 说明：=============================================================================

def normalize_task_ref(task_ref: str) -> str:
    """
    规范化：Normalize a task ref for stable runtime storage.

    Stored refs should prefer repo-relative POSIX paths like
    `.trellis/tasks/03-27-my-task`, even on Windows. Absolute paths are preserved
    unless they can later be converted back to repo-relative form by callers.
    """
    # normalized ← 调用 task_ref.strip
    normalized = task_ref.strip()
    # 若条件不成立：not normalized
    if not normalized:
        return ""  # 返回空字符串

    # path_obj ← 调用 Path
    path_obj = Path(normalized)
    # 条件分支：path_obj.is_absolute()
    if path_obj.is_absolute():
        # 返回 str 的调用结果
        return str(path_obj)

    # normalized ← 调用 normalized.replace
    normalized = normalized.replace("\\", "/")
    # while 循环：normalized.startswith("./")
    while normalized.startswith("./"):
        # 按键/下标取值赋给 normalized
        normalized = normalized[2:]

    # 条件分支：normalized.startswith(f"{DIR_TASKS}/")
    if normalized.startswith(f"{DIR_TASKS}/"):
        return f"{DIR_WORKFLOW}/{normalized}"  # 返回格式化字符串

    return normalized  # 返回 normalized


def resolve_task_ref(task_ref: str, repo_root: Path | None = None) -> Path | None:
    """解析/解析出：Resolve a task ref to an absolute task directory path."""
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # normalized ← 调用 normalize_task_ref
    normalized = normalize_task_ref(task_ref)
    # 若条件不成立：not normalized
    if not normalized:
        return None  # 返回 None

    # path_obj ← 调用 Path
    path_obj = Path(normalized)
    # 条件分支：path_obj.is_absolute()
    if path_obj.is_absolute():
        return path_obj  # 返回 path_obj

    # 条件分支：normalized.startswith(f"{DIR_WORKFLOW}/")
    if normalized.startswith(f"{DIR_WORKFLOW}/"):
        # 返回 repo_root / path_obj
        return repo_root / path_obj

    # 返回 repo_root / DIR_WORKFLOW / DIR_TASK…
    return repo_root / DIR_WORKFLOW / DIR_TASKS / path_obj


def get_current_task(
    repo_root: Path | None = None,
    platform_input: dict | None = None,
    platform: str | None = None,
) -> str | None:
    """
    获取：Get current task directory path (relative to repo_root).


    参数:
        repo_root: Repository root path. Defaults to auto-detected.


    返回:
        Relative path to current task directory or None.
    """
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # 局部导入 active_task
    from .active_task import resolve_active_task

    # 返回属性 resolve_active_task(repo_root…
    return resolve_active_task(repo_root, platform_input, platform).task_path


def get_current_task_abs(
    repo_root: Path | None = None,
    platform_input: dict | None = None,
    platform: str | None = None,
) -> Path | None:
    """
    获取：Get current task directory absolute path.


    参数:
        repo_root: Repository root path. Defaults to auto-detected.


    返回:
        Absolute path to current task directory or None.
    """
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # relative ← 调用 get_current_task
    relative = get_current_task(repo_root, platform_input, platform)
    # 条件分支：relative
    if relative:
        # 返回 resolve_task_ref 的调用结果
        return resolve_task_ref(relative, repo_root)
    return None  # 返回 None


def get_current_task_source(
    repo_root: Path | None = None,
    platform_input: dict | None = None,
    platform: str | None = None,
) -> tuple[str, str | None, str | None]:
    """获取：Get active task source as (`source`, `context_key`, `task_path`)."""
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # 局部导入 active_task
    from .active_task import get_current_task_source as _get_source

    # 返回 _get_source 的调用结果
    return _get_source(repo_root, platform_input, platform)


def set_current_task(
    task_path: str,
    repo_root: Path | None = None,
    platform_input: dict | None = None,
    platform: str | None = None,
) -> bool:
    """
    设置：Set current task in session scope.


    参数:
        task_path: Task directory path (relative to repo_root).
        repo_root: Repository root path. Defaults to auto-detected.


    返回:
        True on success, False on error.
    """
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # 局部导入 active_task
    from .active_task import set_active_task

    # 返回 set_active_task( task_path, repo_ro…
    return set_active_task(
        task_path,
        repo_root,
        platform_input=platform_input,
        platform=platform,
    ) is not None


def clear_current_task(
    repo_root: Path | None = None,
    platform_input: dict | None = None,
    platform: str | None = None,
) -> bool:
    """
    清空/重置：Clear current task in session scope.


    参数:
        repo_root: Repository root path. Defaults to auto-detected.


    返回:
        True on success.
    """
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # 局部导入 active_task
    from .active_task import clear_active_task

    # 调用 clear_active_task
    clear_active_task(
        repo_root,
        platform_input=platform_input,
        platform=platform,
    )
    return True  # 返回 True


def has_current_task(repo_root: Path | None = None) -> bool:
    """
    检查/校验：Check if has current task.


    参数:
        repo_root: Repository root path. Defaults to auto-detected.


    返回:
        True if current task is set.
    """
    # 返回 get_current_task(repo_root) is not …
    return get_current_task(repo_root) is not None


# 说明：=============================================================================
# 任务 ID 生成
# 说明：=============================================================================

def generate_task_date_prefix() -> str:
    """
    生成：Generate task ID based on date (MM-DD format).


    返回:
        Date prefix string (e.g., "01-21").
    """
    # 返回 datetime.now().strftime 的调用结果
    return datetime.now().strftime("%m-%d")


# 说明：=============================================================================
# Monorepo / 包路径
# 说明：=============================================================================


def get_spec_dir(package: str | None = None, repo_root: Path | None = None) -> Path:
    """
    获取：Get the spec directory path.

    Single-repo: .trellis/spec
    Monorepo with package: .trellis/spec/<package>

    Uses lazy import to avoid circular dependency with config.py.
    """
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # 局部导入 config
    from .config import get_spec_base

    # base ← 调用 get_spec_base
    base = get_spec_base(package, repo_root)
    # 返回 repo_root / DIR_WORKFLOW / base
    return repo_root / DIR_WORKFLOW / base


def get_package_path(package: str, repo_root: Path | None = None) -> Path | None:
    """
    获取：Get a package's source directory absolute path from config.


    返回:
        Absolute path to the package directory, or None if not found.
    """
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # 局部导入 config
    from .config import get_packages

    # packages ← 调用 get_packages
    packages = get_packages(repo_root)
    # 若条件不成立：not packages or package not in packages
    if not packages or package not in packages:
        return None  # 返回 None

    # 按键/下标取值赋给 info
    info = packages[package]
    # 条件分支：isinstance(info, dict)
    if isinstance(info, dict):
        # rel_path ← 调用 info.get
        rel_path = info.get("path", package)
    else:
        # rel_path ← 调用 str
        rel_path = str(info)

    # 返回 repo_root / rel_path
    return repo_root / rel_path


# 说明：=============================================================================
# 测试用主入口
# 说明：=============================================================================

# 条件分支：__name__ == "__main__"
# 直接运行本文件时进入入口
if __name__ == "__main__":
    # repo ← 调用 get_repo_root
    repo = get_repo_root()
    # 输出信息
    print(f"Repository root: {repo}")
    # 输出信息
    print(f"Developer: {get_developer(repo)}")
    # 输出信息
    print(f"Tasks dir: {get_tasks_dir(repo)}")
    # 输出信息
    print(f"Workspace dir: {get_workspace_dir(repo)}")
    # 输出信息
    print(f"Journal file: {get_active_journal_file(repo)}")
    # 输出信息
    print(f"Current task: {get_current_task(repo)}")
