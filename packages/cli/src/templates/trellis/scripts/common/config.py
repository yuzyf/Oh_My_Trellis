#!/usr/bin/env python3
"""
Trellis 配置读取与解析。

从 config.yaml 等来源读取 monorepo/包/会话提交等相关配置。
"""

# 启用延迟注解求值等 future 特性
from __future__ import annotations

# 导入依赖
import sys
from pathlib import Path

from .paths import DIR_WORKFLOW, get_repo_root


# 说明：=============================================================================
# 简易 YAML 解析器（无第三方依赖）
# 说明：=============================================================================


def _unquote(s: str) -> str:
    """
    移除：Remove exactly one layer of matching surrounding quotes.

    Unlike str.strip('"'), this only removes the outermost pair,
    preserving any nested quotes inside the value.


    示例:
        _unquote('"hello"')        -> 'hello'
        _unquote("'hello'")        -> 'hello'
        _unquote('"echo \'hi\'"')  -> "echo 'hi'"
        _unquote('hello')          -> 'hello'
        _unquote('"hello\'')       -> '"hello\''  (mismatched, unchanged)
    """
    # 条件分支：len(s) >= 2 and s[0] == s[-1] and s[0] in…
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        # 返回下标/键取值 s[1:-1]
        return s[1:-1]
    return s  # 返回 s


def _strip_inline_comment(value: str) -> str:
    """剥离 ` # …` 行内注释，同时保留引号内的 `#`。"""
    # in_quote 置为 None（带类型）
    in_quote: str | None = None
    # 遍历：idx, ch in enumerate(value)
    for idx, ch in enumerate(value):
        # 条件分支：in_quote
        if in_quote:
            # 条件分支：ch == in_quote
            if ch == in_quote:
                # 初始化 in_quote
                in_quote = None
            continue  # 跳过本轮循环
        # 条件分支：ch in ('"', "'")
        if ch in ('"', "'"):
            in_quote = ch  # 将 ch 赋给 in_quote
            continue  # 跳过本轮循环
        # 条件分支：ch == "#" and (idx == 0 or value[idx - 1]…
        if ch == "#" and (idx == 0 or value[idx - 1].isspace()):
            # 返回下标/键取值 value[:idx]
            return value[:idx]
    return value  # 返回 value


def parse_simple_yaml(content: str) -> dict:
    """
    解析：Parse simple YAML with nested dict support (no dependencies).

    Supports:
        - key: value (string)
        - key: (followed by list items)
            - item1
            - item2
        - key: (followed by nested dict)
            nested_key: value
            nested_key2:
              - item

    Uses indentation to detect nesting (2+ spaces deeper = child).


    参数:
        content: YAML content string.


    返回:
        Parsed dict (values can be str, list[str], or dict).
    """
    # lines ← 调用 content.splitlines
    lines = content.splitlines()
    # 赋值（含类型标注）：result
    result: dict = {}
    # 调用 _parse_yaml_block
    _parse_yaml_block(lines, 0, 0, result)
    return result  # 返回 result


