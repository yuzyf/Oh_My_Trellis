#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向 journal 追加新会话并更新 index.md。

用法:
    python3 add_session.py --title "Title" --commit "hash" --summary "Summary" [--package cli]
    python3 add_session.py --title "Title" --branch "feat/my-branch"

    # 也可通过 stdin 传入详细内容（需 --stdin）:
    # 也可通过 stdin 传入详细内容（需 --stdin）:
    cat << 'EOF' | python3 add_session.py --stdin --title "Title" --summary "Summary"
    <session content here>
    EOF

分支解析顺序:
    1. --branch CLI 参数（显式）
    2. 活跃任务 task.json 的 branch 字段（若仍存在）
    3. git branch --show-current（自动检测）
    4. None（优雅省略）
"""

# 启用延迟注解求值等 future 特性
from __future__ import annotations

# 导入依赖
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

from common.paths import (
    DIR_TASKS,
    DIR_WORKFLOW,
    FILE_JOURNAL_PREFIX,
    get_repo_root,
    get_current_task,
    get_developer,
    get_workspace_dir,
)
from common.developer import ensure_developer
from common.git import run_git
from common.safe_commit import (
    print_gitignore_warning,
    safe_git_add,
    safe_trellis_paths_to_add,
)
from common.tasks import load_task
from common.types import TaskInfo
from common.config import (
    get_packages,
    get_session_auto_commit,
    get_session_commit_message,
    get_max_journal_lines,
    is_monorepo,
    resolve_package,
    validate_package,
)


DEFAULT_MAIN_CHANGES = (
    "- Detailed change bullets were not supplied; see the summary above."
)
DEFAULT_TESTING = "- Validation was not recorded for this session."


# =============================================================================
# Helper Functions
# =============================================================================

# 辅助函数
def get_latest_journal_info(dev_dir: Path) -> tuple[Path | None, int, int]:
    """
获取：Get latest journal file info.


返回:
    Tuple of (file_path, file_number, line_count).
"""
    # latest_file 置为 None（带类型）
    latest_file: Path | None = None
    # 一元运算结果赋给 latest_num
    latest_num = -1

    # 遍历：f in dev_dir.glob(f"{FILE_JOURNAL_PREFIX}*.md")
    for f in dev_dir.glob(f"{FILE_JOURNAL_PREFIX}*.md"):
        # 若条件不成立：not f.is_file()
        if not f.is_file():
            continue  # 跳过本轮循环

        # match ← 调用 re.search
        match = re.search(r"(\d+)$", f.stem)
        # 条件分支：match
        if match:
            # num ← 调用 int
            num = int(match.group(1))
            # 条件分支：num > latest_num
            if num > latest_num:
                latest_num = num  # 将 num 赋给 latest_num
                latest_file = f  # 将 f 赋给 latest_file

    # 条件分支：latest_file
    if latest_file:
        # lines ← 调用 len
        lines = len(latest_file.read_text(encoding="utf-8").splitlines())
        return latest_file, latest_num, lines  # 返回结果

    return None, 0, 0  # 返回结果


def get_current_session(index_file: Path) -> int:
    """获取：Get current session number from index.md."""
    # 若条件不成立：not index_file.is_file()
    if not index_file.is_file():
        return 0  # 返回 0

    # content ← 调用 index_file.read_text
    content = index_file.read_text(encoding="utf-8")
    # 遍历：line in content.splitlines()
    for line in content.splitlines():
        # 条件分支："Total Sessions" in line
        if "Total Sessions" in line:
            # match ← 调用 re.search
            match = re.search(r":\s*(\d+)", line)
            if match:
                return int(match.group(1))  # 返回 int(...) 的结果
    return 0


def _extract_journal_num(filename: str) -> int:
    """从文件名提取 journal 编号，供排序使用。"""
    # match ← 调用 re.search
    match = re.search(r"(\d+)", filename)
    # 按条件返回不同值
    return int(match.group(1)) if match else 0


def count_journal_files(dev_dir: Path, active_num: int) -> str:
    """统计 journal 文件数量，并返回表格行数据。"""
    # 拼出字符串赋给 active_file
    active_file = f"{FILE_JOURNAL_PREFIX}{active_num}.md"
    # result_lines 初始化为空列表
    result_lines = []

    # files ← 调用 sorted
    files = sorted(
        [f for f in dev_dir.glob(f"{FILE_JOURNAL_PREFIX}*.md") if f.is_file()],
        key=lambda f: _extract_journal_num(f.stem),
        reverse=True
    )

    # 遍历：f in files
    for f in files:
        # 读取属性赋给 filename
        filename = f.name
        # lines ← 调用 len
        lines = len(f.read_text(encoding="utf-8").splitlines())
        # 按条件取值赋给 status
        status = "Active" if filename == active_file else "Archived"
        # 追加到列表
        result_lines.append(f"| `{filename}` | ~{lines} | {status} |")

    return "\n".join(result_lines)  # 返回 join(...) 的结果


def get_current_git_branch(repo_root: Path) -> str | None:
    """
