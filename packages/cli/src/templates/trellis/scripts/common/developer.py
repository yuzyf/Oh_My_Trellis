#!/usr/bin/env python3
"""
developer 模块：Developer management utilities.


提供:
init_developer     - Initialize developer
ensure_developer   - Ensure developer is initialized (exit if not)
show_developer_info - Show developer information
"""

# 启用延迟注解求值等 future 特性
from __future__ import annotations

# 导入依赖
import sys
from datetime import datetime
from pathlib import Path

from .paths import (
    DIR_WORKFLOW,
    DIR_WORKSPACE,
    DIR_TASKS,
    FILE_DEVELOPER,
    FILE_JOURNAL_PREFIX,
    get_repo_root,
    get_developer,
    check_developer,
)


# =============================================================================
# 开发者初始化
# =============================================================================

def init_developer(name: str, repo_root: Path | None = None) -> bool:
    """
    初始化：Initialize developer.

    Creates:
        - .trellis/.developer file with developer info
        - .trellis/workspace/<name>/ directory structure
        - Initial journal file and index.md


    参数:
        name: Developer name.
        repo_root: Repository root path. Defaults to auto-detected.


    返回:
        True on success, False on error.
    """
    # 若条件不成立：not name
    if not name:
        # 输出信息
        print("Error: developer name is required", file=sys.stderr)
        return False  # 返回 False

    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # 计算后赋给 dev_file
    dev_file = repo_root / DIR_WORKFLOW / FILE_DEVELOPER
    # 计算后赋给 workspace_dir
    workspace_dir = repo_root / DIR_WORKFLOW / DIR_WORKSPACE / name

    # 创建 .developer 文件
    # initialized_at ← 调用 datetime.now().isoformat
    initialized_at = datetime.now().isoformat()
    # try：执行可能失败的逻辑
    try:
        # 写入文件
        dev_file.write_text(
            f"name={name}\ninitialized_at={initialized_at}\n",
            encoding="utf-8"
        )
    except (OSError, IOError) as e:
        # 输出信息
        print(f"Error: Failed to create .developer file: {e}", file=sys.stderr)
        return False  # 返回 False

    # 创建工作区目录结构
    # try：执行可能失败的逻辑
    try:
        # 创建目录
        workspace_dir.mkdir(parents=True, exist_ok=True)
    except (OSError, IOError) as e:
        # 输出信息
        print(f"Error: Failed to create workspace directory: {e}", file=sys.stderr)
        return False  # 返回 False

    # 创建初始 journal 文件
    # 计算后赋给 journal_file
    journal_file = workspace_dir / f"{FILE_JOURNAL_PREFIX}1.md"
    # 若条件不成立：not journal_file.exists()
    if not journal_file.exists():
        # today ← 调用 datetime.now().strftime
        today = datetime.now().strftime("%Y-%m-%d")
        # 拼出字符串赋给 journal_content
        journal_content = f"""# Journal - {name} (Part 1)

> AI development session journal
> Started: {today}

---

"""
        # try：执行可能失败的逻辑
        try:
            # 写入文件
            journal_file.write_text(journal_content, encoding="utf-8")
        except (OSError, IOError) as e:
            # 输出信息
            print(f"Error: Failed to create journal file: {e}", file=sys.stderr)
            return False  # 返回 False

    # 创建带自动更新标记的 index.md
    # 计算后赋给 index_file
    index_file = workspace_dir / "index.md"
    # 若条件不成立：not index_file.exists()
    if not index_file.exists():
        # 拼出字符串赋给 index_content
        index_content = f"""# Workspace Index - {name}

> Journal tracking for AI development sessions.

---

## Current Status

<!-- @@@auto:current-status -->
- **Active File**: `journal-1.md`
- **Total Sessions**: 0
- **Last Active**: -
<!-- @@@/auto:current-status -->

---

## Active Documents

<!-- @@@auto:active-documents -->
| File | Lines | Status |
|------|-------|--------|
| `journal-1.md` | ~0 | Active |
<!-- @@@/auto:active-documents -->

---

## Session History

<!-- @@@auto:session-history -->
| # | Date | Title | Commits | Branch |
|---|------|-------|---------|--------|
<!-- @@@/auto:session-history -->

---

## Notes

- Sessions are appended to journal files
- New journal file created when current exceeds 2000 lines
- Use `add_session.py` to record sessions
"""
        # try：执行可能失败的逻辑
        try:
            # 写入文件
            index_file.write_text(index_content, encoding="utf-8")
        except (OSError, IOError) as e:
            # 输出信息
            print(f"Error: Failed to create index.md: {e}", file=sys.stderr)
            return False  # 返回 False

    # 输出信息
    print(f"Developer initialized: {name}")
    # 输出信息
    print(f"  .developer file: {dev_file}")
    # 输出信息
    print(f"  Workspace dir: {workspace_dir}")

    return True  # 返回 True


def ensure_developer(repo_root: Path | None = None) -> None:
    """
    确保：Ensure developer is initialized, exit if not.


    参数:
        repo_root: Repository root path. Defaults to auto-detected.
    """
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # 若条件不成立：not check_developer(repo_root)
    if not check_developer(repo_root):
        # 输出信息
        print("Error: Developer not initialized.", file=sys.stderr)
        # 输出信息
        print(f"Run: python3 ./{DIR_WORKFLOW}/scripts/init_developer.py <your-name>", file=sys.stderr)
        # 结束进程/解析：sys.exit
        sys.exit(1)


def show_developer_info(repo_root: Path | None = None) -> None:
    """
    show_developer_info：Show developer information.


    参数:
        repo_root: Repository root path. Defaults to auto-detected.
    """
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # developer ← 调用 get_developer
    developer = get_developer(repo_root)

    # 若条件不成立：not developer
    if not developer:
        # 输出信息
        print("Developer: (not initialized)")
    else:
        # 输出信息
        print(f"Developer: {developer}")
        # 输出信息
        print(f"Workspace: {DIR_WORKFLOW}/{DIR_WORKSPACE}/{developer}/")
        # 输出信息
        print(f"Tasks: {DIR_WORKFLOW}/{DIR_TASKS}/")


# =============================================================================
# 测试用主入口
# =============================================================================

# 条件分支：__name__ == "__main__"
# 直接运行本文件时进入入口
if __name__ == "__main__":
    # 调用 show_developer_info
    show_developer_info()