def _parse_yaml_block(
    lines: list[str], start: int, min_indent: int, target: dict
) -> int:
    """解析：Parse a YAML block into target dict, returning next line index."""
    i = start  # 将 start 赋给 i
    # current_list 置为 None（带类型）
    current_list: list | None = None

    # while 循环：i < len(lines)
    while i < len(lines):
        # 按键/下标取值赋给 line
        line = lines[i]
        # stripped ← 调用 line.strip
        stripped = line.strip()

        # 跳过 empty lines and comments
        if not stripped or stripped.startswith("#"):
            # 就地更新 i
            i += 1
            continue  # 跳过本轮循环

        # 计算缩进
        # 计算后赋给 indent
        indent = len(line) - len(line.lstrip())

        # 若缩进已回到块外则结束
        # 条件分支：indent < min_indent
        if indent < min_indent:
            # 跳出循环
            break

        # 条件分支：stripped.startswith("- ")
        if stripped.startswith("- "):
            # 若已有值：current_list is not None
            if current_list is not None:
                # 追加到列表
                current_list.append(_unquote(stripped[2:].strip()))
            # 就地更新 i
            i += 1
        # 条件分支：":" in stripped
        elif ":" in stripped:
            # key, _, value ← 调用 stripped.partition
            key, _, value = stripped.partition(":")
            # key ← 调用 key.strip
            key = key.strip()
            # value ← 调用 _strip_inline_comment(value).…
            value = _strip_inline_comment(value).strip()
            # value ← 调用 _unquote
            value = _unquote(value)
            # 初始化 current_list
            current_list = None

            # 条件分支：value
            if value:
                # key: value 形式
                target[key] = value
                # 就地更新 i
                i += 1
            else:
                # key:（无值）——向前看以区分 list 与嵌套 dict
                # next_i, next_line ← 调用 _next_content_line
                next_i, next_line = _next_content_line(lines, i + 1)
                # 条件分支：next_i >= len(lines)
                if next_i >= len(lines):
                    # target[key] 初始化为空字典
                    target[key] = {}
                    i = next_i  # 将 next_i 赋给 i
                # 条件分支：next_line.strip().startswith("- ")
                elif next_line.strip().startswith("- "):
                    # 说明：It's a list
                    # current_list 初始化为空列表
                    current_list = []
                    target[key] = current_list  # 下标项 ← current_list
                    # 就地更新 i
                    i += 1
                else:
                    # 计算后赋给 next_indent
                    next_indent = len(next_line) - len(next_line.lstrip())
                    # 条件分支：next_indent > indent
                    if next_indent > indent:
                        # 这是嵌套 dict
                        # 赋值（含类型标注）：nested
                        nested: dict = {}
                        target[key] = nested  # 下标项 ← nested
                        # i ← 调用 _parse_yaml_block
                        i = _parse_yaml_block(lines, i + 1, next_indent, nested)
                    else:
                        # 空值，后续同级或更小缩进
                        # target[key] 初始化为空字典
                        target[key] = {}
                        # 就地更新 i
                        i += 1
        else:
            # 就地更新 i
            i += 1

    return i  # 返回 i


def _next_content_line(lines: list[str], start: int) -> tuple[int, str]:
    """查找：Find the next non-empty, non-comment line."""
    i = start  # 将 start 赋给 i
    # while 循环：i < len(lines)
    while i < len(lines):
        # stripped ← 调用 lines[i].strip
        stripped = lines[i].strip()
        # 条件分支：stripped and not stripped.startswith("#")
        if stripped and not stripped.startswith("#"):
            return i, lines[i]  # 返回结果
        # 就地更新 i
        i += 1
    return i, ""  # 返回结果


# 标识：Defaults
# 初始化 DEFAULT_SESSION_COM…
DEFAULT_SESSION_COMMIT_MESSAGE = "chore: record journal"
# 初始化 DEFAULT_MAX_JOURNAL…
DEFAULT_MAX_JOURNAL_LINES = 2000
# 初始化 DEFAULT_SESSION_AUT…
DEFAULT_SESSION_AUTO_COMMIT = True
# 初始化 DEFAULT_CODEX_DISPA…
DEFAULT_CODEX_DISPATCH_MODE = "inline"

# 初始化 CONFIG_FILE
CONFIG_FILE = "config.yaml"


def _is_true_config_value(value: object) -> bool:
    """返回：Return True when a config value represents an enabled flag."""
    # 条件分支：isinstance(value, bool)
    if isinstance(value, bool):
        return value  # 返回 value
    # 条件分支：isinstance(value, str)
    if isinstance(value, str):
        # 返回 value.strip().lower() == "true"
        return value.strip().lower() == "true"
    return False  # 返回 False