返回：Return the current checkout branch, or None for detached/non-git states.
"""
    # rc, branch_out, _ ← 调用 run_git
    rc, branch_out, _ = run_git(["branch", "--show-current"], cwd=repo_root)
    # 条件分支：rc != 0
    if rc != 0:
        return None  # 返回 None
    # detected ← 调用 branch_out.strip
    detected = branch_out.strip()
    # 返回 detected or None
    return detected or None


def branch_ref_exists(repo_root: Path, branch: str) -> bool:
    """返回：Return True when branch exists locally or as the local origin ref."""
    # 遍历：ref in (f"refs/heads/{branch}", f"refs/remotes/ori
    for ref in (f"refs/heads/{branch}", f"refs/remotes/origin/{branch}"):
        # rc, _, _ ← 调用 run_git
        rc, _, _ = run_git(["show-ref", "--verify", "--quiet", ref], cwd=repo_root)
        # 条件分支：rc == 0
        if rc == 0:
            return True  # 返回 True
    return False  # 返回 False


def resolve_session_branch(
    repo_root: Path,
    cli_branch: str | None,
    task_data: TaskInfo | None,
) -> str | None:
    """
解析/解析出：Resolve journal branch without trusting stale task.json branch fields.
"""
    # 条件分支：cli_branch
    if cli_branch:
        return cli_branch  # 返回 cli_branch

    # current_branch ← 调用 get_current_git_branch
    current_branch = get_current_git_branch(repo_root)
    # 按条件取值赋给 raw_task_branch
    raw_task_branch = task_data.raw.get("branch") if task_data else None
    # 按条件取值赋给 task_branch
    task_branch = raw_task_branch.strip() if isinstance(raw_task_branch, str) else ""
    # 若条件不成立：not task_branch
    if not task_branch:
        return current_branch  # 返回 current_branch

    # 条件分支：branch_ref_exists(repo_root, task_branch)
    if branch_ref_exists(repo_root, task_branch):
        return task_branch  # 返回 task_branch

    # 条件分支：current_branch
    if current_branch:
        # 输出信息
        print(
            f"Warning: task.json branch '{task_branch}' no longer exists locally or as origin/{task_branch}; using current branch '{current_branch}'.",
            file=sys.stderr,
        )
        return current_branch

    print(
        f"Warning: task.json branch '{task_branch}' no longer exists locally or as origin/{task_branch}; omitting branch.",
        file=sys.stderr,
    )
    return None


def create_new_journal_file(
    dev_dir: Path, num: int, developer: str, today: str, max_lines: int = 2000,
) -> Path:
    """创建：Create a new journal file."""
    # 计算后赋给 prev_num
    prev_num = num - 1
    # 计算后赋给 new_file
    new_file = dev_dir / f"{FILE_JOURNAL_PREFIX}{num}.md"

    # 拼出字符串赋给 content
    content = f"""# Journal - {developer} (Part {num})

> Continuation from `{FILE_JOURNAL_PREFIX}{prev_num}.md` (archived at ~{max_lines} lines)
> Started: {today}

---

"""
    # 写入文件
    new_file.write_text(content, encoding="utf-8")
    return new_file  # 返回 new_file


def generate_session_content(
    session_num: int,
    title: str,
    commit: str,
    summary: str,
    extra_content: str,
    today: str,
    package: str | None = None,
    branch: str | None = None,
    testing_content: str = DEFAULT_TESTING,
) -> str:
    """生成：Generate session content."""
    # 条件分支：commit and commit != "-"
    if commit and commit != "-":
        # 初始化 commit_table
        commit_table = """| Hash | Message |
|------|---------|"""
        # 遍历：c in commit.split(",")
        for c in commit.split(","):
            # c ← 调用 c.strip
            c = c.strip()
            # 就地更新 commit_table
            commit_table += f"\n| `{c}` | (see git log) |"
    else:
        # 初始化 commit_table
        commit_table = "(No commits - planning session)"

    # 按条件取值赋给 package_line
    package_line = f"\n**Package**: {package}" if package else ""
    # 按条件取值赋给 branch_line
    branch_line = f"\n**Branch**: `{branch}`" if branch else ""

    # 返回格式化文本
    return f"""

