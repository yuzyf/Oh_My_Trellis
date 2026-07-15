"""
安全 git 提交辅助。

在尊重 gitignore 的前提下选择可 add 的 Trellis 路径，并给出警告。
"""

# 启用延迟注解求值等 future 特性
from __future__ import annotations

# 导入依赖
import sys
from pathlib import Path

from .git import run_git
from .paths import (
    DIR_ARCHIVE,
    DIR_TASKS,
    DIR_WORKFLOW,
    DIR_WORKSPACE,
    FILE_JOURNAL_PREFIX,
    get_developer,
)


# .trellis/ 下严禁自动暂存的路径。列在这里以便
# 警告能向用户展示可单独忽略的具体子路径
# 而不是忽略整个 `.trellis/` 树。
# 打包元组赋给 TRELLIS_IGNORED_SUB…
TRELLIS_IGNORED_SUBPATHS = (
    ".trellis/.backup-*",
    ".trellis/worktrees/",
    ".trellis/.template-hashes.json",
    ".trellis/.runtime/",
    ".trellis/.cache/",
)


def safe_trellis_paths_to_add(
    repo_root: Path,
    task_name: str | None = None,
) -> list[str]:
    """
    返回：Return the list of repo-relative paths the auto-commit should stage.

    Only includes paths that exist on disk so callers don't pass non-existent
    arguments to git. The caller is responsible for `git diff --cached`
    checking afterwards.

    Included:
      - .trellis/workspace/<developer>/journal-*.md
      - .trellis/workspace/<developer>/index.md
      - .trellis/tasks/<task_name>/   (ONLY the current task dir when
        ``task_name`` is passed; plus its archive location if the task
        already lives under archive/)

    Excluded (intentionally — these must not be staged):
      - .trellis/.backup-*, .trellis/worktrees/,
        .trellis/.template-hashes.json, .trellis/.runtime/, .trellis/.cache/

    Scope contract (see #303 / break-loop analysis): when ``task_name`` is
    passed, the task segment stages ONLY that task directory — it never walks
    ``tasks_dir.iterdir()`` over all active tasks. This mirrors
    :func:`safe_archive_paths_to_add` and prevents dirty changes in OTHER
    parallel-window task dirs from being bundled into the session auto-commit.

    Backwards-compat: with no ``task_name``, the function walks every active
    task directory (+ the archive subtree) the old wide way. New callers
    should always pass ``task_name``.
    """
    # 赋值（含类型标注）：paths
    paths: list[str] = []

    # 工作区 journal 文件与 index.md
    # developer ← 调用 get_developer
    developer = get_developer(repo_root)
    # 条件分支：developer
    if developer:
        # 计算后赋给 ws
        ws = repo_root / DIR_WORKFLOW / DIR_WORKSPACE / developer
        # 条件分支：ws.is_dir()
        if ws.is_dir():
            # 遍历：f in sorted(ws.glob(f"{FILE_JOURNAL_PREFIX}*.md"))
            for f in sorted(ws.glob(f"{FILE_JOURNAL_PREFIX}*.md")):
                # 条件分支：f.is_file()
                if f.is_file():
                    # 追加到列表
                    paths.append(
                        f"{DIR_WORKFLOW}/{DIR_WORKSPACE}/{developer}/{f.name}"
                    )
            # 计算后赋给 index_md
            index_md = ws / "index.md"
            # 条件分支：index_md.is_file()
            if index_md.is_file():
                # 追加到列表
                paths.append(
                    f"{DIR_WORKFLOW}/{DIR_WORKSPACE}/{developer}/index.md"
                )

    # 计算后赋给 tasks_dir
    tasks_dir = repo_root / DIR_WORKFLOW / DIR_TASKS
    # 若条件不成立：not tasks_dir.is_dir()
    if not tasks_dir.is_dir():
        return paths  # 返回 paths

    # 若已有值：task_name is not None
    if task_name is not None:
        # 窄作用域——仅当前任务目录（活动或已归档）。
        # 切勿对全部任务 iterdir()：并行窗口下其它任务的脏目录不得
        # 泄漏进会话自动提交。
        # 计算后赋给 active_task
        active_task = tasks_dir / task_name
        # 条件分支：active_task.is_dir()
        if active_task.is_dir():
            # 追加到列表
            paths.append(f"{DIR_WORKFLOW}/{DIR_TASKS}/{task_name}")
        # 计算后赋给 archived_task
        archived_task = tasks_dir / DIR_ARCHIVE / task_name
        # 条件分支：archived_task.is_dir()
        if archived_task.is_dir():
            # 追加到列表
            paths.append(
                f"{DIR_WORKFLOW}/{DIR_TASKS}/{DIR_ARCHIVE}/{task_name}"
            )
        return paths  # 返回 paths

    # 旧版宽作用域（无 task_name）：tasks/ 下每个直接子目录若是
    # 目录（且不是 archive 根），再加上整个 archive 子树。
    for child in sorted(tasks_dir.iterdir()):
        # 若条件不成立：not child.is_dir()
        if not child.is_dir():
            continue  # 跳过本轮循环
        # 条件分支：child.name == DIR_ARCHIVE
        if child.name == DIR_ARCHIVE:
            continue  # 跳过本轮循环
        # 追加到列表
        paths.append(f"{DIR_WORKFLOW}/{DIR_TASKS}/{child.name}")

    # 计算后赋给 archive_dir
    archive_dir = tasks_dir / DIR_ARCHIVE
    # 条件分支：archive_dir.is_dir()
    if archive_dir.is_dir():
        # 追加到列表
        paths.append(f"{DIR_WORKFLOW}/{DIR_TASKS}/{DIR_ARCHIVE}")

    return paths  # 返回 paths