def _get_config_path(repo_root: Path | None = None) -> Path:
    """获取：Get path to config.yaml."""
    # 逻辑运算结果赋给 root
    root = repo_root or get_repo_root()
    # 返回 root / DIR_WORKFLOW / CONFIG_FILE
    return root / DIR_WORKFLOW / CONFIG_FILE


def _load_config(repo_root: Path | None = None) -> dict:
    """加载/读取：Load and parse config.yaml. Returns empty dict on any error."""
    # config_file ← 调用 _get_config_path
    config_file = _get_config_path(repo_root)
    # try：执行可能失败的逻辑
    try:
        # content ← 调用 config_file.read_text
        content = config_file.read_text(encoding="utf-8")
        # 返回 parse_simple_yaml 的调用结果
        return parse_simple_yaml(content)
    except (OSError, IOError):
        return {}  # 返回字典结果


def get_session_commit_message(repo_root: Path | None = None) -> str:
    """获取：Get the commit message for auto-committing session records."""
    # config ← 调用 _load_config
    config = _load_config(repo_root)
    # 返回 config.get 的调用结果
    return config.get("session_commit_message", DEFAULT_SESSION_COMMIT_MESSAGE)


def get_max_journal_lines(repo_root: Path | None = None) -> int:
    """获取：Get the maximum lines per journal file."""
    # config ← 调用 _load_config
    config = _load_config(repo_root)
    # value ← 调用 config.get
    value = config.get("max_journal_lines", DEFAULT_MAX_JOURNAL_LINES)
    # try：执行可能失败的逻辑
    try:
        return int(value)  # 返回 int(...) 的结果
    except (ValueError, TypeError):
        return DEFAULT_MAX_JOURNAL_LINES  # 返回 DEFAULT_MAX_JOURNAL_LINES


def get_session_auto_commit(repo_root: Path | None = None) -> bool:
    """脚本是否应在会话写入后自动暂存并自动提交。"""
    # config ← 调用 _load_config
    config = _load_config(repo_root)
    # raw ← 调用 config.get
    raw = config.get("session_auto_commit", DEFAULT_SESSION_AUTO_COMMIT)
    # 条件分支：isinstance(raw, bool)
    if isinstance(raw, bool):
        return raw  # 返回 raw
    # s ← 调用 str(raw).strip().lower
    s = str(raw).strip().lower()
    # 条件分支：s in ("true", "yes", "1", "on")
    if s in ("true", "yes", "1", "on"):
        return True  # 返回 True
    # 条件分支：s in ("false", "no", "0", "off")
    if s in ("false", "no", "0", "off"):
        return False  # 返回 False
    # 输出信息
    print(
        f"[WARN] invalid session_auto_commit value: {raw!r}; using true (default)",
        file=sys.stderr,
    )
    return DEFAULT_SESSION_AUTO_COMMIT  # 返回 DEFAULT_SESSION_AUTO_COMMIT


def get_codex_dispatch_mode(repo_root: Path | None = None) -> str:
    """
    返回：Return Codex dispatch mode.

    Default is ``inline``. ``sub-agent`` is an explicit opt-in because Codex
    sub-agents do not inherit the parent session context.
    """
    # config ← 调用 _load_config
    config = _load_config(repo_root)
    # codex ← 调用 config.get
    codex = config.get("codex")
    # 若为 None：codex is None
    if codex is None:
        return DEFAULT_CODEX_DISPATCH_MODE  # 返回 DEFAULT_CODEX_DISPATCH_MODE
    # 若条件不成立：not isinstance(codex, dict)
    if not isinstance(codex, dict):
        # 输出信息
        print(
            f"[WARN] invalid codex config: {codex!r}; using {DEFAULT_CODEX_DISPATCH_MODE}",
            file=sys.stderr,
        )
        return DEFAULT_CODEX_DISPATCH_MODE  # 返回 DEFAULT_CODEX_DISPATCH_MODE

    # raw ← 调用 codex.get
    raw = codex.get("dispatch_mode", DEFAULT_CODEX_DISPATCH_MODE)
    # mode ← 调用 str(raw).strip().lower
    mode = str(raw).strip().lower()
    # 条件分支：mode in ("inline", "sub-agent")
    if mode in ("inline", "sub-agent"):
        return mode  # 返回 mode
    # 输出信息
    print(
        f"[WARN] invalid codex.dispatch_mode value: {raw!r}; using {DEFAULT_CODEX_DISPATCH_MODE}",
        file=sys.stderr,
    )
    return DEFAULT_CODEX_DISPATCH_MODE  # 返回 DEFAULT_CODEX_DISPATCH_MODE