## Session {session_num}: {title}

**Date**: {today}
**Task**: {title}{package_line}{branch_line}

### Summary

{summary}

### Main Changes

{extra_content}

### Git Commits

{commit_table}

### Testing

{testing_content}

### Status

[OK] **Completed**

### Next Steps

- None - task complete
"""


def update_index(
    index_file: Path,
    dev_dir: Path,
    title: str,
    commit: str,
    new_session: int,
    active_file: str,
    today: str,
    branch: str | None = None,
) -> bool:
    """更新：Update index.md with new session info."""
    # Format commit for display
    # 格式化 commit 供展示
    # 初始化 commit_display
    commit_display = "-"
    if commit and commit != "-":
        # commit_display ← 调用 re.sub
        commit_display = re.sub(r"([a-f0-9]{7,})", r"`\1`", commit.replace(",", ", "))

    # Get file number from active_file name
    # 从 active_file 文件名提取编号
    # match ← 调用 re.search
    match = re.search(r"(\d+)", active_file)
    # 按条件取值赋给 active_num
    active_num = int(match.group(1)) if match else 0
    # files_table ← 调用 count_journal_files
    files_table = count_journal_files(dev_dir, active_num)

    # 输出信息
    print(f"Updating index.md for session {new_session}...")
    # 输出信息
    print(f"  Title: {title}")
    # 输出信息
    print(f"  Commit: {commit_display}")
    # 输出信息
    print(f"  Active File: {active_file}")
    # 输出信息
    print()

    content = index_file.read_text(encoding="utf-8")

    # 条件分支："@@@auto:current-status" not in content
    if "@@@auto:current-status" not in content:
        # 输出信息
        print("Error: Markers not found in index.md. Please ensure markers exist.", file=sys.stderr)
        return False

    # Process sections
    # 处理各分区
    # lines ← 调用 content.splitlines
    lines = content.splitlines()
    # new_lines 初始化为空列表
    new_lines = []

    # 初始化 in_current_status
    in_current_status = False
    # 初始化 in_active_documents
    in_active_documents = False
    # 初始化 in_session_history
    in_session_history = False
    # 初始化 header_written
    header_written = False

    # 遍历：line in lines
    for line in lines:
        # 条件分支："@@@auto:current-status" in line
        if "@@@auto:current-status" in line:
            # 追加到列表
            new_lines.append(line)
            # 初始化 in_current_status
            in_current_status = True
            # 追加到列表
            new_lines.append(f"- **Active File**: `{active_file}`")
            # 追加到列表
            new_lines.append(f"- **Total Sessions**: {new_session}")
            # 追加到列表
            new_lines.append(f"- **Last Active**: {today}")
            continue

        # 条件分支："@@@/auto:current-status" in line
        if "@@@/auto:current-status" in line:
            in_current_status = False
            new_lines.append(line)
            continue

        # 条件分支："@@@auto:active-documents" in line
        if "@@@auto:active-documents" in line:
            new_lines.append(line)
            # 初始化 in_active_documents
            in_active_documents = True
            # 追加到列表
            new_lines.append("| File | Lines | Status |")
            # 追加到列表
            new_lines.append("|------|-------|--------|")
            # 追加到列表
            new_lines.append(files_table)
            continue

        # 条件分支："@@@/auto:active-documents" in line
        if "@@@/auto:active-documents" in line:
            in_active_documents = False
            new_lines.append(line)
            continue

        # 条件分支："@@@auto:session-history" in line
        if "@@@auto:session-history" in line:
            new_lines.append(line)
            # 初始化 in_session_history
            in_session_history = True
            header_written = False
            continue

        # 条件分支："@@@/auto:session-history" in line
        if "@@@/auto:session-history" in line:
            in_session_history = False
            new_lines.append(line)
            continue

        # 条件分支：in_current_status
        if in_current_status:
            continue

        # 条件分支：in_active_documents
        if in_active_documents:
            continue

        # 条件分支：in_session_history
        if in_session_history:
            # Migrate old 4/6-column headers to 5-column Branch-only history.
            # 把旧的 4/6 列表头迁移为仅含 Branch 的 5 列历史表
            # 条件分支：re.match( r"^\|\s*#\s*\|\s*Date\s*\|\s*Ti…
            if re.match(
                r"^\|\s*#\s*\|\s*Date\s*\|\s*Title\s*\|\s*Commits\s*\|\s*Branch\s*\|\s*Base Branch\s*\|\s*$",
                line,
            ):
                # 追加到列表
                new_lines.append("| # | Date | Title | Commits | Branch |")
                continue
            # 条件分支：re.match(r"^\|\s*#\s*\|\s*Date\s*\|\s*Tit…
            if re.match(r"^\|\s*#\s*\|\s*Date\s*\|\s*Title\s*\|\s*Commits\s*\|\s*Branch\s*\|\s*$", line):
                new_lines.append("| # | Date | Title | Commits | Branch |")
                continue
            # 条件分支：re.match(r"^\|\s*#\s*\|\s*Date\s*\|\s*Tit…
            if re.match(r"^\|\s*#\s*\|\s*Date\s*\|\s*Title\s*\|\s*Commits\s*\|\s*$", line):
                new_lines.append("| # | Date | Title | Commits | Branch |")
                continue
            # 条件分支：re.match(r"^\|[-| ]+\|\s*$", line) and no…
            if re.match(r"^\|[-| ]+\|\s*$", line) and not header_written:
                # 追加到列表
                new_lines.append("|---|------|-------|---------|--------|")
                # 追加到列表
                new_lines.append(f"| {new_session} | {today} | {title} | {commit_display} | `{branch or '-'}` |")
                # 初始化 header_written
                header_written = True
                continue
            new_lines.append(line)
            continue

        new_lines.append(line)

    # 写入文件
    index_file.write_text("\n".join(new_lines), encoding="utf-8")
    # 输出信息
    print("[OK] Updated index.md successfully!")
    return True


# =============================================================================
# Main Function
# =============================================================================

# 主函数
def _auto_commit_workspace(repo_root: Path) -> None:
    """在会话写入后，暂存 Trellis 管辖的工作区与当前任务路径并自动提交。"""
    # 若条件不成立：not get_session_auto_commit(repo_root)
    if not get_session_auto_commit(repo_root):
        print(
            "[OK] session_auto_commit: false — skipping git stage/commit.",
            file=sys.stderr,
        )
        # 返回（无值）
        return

    # commit_msg ← 调用 get_session_commit_message
    commit_msg = get_session_commit_message(repo_root)
    # Resolve the current task so staging is scoped to its dir only. The ref
    # is ``.trellis/tasks/<name>`` (or under archive/) — pass the bare name.
    # 解析当前任务，使暂存仅限其目录。引用
    # 为 ``.trellis/tasks/<name>``（或 archive/ 下）——传入裸名称。
    # current ← 调用 get_current_task
    current = get_current_task(repo_root)
    # 条件分支：current
    if current:
        # 读取属性赋给 task_name
        task_name = Path(current).name
        # paths ← 调用 safe_trellis_paths_to_add
        paths = safe_trellis_paths_to_add(repo_root, task_name=task_name)
    else:
        # Current task unknown (0 or >=2 parallel sessions — exactly the
        # parallel-window case #303 is about). Do NOT fall back to the wide
        # `tasks_dir.iterdir()` scan; that would re-leak other tasks' dirty
        # dirs into the session commit. Stage only the developer's journal/
        # index and skip every task dir.
        # 当前任务未知（0 个或 ≥2 个并行会话——正是
        # issue #303 描述的并行窗口情形）。切勿回退到宽泛的
        # `tasks_dir.iterdir()` 扫描；那会把其它任务的脏
        # 目录重新泄漏进会话提交。只暂存开发者的 journal/
        # index，并跳过所有任务目录。
        # 用推导式生成 paths
        paths = [
            p
            for p in safe_trellis_paths_to_add(repo_root, task_name=None)
            if not p.startswith(f"{DIR_WORKFLOW}/{DIR_TASKS}/")
        ]
    # 若条件不成立：not paths
    if not paths:
        # 输出信息
        print("[OK] No workspace changes to commit.", file=sys.stderr)
        return

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
        return

    # Check if there are staged changes for the paths we just staged.
    # 检查刚暂存路径是否确有 staged 变更。
    # rc, _, _ ← 调用 run_git
    rc, _, _ = run_git(
        ["diff", "--cached", "--quiet", "--", *paths], cwd=repo_root
    )
    if rc == 0:
        print("[OK] No workspace changes to commit.", file=sys.stderr)
        return

    # rc, _, commit_err ← 调用 run_git
    rc, _, commit_err = run_git(["commit", "-m", commit_msg], cwd=repo_root)
    if rc == 0:
        # 输出信息
        print(f"[OK] Auto-committed: {commit_msg}", file=sys.stderr)
    else:
        print(
            f"[WARN] Auto-commit failed: {commit_err.strip()}",
            file=sys.stderr,
        )


def add_session(
    title: str,
    commit: str = "-",
    summary: str = "Session summary was not supplied.",
    extra_content: str = DEFAULT_MAIN_CHANGES,
    auto_commit: bool = True,
    package: str | None = None,
    branch: str | None = None,
) -> int:
    """添加：Add a new session."""
    # repo_root ← 调用 get_repo_root
    # 只加载一次活动任务——包与分支解析共用
    repo_root = get_repo_root()
    # 调用 ensure_developer
    ensure_developer(repo_root)

    # developer ← 调用 get_developer
    developer = get_developer(repo_root)
    # 若条件不成立：not developer
    if not developer:
        # 输出信息
        print("Error: Developer not initialized", file=sys.stderr)
        # 返回常量 1
        return 1

    # dev_dir ← 调用 get_workspace_dir
    dev_dir = get_workspace_dir(repo_root)
    # 若条件不成立：not dev_dir
    if not dev_dir:
        # 输出信息
        print("Error: Workspace directory not found", file=sys.stderr)
        return 1

    # max_lines ← 调用 get_max_journal_lines
    max_lines = get_max_journal_lines(repo_root)

    # 计算后赋给 index_file
    index_file = dev_dir / "index.md"
    # today ← 调用 datetime.now().strftime
    today = datetime.now().strftime("%Y-%m-%d")

    # journal_file, curre… ← 调用 get_latest_journal_info
    journal_file, current_num, current_lines = get_latest_journal_info(dev_dir)
    # current_session ← 调用 get_current_session
    current_session = get_current_session(index_file)
    # 计算后赋给 new_session
    new_session = current_session + 1

    # session_content ← 调用 generate_session_content
    session_content = generate_session_content(
        new_session, title, commit, summary, extra_content, today, package,
        branch,
    )
    # content_lines ← 调用 len
    content_lines = len(session_content.splitlines())

    # 输出信息
    print("========================================", file=sys.stderr)
    # 输出信息
    print("ADD SESSION", file=sys.stderr)
    print("========================================", file=sys.stderr)
    # 输出信息
    print("", file=sys.stderr)
    # 输出信息
    print(f"Session: {new_session}", file=sys.stderr)
    # 输出信息
    print(f"Title: {title}", file=sys.stderr)
    # 输出信息
    print(f"Commit: {commit}", file=sys.stderr)
    print("", file=sys.stderr)
    # 输出信息
    print(f"Current journal file: {FILE_JOURNAL_PREFIX}{current_num}.md", file=sys.stderr)
    # 输出信息
    print(f"Current lines: {current_lines}", file=sys.stderr)
    # 输出信息
    print(f"New content lines: {content_lines}", file=sys.stderr)
    # 输出信息
    print(f"Total after append: {current_lines + content_lines}", file=sys.stderr)
    print("", file=sys.stderr)

    target_file = journal_file  # 将 journal_file 赋给 target_file
    target_num = current_num  # 将 current_num 赋给 target_num

    # 条件分支：current_lines + content_lines > max_lines
    if current_lines + content_lines > max_lines:
        # 计算后赋给 target_num
        target_num = current_num + 1
        # 输出信息
        print(f"[!] Exceeds {max_lines} lines, creating {FILE_JOURNAL_PREFIX}{target_num}.md", file=sys.stderr)
        # target_file ← 调用 create_new_journal_file
        target_file = create_new_journal_file(dev_dir, target_num, developer, today, max_lines)
        # 输出信息
        print(f"Created: {target_file}", file=sys.stderr)

    # Append session content
    # 追加会话内容
    # 条件分支：target_file
    if target_file:
        # with 上下文：target_file.open("a",…
        with target_file.open("a", encoding="utf-8") as f:
            # 输出信息
            f.write(session_content)
        # 输出信息
        print(f"[OK] Appended session to {target_file.name}", file=sys.stderr)

    print("", file=sys.stderr)

    # Update index.md
    # 更新 index.md
    # 拼出字符串赋给 active_file
    active_file = f"{FILE_JOURNAL_PREFIX}{target_num}.md"
    # 若条件不成立：not update_index(
    if not update_index(
        index_file,
        dev_dir,
        title,
        commit,
        new_session,
        active_file,
        today,
        branch,
    ):
        return 1

    print("", file=sys.stderr)
    print("========================================", file=sys.stderr)
    # 输出信息
    print(f"[OK] Session {new_session} added successfully!", file=sys.stderr)
    print("========================================", file=sys.stderr)
    print("", file=sys.stderr)
    # 输出信息
    print("Files updated:", file=sys.stderr)
    # 输出信息
    print(f"  - {target_file.name if target_file else 'journal'}", file=sys.stderr)
    # 输出信息
    print("  - index.md", file=sys.stderr)

    # Auto-commit workspace changes
    # 自动提交工作区变更
    # 条件分支：auto_commit
    if auto_commit:
        print("", file=sys.stderr)
        # 调用 _auto_commit_workspace
        _auto_commit_workspace(repo_root)

    return 0


# =============================================================================
# Main Entry
# =============================================================================

# 主入口
def main() -> int:
    """入口：CLI entry point."""
    # parser ← 调用 argparse.ArgumentParser
    parser = argparse.ArgumentParser(
        description="Add a new session to journal file and update index.md"
    )
    # 注册 CLI 参数/子命令
    parser.add_argument("--title", required=True, help="Session title")
    # 注册 CLI 参数/子命令
    parser.add_argument("--commit", default="-", help="Comma-separated commit hashes")
    parser.add_argument("--summary", default="Session summary was not supplied.", help="Brief summary")
    # 注册 CLI 参数/子命令
    parser.add_argument("--content-file", help="Path to file with detailed content")
    # 注册 CLI 参数/子命令
    parser.add_argument("--package", help="Package name tag (e.g., cli, docs-site)")
    # 注册 CLI 参数/子命令
    parser.add_argument("--branch", help="Branch name (auto-detected if omitted)")
    # 注册 CLI 参数/子命令
    parser.add_argument("--no-commit", action="store_true",
                        help="Skip auto-commit of workspace changes")
    # 注册 CLI 参数/子命令
    parser.add_argument("--stdin", action="store_true",
                        help="Read extra content from stdin (explicit opt-in)")

    # args ← 调用 parser.parse_args
    args = parser.parse_args()

    extra_content = DEFAULT_MAIN_CHANGES
    # 条件分支：args.content_file
    if args.content_file:
        # content_path ← 调用 Path
        content_path = Path(args.content_file)
        # 条件分支：content_path.is_file()
        if content_path.is_file():
            # extra_content ← 调用 content_path.read_text
            extra_content = content_path.read_text(encoding="utf-8")
    # 条件分支：args.stdin
    elif args.stdin:
        # extra_content ← 调用 sys.stdin.read
        extra_content = sys.stdin.read()

    # Load active task once — shared by package and branch resolution
    repo_root = get_repo_root()
    current = get_current_task(repo_root)
    # 按条件取值赋给 task_data
    task_data = load_task(repo_root / current) if current else None

    # 读取属性赋给 package
    package = args.package
    # 条件分支：package
    if package:
        # CLI source: fail-fast in monorepo, ignore in single-repo
        # CLI 来源：monorepo 快速失败，单仓忽略
        if not is_monorepo(repo_root):
            # 输出信息
            print("Warning: --package ignored in single-repo project", file=sys.stderr)
            # 初始化 package
            package = None
        # 条件分支：elif not validate_package(package, repo_root)
        elif not validate_package(package, repo_root):
            # packages ← 调用 get_packages
            packages = get_packages(repo_root)
            # 按条件取值赋给 available
            available = ", ".join(sorted(packages.keys())) if packages else "(none)"
            # 输出信息
            print(f"Error: unknown package '{package}'. Available: {available}", file=sys.stderr)
            return 1
    else:
        # Inferred: active task's task.json.package → default_package → None
        # 推断：活动任务 task.json.package → default_package → None
        # 按条件取值赋给 task_package
        task_package = task_data.package if task_data else None
        # package ← 调用 resolve_package
        package = resolve_package(task_package, repo_root)

    # branch ← 调用 resolve_session_branch
    branch = resolve_session_branch(repo_root, args.branch, task_data)

    # 返回 add_session 的调用结果
    return add_session(
        args.title, args.commit, args.summary, extra_content,
        auto_commit=not args.no_commit,
        package=package,
        branch=branch,
    )


# 条件分支：__name__ == "__main__"
# 直接运行本文件时进入入口
if __name__ == "__main__":
    # 结束进程/解析：sys.exit
    sys.exit(main())