def safe_archive_paths_to_add(
    repo_root: Path,
    task_name: str | None = None,
    modified_children: list[str] | None = None,
) -> list[str]:
    """
    返回：Return paths to stage after `task.py archive`.

    Scoped to ONLY the paths the archive operation actually touched:

      - the archive subtree (where the freshly-moved task lives)
      - the source task directory (for source-side deletes; caller pairs
        this with `git rm --cached` since `git add` won't stage deletes
        for a path that no longer exists in the working tree)
      - any child task directories whose `task.json` was edited to drop
        the archived parent (parent-children relationship update)

    This narrow scope avoids "scope creep" — dirty changes in OTHER
    active task dirs (parallel-window edits) are NOT bundled into the
    archive commit. Callers handle each kind of change in its own
    commit boundary.

    Backwards-compat: with no arguments, the function walks the whole
    `.trellis/tasks/` subtree the old way (active tasks + archive). New
    callers should always pass `task_name`.
    """
    # 赋值（含类型标注）：paths
    paths: list[str] = []
    # 计算后赋给 tasks_dir
    tasks_dir = repo_root / DIR_WORKFLOW / DIR_TASKS
    # 若条件不成立：not tasks_dir.is_dir()
    if not tasks_dir.is_dir():
        return paths  # 返回 paths

    # 计算后赋给 archive_dir
    archive_dir = tasks_dir / DIR_ARCHIVE

    # 若已有值：task_name is not None
    if task_name is not None:
        # 窄作用域——仅磁盘上仍存在的路径（以便
        # `git add` 不会因源路径已搬走而失败）。调用方
        # 通过 `git rm --cached` 处理源侧删除
        # 标识：explicitly.
        # 条件分支：archive_dir.is_dir()
        if archive_dir.is_dir():
            # 追加到列表
            paths.append(
                f"{DIR_WORKFLOW}/{DIR_TASKS}/{DIR_ARCHIVE}"
            )
        # 遍历：child_name in modified_children or []
        for child_name in modified_children or []:
            # 追加到列表
            paths.append(f"{DIR_WORKFLOW}/{DIR_TASKS}/{child_name}")
        return paths  # 返回 paths

    # 旧版宽作用域（无 task_name）：保留旧行为，使尚未更新的调用方
    # 仍可继续工作。
    # 条件分支：archive_dir.is_dir()
    if archive_dir.is_dir():
        # 追加到列表
        paths.append(f"{DIR_WORKFLOW}/{DIR_TASKS}/{DIR_ARCHIVE}")
    # 遍历：child in sorted(tasks_dir.iterdir())
    for child in sorted(tasks_dir.iterdir()):
        # 若条件不成立：not child.is_dir()
        if not child.is_dir():
            continue  # 跳过本轮循环
        # 条件分支：child.name == DIR_ARCHIVE
        if child.name == DIR_ARCHIVE:
            continue  # 跳过本轮循环
        # 追加到列表
        paths.append(f"{DIR_WORKFLOW}/{DIR_TASKS}/{child.name}")
    return paths  # 返回 paths