def get_hooks(event: str, repo_root: Path | None = None) -> list[str]:
    """
    获取：Get hook commands for a lifecycle event.


    参数:
        event: Event name (e.g. "after_create", "after_archive").
        repo_root: Repository root path.


    返回:
        List of shell commands to execute, empty if none configured.
    """
    # config ← 调用 _load_config
    config = _load_config(repo_root)
    # hooks ← 调用 config.get
    hooks = config.get("hooks")
    # 若条件不成立：not isinstance(hooks, dict)
    if not isinstance(hooks, dict):
        return []  # 返回列表结果
    # commands ← 调用 hooks.get
    commands = hooks.get(event)
    # 条件分支：isinstance(commands, list)
    if isinstance(commands, list):
        return [str(c) for c in commands]  # 返回结果
    return []  # 返回列表结果


# 说明：=============================================================================
# Monorepo / 包配置
# 说明：=============================================================================


def get_packages(repo_root: Path | None = None) -> dict[str, dict] | None:
    """
    获取：Get monorepo package declarations.


    返回:
        Dict mapping package name to its config (path, type, etc.),
        or None if not configured (single-repo mode).

    Example return:
        {"cli": {"path": "packages/cli"}, "docs-site": {"path": "docs-site", "type": "submodule"}}
    """
    # config ← 调用 _load_config
    config = _load_config(repo_root)
    # packages ← 调用 config.get
    packages = config.get("packages")
    # 若条件不成立：not isinstance(packages, dict)
    if not isinstance(packages, dict):
        return None  # 返回 None
    # 确保 each value is a dict (filter out scalar entries)
    # 用推导式生成 filtered
    filtered = {k: v for k, v in packages.items() if isinstance(v, dict)}
    # 若条件不成立：not filtered
    if not filtered:
        return None  # 返回 None
    return filtered  # 返回 filtered


def get_default_package(repo_root: Path | None = None) -> str | None:
    """
    获取：Get the default package name from config.


    返回:
        Package name string, or None if not configured.
    """
    # config ← 调用 _load_config
    config = _load_config(repo_root)
    # value ← 调用 config.get
    value = config.get("default_package")
    # 按条件返回不同值
    return str(value) if value else None


def get_submodule_packages(repo_root: Path | None = None) -> dict[str, str]:
    """
    获取：Get packages that are git submodules.


    返回:
        Dict mapping package name to its path for submodule-type packages.
        Empty dict if none configured.

    Example return:
        {"docs-site": "docs-site"}
    """
    # packages ← 调用 get_packages
    packages = get_packages(repo_root)
    # 若为 None：packages is None
    if packages is None:
        return {}  # 返回字典结果
    return {  # 返回结果
        name: cfg.get("path", name)
        for name, cfg in packages.items()
        if cfg.get("type") == "submodule"
    }


def get_git_packages(repo_root: Path | None = None) -> dict[str, str]:
    """
    获取：Get packages that have their own independent git repository.

    These are sub-directories with their own .git (not submodules),
    marked with ``git: true`` in config.yaml.


    返回:
        Dict mapping package name to its path for git-repo packages.
        Empty dict if none configured.

    Example config::

        packages:
          backend:
            path: iqs
            git: true

    Example return::

        {"backend": "iqs"}
    """
    # packages ← 调用 get_packages
    packages = get_packages(repo_root)
    # 若为 None：packages is None
    if packages is None:
        return {}  # 返回字典结果
    return {  # 返回结果
        name: cfg.get("path", name)
        for name, cfg in packages.items()
        if _is_true_config_value(cfg.get("git"))
    }


def is_monorepo(repo_root: Path | None = None) -> bool:
    """
    检查/校验：Check if the project is configured as a monorepo (has packages in config).
    """
    # 返回 get_packages(repo_root) is not None
    return get_packages(repo_root) is not None


def get_spec_base(package: str | None = None, repo_root: Path | None = None) -> str:
    """
    获取：Get the spec directory base path relative to .trellis/.

    Single-repo: returns "spec"
    Monorepo with package: returns "spec/<package>"
    Monorepo without package: returns "spec" (caller should specify package)
    """
    # 条件分支：package and is_monorepo(repo_root)
    if package and is_monorepo(repo_root):
        return f"spec/{package}"  # 返回格式化字符串
    # 返回常量 'spec'
    return "spec"


def validate_package(package: str, repo_root: Path | None = None) -> bool:
    """
    检查/校验：Check if a package name is valid in this project.

    Single-repo (no packages configured): always returns True.
    Monorepo: returns True only if package exists in config.yaml packages.
    """
    # packages ← 调用 get_packages
    packages = get_packages(repo_root)
    # 若为 None：packages is None
    if packages is None:
        return True  # 单仓，无需校验
    # 返回 package in packages
    return package in packages


def resolve_package(
    task_package: str | None = None,
    repo_root: Path | None = None,
) -> str | None:
    """
    解析/解析出：Resolve package from inferred sources with validation.

    Checks in order: task_package → default_package.
    Invalid inferred values print a warning to stderr and are skipped.


    返回:
        Resolved package name, or None if no valid package found.


    说明:
        CLI --package should be validated separately by the caller
        (fail-fast with available packages list on error).
    """
    # packages ← 调用 get_packages
    packages = get_packages(repo_root)
    # 若为 None：packages is None
    if packages is None:
        return None  # 单仓，无需 package

    # 尝试 task_package（防止畸形 JSON 的非字符串值）
    # 条件分支：task_package and isinstance(task_package,…
    if task_package and isinstance(task_package, str):
        # 条件分支：task_package in packages
        if task_package in packages:
            return task_package  # 返回 task_package
        # 输出信息
        print(
            f"Warning: task.json package '{task_package}' not found in config, skipping",
            file=sys.stderr,
        )

    # 尝试 default_package
    # default ← 调用 get_default_package
    default = get_default_package(repo_root)
    # 条件分支：default
    if default:
        # 条件分支：default in packages
        if default in packages:
            return default  # 返回 default
        # 输出信息
        print(
            f"Warning: default_package '{default}' not found in config, skipping",
            file=sys.stderr,
        )

    return None  # 返回 None


def get_spec_scope(repo_root: Path | None = None) -> list[str] | str | None:
    """
    获取：Get session.spec_scope configuration.


    返回:
        list[str]: Package names to include in spec scanning.
        str: "active_task" to use current task's package.
        None: No scope configured (scan all packages).
    """
    # config ← 调用 _load_config
    config = _load_config(repo_root)
    # session ← 调用 config.get
    session = config.get("session")
    # 若条件不成立：not isinstance(session, dict)
    if not isinstance(session, dict):
        return None  # 返回 None

    # scope ← 调用 session.get
    scope = session.get("spec_scope")
    # 若为 None：scope is None
    if scope is None:
        return None  # 返回 None
    # 条件分支：isinstance(scope, str)
    if isinstance(scope, str):
        return scope  # 例如 "active_task"
    # 条件分支：isinstance(scope, list)
    if isinstance(scope, list):
        return [str(s) for s in scope]  # 返回结果
    return None  # 返回 None