def _stderr_indicates_ignored(stderr: str) -> bool:
    """判断 git add 的错误输出是否表示路径被 .gitignore 排除。"""
    # 若条件不成立：not stderr
    if not stderr:
        return False  # 返回 False
    # lowered ← 调用 stderr.lower
    lowered = stderr.lower()
    # 返回 "ignored by" in lowered
    return "ignored by" in lowered


def safe_git_add(
    paths: list[str], repo_root: Path
) -> tuple[bool, bool, str]:
    """
    执行：Run `git add` on specific paths; never retry with -f.

    Returns ``(success, used_force, stderr)``. The ``used_force`` field is
    kept for signature compatibility with the 0.5.10 implementation but is
    always ``False`` — we never auto-force.

    Behavior:
      - No paths passed → success, no force, empty stderr.
      - Plain ``git add -- <paths>`` succeeds → return success.
      - Plain fails (any reason — ignored or otherwise) → return failure with
        the stderr. Callers should inspect the stderr (see
        :func:`print_gitignore_warning`) and skip the auto-commit.
    """
    # 若条件不成立：not paths
    if not paths:
        return True, False, ""  # 返回结果

    # rc, _, err ← 调用 run_git
    rc, _, err = run_git(["add", "--", *paths], cwd=repo_root)
    # 条件分支：rc == 0
    if rc == 0:
        return True, False, ""  # 返回结果
    return False, False, err  # 返回结果


def print_gitignore_warning(paths: list[str]) -> None:
    """向用户（以及阅读日志的 AI）解释路径因 gitignore 未被纳入暂存。"""
    # 输出信息
    print(
        "[WARN] git add failed because .trellis/ paths are ignored by your .gitignore.",
        file=sys.stderr,
    )
    # 输出信息
    print(
        "[WARN] Skipping auto-commit. The journal/task files were still written to disk;",
        file=sys.stderr,
    )
    # 输出信息
    print(
        "[WARN] git was not touched.",
        file=sys.stderr,
    )
    # 输出信息
    print("[WARN]", file=sys.stderr)
    # 输出信息
    print(
        "[WARN] Trellis manages these specific paths and they should be tracked:",
        file=sys.stderr,
    )
    # 条件分支：paths
    if paths:
        # 遍历：p in paths
        for p in paths:
            # 输出信息
            print(f"[WARN]   {p}", file=sys.stderr)
    else:
        # 输出信息
        print(
            "[WARN]   .trellis/workspace/<developer>/{journal-*.md,index.md}",
            file=sys.stderr,
        )
        # 输出信息
        print(
            "[WARN]   .trellis/tasks/<task-dir>/",
            file=sys.stderr,
        )
        # 输出信息
        print(
            "[WARN]   .trellis/tasks/archive/",
            file=sys.stderr,
        )
    # 输出信息
    print("[WARN]", file=sys.stderr)
    # 输出信息
    print(
        "[WARN] Recommended: change your .gitignore from `.trellis/` to specific",
        file=sys.stderr,
    )
    # 输出信息
    print(
        "[WARN] subpaths that should remain ignored, e.g.:",
        file=sys.stderr,
    )
    # 遍历：sub in TRELLIS_IGNORED_SUBPATHS
    for sub in TRELLIS_IGNORED_SUBPATHS:
        # 输出信息
        print(f"[WARN]   {sub}", file=sys.stderr)
    # 输出信息
    print("[WARN]", file=sys.stderr)
    # 输出信息
    print(
        "[WARN] Or, if you intentionally keep .trellis/ local-only, set in",
        file=sys.stderr,
    )
    # 输出信息
    print(
        "[WARN] .trellis/config.yaml:",
        file=sys.stderr,
    )
    # 输出信息
    print(
        "[WARN]   session_auto_commit: false",
        file=sys.stderr,
    )
    # 输出信息
    print(
        "[WARN] so the scripts skip git entirely and you can review / commit",
        file=sys.stderr,
    )
    # 输出信息
    print(
        "[WARN] manually with `git status` / `git add` / `git commit`.",
        file=sys.stderr,
    )
    # 输出信息
    print("[WARN]", file=sys.stderr)
    # 输出信息
    print(
        "[WARN] Do NOT use `git add -f .trellis/` — it pulls in backups, worktrees,",
        file=sys.stderr,
    )
    # 输出信息
    print(
        "[WARN] and runtime caches that should never be committed.",
        file=sys.stderr,
    )
