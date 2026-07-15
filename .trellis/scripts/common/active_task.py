#!/usr/bin/env python3
"""
活跃任务（active task）解析与持久化。

负责当前任务指针、上下文键（context key）与 active task 的读写。
"""

# 启用延迟注解求值等 future 特性
from __future__ import annotations

# 导入依赖
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# 工作流根目录名（.trellis）
DIR_WORKFLOW = ".trellis"
# 任务目录名
DIR_TASKS = "tasks"
# 初始化 DIR_RUNTIME
DIR_RUNTIME = ".runtime"
# 初始化 DIR_SESSIONS
DIR_SESSIONS = "sessions"
# 初始化 DIR_CURSOR_SHELL
DIR_CURSOR_SHELL = "cursor-shell"
# 初始化 CURSOR_SHELL_TICKET…
CURSOR_SHELL_TICKET_TTL_SECONDS = 30
# 构造集合赋给 TASK_SESSION_COMMAN…
TASK_SESSION_COMMANDS = {"start", "current", "finish"}

# 打包元组赋给 _SESSION_KEYS
_SESSION_KEYS = ("session_id", "sessionId", "sessionID")
# 打包元组赋给 _CONVERSATION_KEYS
_CONVERSATION_KEYS = ("conversation_id", "conversationId", "conversationID")
# 打包元组赋给 _TRANSCRIPT_KEYS
_TRANSCRIPT_KEYS = ("transcript_path", "transcriptPath", "transcript")
# 打包元组赋给 _NESTED_KEYS
_NESTED_KEYS = ("input", "properties", "event", "hook_input", "hookInput")
# 构造集合赋给 _KNOWN_PLATFORMS
_KNOWN_PLATFORMS = {
    "claude",
    "codex",
    "cursor",
    "opencode",
    "gemini",
    "droid",
    "qoder",
    "codebuddy",
    "kiro",
    "copilot",
    "pi",
}

# 赋值（含类型标注）：_ENV_SESSION_KEYS
_ENV_SESSION_KEYS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("claude", ("CLAUDE_SESSION_ID", "CLAUDE_CODE_SESSION_ID")),
    ("codex", ("CODEX_SESSION_ID", "CODEX_THREAD_ID")),
    ("cursor", ("CURSOR_SESSION_ID",)),
    ("opencode", ("OPENCODE_SESSION_ID", "OPENCODE_SESSIONID", "OPENCODE_RUN_ID")),
    ("gemini", ("GEMINI_SESSION_ID",)),
    ("droid", ("FACTORY_SESSION_ID", "DROID_SESSION_ID")),
    ("qoder", ("QODER_SESSION_ID",)),
    ("codebuddy", ("CODEBUDDY_SESSION_ID",)),
    ("kiro", ("KIRO_SESSION_ID",)),
    ("copilot", ("COPILOT_SESSION_ID", "COPILOT_SESSIONID")),
    ("pi", ("PI_SESSION_ID", "PI_SESSIONID")),
)
# 赋值（含类型标注）：_ENV_CONVERSATION_KEYS
_ENV_CONVERSATION_KEYS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("cursor", ("CURSOR_CONVERSATION_ID", "CURSOR_CONVERSATIONID")),
)
# 赋值（含类型标注）：_ENV_TRANSCRIPT_KEYS
_ENV_TRANSCRIPT_KEYS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("claude", ("CLAUDE_TRANSCRIPT_PATH",)),
    ("codex", ("CODEX_TRANSCRIPT_PATH",)),
    ("cursor", ("CURSOR_TRANSCRIPT_PATH",)),
    ("gemini", ("GEMINI_TRANSCRIPT_PATH",)),
    ("droid", ("FACTORY_TRANSCRIPT_PATH", "DROID_TRANSCRIPT_PATH")),
    ("qoder", ("QODER_TRANSCRIPT_PATH",)),
    ("codebuddy", ("CODEBUDDY_TRANSCRIPT_PATH",)),
)
# 构造字典赋给 _ENV_PLATFORM_ALIAS…
_ENV_PLATFORM_ALIASES = {
    "claude-code": "claude",
    "factory": "droid",
    "factory-ai": "droid",
    "github-copilot": "copilot",
}


@dataclass(frozen=True)
class ActiveTask:
    """ActiveTask 类：Resolved active task state."""

    # 声明带类型标注的字段/变量：task_path
    task_path: str | None
    # 声明带类型标注的字段/变量：source_type
    source_type: str
    # context_key 置为 None（带类型）
    context_key: str | None = None
    # 赋值（含类型标注）：stale
    stale: bool = False

    @property
    def source(self) -> str:
        """可读的来源标签（source）。"""
        # 条件分支：self.source_type == "session" and self.co…
        if self.source_type == "session" and self.context_key:
            return f"session:{self.context_key}"  # 返回格式化字符串
        # 条件分支：self.source_type == "session-fallback" an…
        if self.source_type == "session-fallback" and self.context_key:
            return f"session-fallback:{self.context_key}"  # 返回格式化字符串
        # 返回属性 self.source_type
        return self.source_type


def normalize_task_ref(task_ref: str) -> str:
    """规范化：Normalize a task ref for stable storage and comparison."""
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


def resolve_task_ref(task_ref: str, repo_root: Path) -> Path | None:
    """解析/解析出：Resolve a task ref to an absolute task directory."""
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


# 定义函数 _runtime_sessions_dir
def _runtime_sessions_dir(repo_root: Path) -> Path:
    # 返回 repo_root / DIR_WORKFLOW / DIR_RUNT…
    return repo_root / DIR_WORKFLOW / DIR_RUNTIME / DIR_SESSIONS


# 定义函数 _sanitize_key
def _sanitize_key(raw: str) -> str:
    # safe ← 调用 re.sub
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", raw.strip())
    # safe ← 调用 safe.strip
    safe = safe.strip("._-")
    # 按条件返回不同值
    return safe[:160] if safe else ""


# 定义函数 _hash_value
def _hash_value(raw: str) -> str:
    # 返回下标/键取值 hashlib.sha256(raw.encode("ut…
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


# 定义函数 _as_dict
def _as_dict(value: Any) -> dict[str, Any] | None:
    # 按条件返回不同值
    return value if isinstance(value, dict) else None


# 定义函数 _string_value
def _string_value(value: Any) -> str | None:
    # 条件分支：isinstance(value, str)
    if isinstance(value, str):
        # stripped ← 调用 value.strip
        stripped = value.strip()
        # 返回 stripped or None
        return stripped or None
    return None  # 返回 None


# 定义函数 _lookup_string
def _lookup_string(data: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    # 遍历：key in keys
    for key in keys:
        # value ← 调用 _string_value
        value = _string_value(data.get(key))
        # 条件分支：value
        if value:
            return value  # 返回 value

    # 遍历：nested_key in _NESTED_KEYS
    for nested_key in _NESTED_KEYS:
        # nested ← 调用 _as_dict
        nested = _as_dict(data.get(nested_key))
        # 若条件不成立：not nested
        if not nested:
            continue  # 跳过本轮循环
        # value ← 调用 _lookup_string
        value = _lookup_string(nested, keys)
        # 条件分支：value
        if value:
            return value  # 返回 value

    return None  # 返回 None


# 定义函数 _detect_platform
def _detect_platform(platform_input: dict[str, Any] | None, platform: str | None) -> str:
    # 条件分支：platform
    if platform:
        # 返回 _sanitize_key(platform) or "session"
        return _sanitize_key(platform) or "session"
    # 条件分支：platform_input
    if platform_input:
        # 遍历：key in ("_trellis_platform", "trellis_platform", "
        for key in ("_trellis_platform", "trellis_platform", "platform", "source"):
            # value ← 调用 _string_value
            value = _string_value(platform_input.get(key))
            # 条件分支：value
            if value:
                # 返回 _sanitize_key(value) or "session"
                return _sanitize_key(value) or "session"
        # 条件分支：_string_value(platform_input.get("cursor_…
        if _string_value(platform_input.get("cursor_version")):
            # 返回常量 'cursor'
            return "cursor"
    # 返回常量 'session'
    return "session"


# 定义函数 _context_key
def _context_key(platform_name: str, kind: str, value: str) -> str:
    # 条件分支：kind == "transcript"
    if kind == "transcript":
        return f"{platform_name}_transcript_{_hash_value(value)}"  # 返回格式化字符串
    # safe_value ← 调用 _sanitize_key
    safe_value = _sanitize_key(value)
    # 条件分支：safe_value
    if safe_value:
        return f"{platform_name}_{safe_value}"  # 返回格式化字符串
    return f"{platform_name}_{_hash_value(value)}"  # 返回格式化字符串


# 定义函数 _iter_env_keys
def _iter_env_keys(
    env_keys: tuple[tuple[str, tuple[str, ...]], ...],
    platform_name: str | None,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    # 若条件不成立：not platform_name
    if not platform_name:
        return env_keys  # 返回 env_keys
    # matched ← 调用 tuple
    matched = tuple((name, keys) for name, keys in env_keys if name == platform_name)
    return matched  # 返回 matched


# 定义函数 _env_platform_name
def _env_platform_name(platform_name: str | None) -> str | None:
    # 若条件不成立：not platform_name or platform_name == "session"
    if not platform_name or platform_name == "session":
        return None  # 返回 None
    # 返回 _ENV_PLATFORM_ALIASES.get 的调用结果
    return _ENV_PLATFORM_ALIASES.get(platform_name, platform_name)


def _lookup_env_context_key(platform_name: str | None) -> str | None:
    """
    解析/解析出：Resolve a context key from platform-provided environment variables.

    Hooks pass `TRELLIS_CONTEXT_ID` to subprocesses they launch, but an AI-run
    shell command can only see session identity if the host platform exports it
    in the command environment. These names are best-effort adapters; if none
    are present, there is no session-scoped active task.
    """
    # env_platform_name ← 调用 _env_platform_name
    env_platform_name = _env_platform_name(platform_name)

    # 遍历：name, keys in _iter_env_keys(_ENV_SESSION_KEYS, en
    for name, keys in _iter_env_keys(_ENV_SESSION_KEYS, env_platform_name):
        # 遍历：key in keys
        for key in keys:
            # value ← 调用 _string_value
            value = _string_value(os.environ.get(key))
            # 条件分支：value
            if value:
                # 返回 _context_key 的调用结果
                return _context_key(name, "session", value)

    # 遍历：name, keys in _iter_env_keys(_ENV_CONVERSATION_KEY
    for name, keys in _iter_env_keys(_ENV_CONVERSATION_KEYS, env_platform_name):
        # 遍历：key in keys
        for key in keys:
            # value ← 调用 _string_value
            value = _string_value(os.environ.get(key))
            # 条件分支：value
            if value:
                # 返回 _context_key 的调用结果
                return _context_key(name, "conversation", value)

    # 遍历：name, keys in _iter_env_keys(_ENV_TRANSCRIPT_KEYS,
    for name, keys in _iter_env_keys(_ENV_TRANSCRIPT_KEYS, env_platform_name):
        # 遍历：key in keys
        for key in keys:
            # value ← 调用 _string_value
            value = _string_value(os.environ.get(key))
            # 条件分支：value
            if value:
                # 返回 _context_key 的调用结果
                return _context_key(name, "transcript", value)

    return None  # 返回 None


# 定义函数 _find_repo_root_from_cwd
def _find_repo_root_from_cwd() -> Path | None:
    # current ← 调用 Path.cwd().resolve
    current = Path.cwd().resolve()
    # while 循环：True
    while True:
        # 条件分支：(current / DIR_WORKFLOW).is_dir()
        if (current / DIR_WORKFLOW).is_dir():
            return current  # 返回 current
        # 条件分支：current == current.parent
        if current == current.parent:
            return None  # 返回 None
        # 读取属性赋给 current
        current = current.parent


# 定义函数 _cursor_shell_ticket_dir
def _cursor_shell_ticket_dir(repo_root: Path) -> Path:
    # 返回 repo_root / DIR_WORKFLOW / DIR_RUNT…
    return repo_root / DIR_WORKFLOW / DIR_RUNTIME / DIR_CURSOR_SHELL


# 定义函数 _remove_file
def _remove_file(path: Path) -> bool:
    # try：执行可能失败的逻辑
    try:
        # 删除或替换文件
        path.unlink()
        return True  # 返回 True
    except OSError:
        return False  # 返回 False


# 定义函数 _task_refs_match
def _task_refs_match(left: str | None, right: str | None, repo_root: Path) -> bool:
    # 若条件不成立：not left or not right
    if not left or not right:
        return False  # 返回 False
    # left_path ← 调用 resolve_task_ref
    left_path = resolve_task_ref(left, repo_root)
    # right_path ← 调用 resolve_task_ref
    right_path = resolve_task_ref(right, repo_root)
    # 若已有值：left_path is not None and right_path is not None
    if left_path is not None and right_path is not None:
        # 返回 left_path == right_path
        return left_path == right_path
    # 返回 normalize_task_ref(left) == normali…
    return normalize_task_ref(left) == normalize_task_ref(right)


# 定义函数 _pending_ticket_matches_args
def _pending_ticket_matches_args(ticket: dict[str, Any], repo_root: Path) -> bool:
    # 条件分支：Path(sys.argv[0]).name != "task.py"
    if Path(sys.argv[0]).name != "task.py":
        return False  # 返回 False
    # args ← 调用 tuple
    args = tuple(sys.argv[1:])
    # 若条件不成立：not args
    if not args:
        return False  # 返回 False

    # 按键/下标取值赋给 command_name
    command_name = args[0]
    # 条件分支：command_name not in TASK_SESSION_COMMANDS
    if command_name not in TASK_SESSION_COMMANDS:
        return False  # 返回 False

    # subcommands ← 调用 ticket.get
    subcommands = ticket.get("subcommands")
    # 若条件不成立：not isinstance(subcommands, list)
    if not isinstance(subcommands, list):
        return False  # 返回 False

    # 遍历：subcommand in subcommands
    for subcommand in subcommands:
        # 若条件不成立：not isinstance(subcommand, dict)
        if not isinstance(subcommand, dict):
            continue  # 跳过本轮循环
        # 条件分支：_string_value(subcommand.get("name")) != …
        if _string_value(subcommand.get("name")) != command_name:
            continue  # 跳过本轮循环
        # 条件分支：command_name != "start"
        if command_name != "start":
            return True  # 返回 True
        # 按条件取值赋给 task_ref
        task_ref = args[1] if len(args) > 1 else None
        # 条件分支：_task_refs_match(_string_value(subcommand…
        if _task_refs_match(_string_value(subcommand.get("task_ref")), task_ref, repo_root):
            return True  # 返回 True

    return False  # 返回 False


# 定义函数 _ticket_is_fresh
def _ticket_is_fresh(ticket: dict[str, Any], ticket_path: Path, now: float) -> bool:
    # expires_at ← 调用 ticket.get
    expires_at = ticket.get("expires_at_epoch")
    # 条件分支：isinstance(expires_at, (int, float)) and …
    if isinstance(expires_at, (int, float)) and expires_at < now:
        # 调用 _remove_file
        _remove_file(ticket_path)
        return False  # 返回 False

    # created_at ← 调用 ticket.get
    created_at = ticket.get("created_at_epoch")
    # 条件分支：isinstance(created_at, (int, float))
    if isinstance(created_at, (int, float)):
        # 条件分支：now - created_at <= CURSOR_SHELL_TICKET_T…
        if now - created_at <= CURSOR_SHELL_TICKET_TTL_SECONDS:
            return True  # 返回 True
        # 调用 _remove_file
        _remove_file(ticket_path)
        return False  # 返回 False
    return True  # 返回 True


# 定义函数 _ticket_cwd_matches_repo
def _ticket_cwd_matches_repo(ticket: dict[str, Any], repo_root: Path) -> bool:
    # cwd ← 调用 _string_value
    cwd = _string_value(ticket.get("cwd"))
    # 若条件不成立：not cwd
    if not cwd:
        return True  # 返回 True
    # try：执行可能失败的逻辑
    try:
        # 调用 Path(cwd).resolve().relative_to
        Path(cwd).resolve().relative_to(repo_root)
    except ValueError:
        return False  # 返回 False
    return True  # 返回 True


# 定义函数 _matching_cursor_ticket_context_key
def _matching_cursor_ticket_context_key(
    ticket_path: Path,
    repo_root: Path,
    now: float,
) -> str | None:
    # ticket ← 调用 _read_json
    ticket = _read_json(ticket_path)
    # 若为 None：ticket is None or ticket.get("platform") …
    if ticket is None or ticket.get("platform") != "cursor":
        return None  # 返回 None
    # 若条件不成立：not _ticket_is_fresh(ticket, ticket_path, now)
    if not _ticket_is_fresh(ticket, ticket_path, now):
        return None  # 返回 None
    # 若条件不成立：not _ticket_cwd_matches_repo(ticket, repo_root)
    if not _ticket_cwd_matches_repo(ticket, repo_root):
        return None  # 返回 None
    # 若条件不成立：not _pending_ticket_matches_args(ticket, repo_root
    if not _pending_ticket_matches_args(ticket, repo_root):
        return None  # 返回 None
    # 返回 _string_value 的调用结果
    return _string_value(ticket.get("context_key"))


def _lookup_cursor_shell_ticket_context_key() -> str | None:
    """
    解析/解析出：Resolve Cursor conversation identity from a short-lived shell ticket.

    Cursor exposes `conversation_id` to `beforeShellExecution`, but does not
    export it into the shell command environment. The Cursor hook writes a
    short-lived ticket just before `task.py` runs. We accept a ticket only when
    the current `task.py` subcommand matches and exactly one fresh context key
    matches, which avoids cross-window pointer contamination.
    """
    # repo_root ← 调用 _find_repo_root_from_cwd
    repo_root = _find_repo_root_from_cwd()
    # 若为 None：repo_root is None
    if repo_root is None:
        return None  # 返回 None

    # ticket_dir ← 调用 _cursor_shell_ticket_dir
    ticket_dir = _cursor_shell_ticket_dir(repo_root)
    # 若条件不成立：not ticket_dir.is_dir()
    if not ticket_dir.is_dir():
        return None  # 返回 None

    # now ← 调用 time.time
    now = time.time()
    # candidates ← 调用 set
    candidates: set[str] = set()
    # 遍历：ticket_path in ticket_dir.glob("*.json")
    for ticket_path in ticket_dir.glob("*.json"):
        # context_key ← 调用 _matching_cursor_ticket_conte…
        context_key = _matching_cursor_ticket_context_key(ticket_path, repo_root, now)
        # 条件分支：context_key
        if context_key:
            # 加入集合或追加条目
            candidates.add(context_key)

    # 条件分支：len(candidates) == 1
    if len(candidates) == 1:
        # 返回 next 的调用结果
        return next(iter(candidates))
    return None  # 返回 None


def resolve_context_key(
    platform_input: dict[str, Any] | None = None,
    platform: str | None = None,
) -> str | None:
    """
    解析/解析出：Resolve a stable session/window context key, if one is available.

    `TRELLIS_CONTEXT_ID` is an explicit context-key override used by CLI
    scripts and subprocesses. It does not store the task itself.
    """
    # override ← 调用 _string_value
    override = _string_value(os.environ.get("TRELLIS_CONTEXT_ID"))
    # 条件分支：override
    if override:
        # 返回 _sanitize_key(override) or _hash_va…
        return _sanitize_key(override) or _hash_value(override)

    # data ← 调用 _as_dict
    data = _as_dict(platform_input)
    # 按条件取值赋给 platform_name
    platform_name = _detect_platform(data, platform) if data or platform else None

    # 条件分支：data
    if data:
        # session_id ← 调用 _lookup_string
        session_id = _lookup_string(data, _SESSION_KEYS)
        # 条件分支：session_id
        if session_id:
            # 返回 _context_key 的调用结果
            return _context_key(platform_name or "session", "session", session_id)

        # conversation_id ← 调用 _lookup_string
        conversation_id = _lookup_string(data, _CONVERSATION_KEYS)
        # 条件分支：conversation_id
        if conversation_id:
            # 返回 _context_key 的调用结果
            return _context_key(platform_name or "session", "conversation", conversation_id)

        # transcript_path ← 调用 _lookup_string
        transcript_path = _lookup_string(data, _TRANSCRIPT_KEYS)
        # 条件分支：transcript_path
        if transcript_path:
            # 返回 _context_key 的调用结果
            return _context_key(platform_name or "session", "transcript", transcript_path)

    # env_context_key ← 调用 _lookup_env_context_key
    env_context_key = _lookup_env_context_key(platform_name)
    # 条件分支：env_context_key
    if env_context_key:
        return env_context_key  # 返回 env_context_key

    # 条件分支：platform_name in (None, "session", "curso…
    if platform_name in (None, "session", "cursor"):
        # 返回 _lookup_cursor_shell_ticket… 的调用结果
        return _lookup_cursor_shell_ticket_context_key()
    return None  # 返回 None


# 定义函数 _read_json
def _read_json(path: Path) -> dict[str, Any] | None:
    # try：执行可能失败的逻辑
    try:
        # data ← 调用 json.loads
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None  # 返回 None
    # 按条件返回不同值
    return data if isinstance(data, dict) else None


# 定义函数 _write_json
def _write_json(path: Path, data: dict[str, Any]) -> bool:
    # try：执行可能失败的逻辑
    try:
        # 创建目录
        path.parent.mkdir(parents=True, exist_ok=True)
        # 写入文件
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return True  # 返回 True
    except OSError:
        return False  # 返回 False


# 定义函数 _canonical_task_ref
def _canonical_task_ref(task_path: str, repo_root: Path) -> str | None:
    # normalized ← 调用 normalize_task_ref
    normalized = normalize_task_ref(task_path)
    # 若条件不成立：not normalized
    if not normalized:
        return None  # 返回 None
    # full_path ← 调用 resolve_task_ref
    full_path = resolve_task_ref(normalized, repo_root)
    # 若为 None：full_path is None or not full_path.is_dir…
    if full_path is None or not full_path.is_dir():
        return None  # 返回 None
    # try：执行可能失败的逻辑
    try:
        # 返回 full_path.relative_to(repo_… 的调用结果
        return full_path.relative_to(repo_root).as_posix()
    except ValueError:
        # 返回 str 的调用结果
        return str(full_path)


# 定义函数 _active_from_ref
def _active_from_ref(
    task_ref: str | None,
    repo_root: Path,
    source_type: str,
    context_key: str | None = None,
) -> ActiveTask | None:
    # 若条件不成立：not task_ref
    if not task_ref:
        return None  # 返回 None
    # resolved ← 调用 resolve_task_ref
    resolved = resolve_task_ref(task_ref, repo_root)
    # 逻辑运算结果赋给 stale
    stale = resolved is None or not resolved.is_dir()
    # 返回 ActiveTask 的调用结果
    return ActiveTask(task_ref, source_type, context_key, stale)


# 定义函数 _context_path
def _context_path(repo_root: Path, context_key: str) -> Path:
    # 返回 _runtime_sessions_dir(repo_root) / …
    return _runtime_sessions_dir(repo_root) / f"{context_key}.json"


def resolve_active_task(
    repo_root: Path,
    platform_input: dict[str, Any] | None = None,
    platform: str | None = None,
) -> ActiveTask:
    """
    解析/解析出：Resolve the active task from session runtime state only.

    A stale session task is returned as stale. Missing context identity or a
    missing/empty session context falls back to single-session inference: if
    exactly one session file exists in the runtime, return its task with
    source_type="session-fallback" — covers class-2 platform sub-agents (codex,
    copilot, gemini, qoder) that don't inherit the parent's session id. ≥2
    files or 0 files yield ActiveTask(None) — refuses to guess across windows.
    """
    # context_key ← 调用 resolve_context_key
    context_key = resolve_context_key(platform_input, platform)
    # 条件分支：context_key
    if context_key:
        # 逻辑运算结果赋给 context
        context = _read_json(_context_path(repo_root, context_key)) or {}
        # task_ref ← 调用 _string_value
        task_ref = _string_value(context.get("current_task"))
        # active ← 调用 _active_from_ref
        active = _active_from_ref(task_ref, repo_root, "session", context_key)
        # 条件分支：active
        if active:
            return active  # 返回 active

    # fallback ← 调用 _resolve_single_session_fallb…
    fallback = _resolve_single_session_fallback(repo_root)
    # 若已有值：fallback is not None
    if fallback is not None:
        return fallback  # 返回 fallback

    # 返回 ActiveTask 的调用结果
    return ActiveTask(None, "none", context_key)


def _resolve_single_session_fallback(repo_root: Path) -> ActiveTask | None:
    """
    返回：Return the task pointed at by the sole session file, if exactly one exists.

    Used when context-key resolution fails (typical for class-2 platform
    sub-agents). Returns None if 0 or ≥2 session files are present — refuses
    to pick across windows so 04-21's multi-session isolation contract holds.
    """
    # sessions_dir ← 调用 _runtime_sessions_dir
    sessions_dir = _runtime_sessions_dir(repo_root)
    # 若条件不成立：not sessions_dir.is_dir()
    if not sessions_dir.is_dir():
        return None  # 返回 None

    # session_files ← 调用 sorted
    session_files = sorted(sessions_dir.glob("*.json"))
    # 条件分支：len(session_files) != 1
    if len(session_files) != 1:
        return None  # 返回 None

    # 按键/下标取值赋给 session_file
    session_file = session_files[0]
    # 逻辑运算结果赋给 context
    context = _read_json(session_file) or {}
    # task_ref ← 调用 _string_value
    task_ref = _string_value(context.get("current_task"))
    # 若条件不成立：not task_ref
    if not task_ref:
        return None  # 返回 None

    # 读取属性赋给 fallback_key
    fallback_key = session_file.stem
    # 返回 _active_from_ref 的调用结果
    return _active_from_ref(task_ref, repo_root, "session-fallback", fallback_key)


# 定义函数 _utc_now
def _utc_now() -> str:
    # 返回 datetime.now(timezone.utc).… 的调用结果
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# 定义函数 _context_metadata
def _context_metadata(
    platform_input: dict[str, Any] | None,
    platform: str | None,
    context_key: str | None = None,
) -> dict[str, Any]:
    # 逻辑运算结果赋给 data
    data = _as_dict(platform_input) or {}
    # platform_name ← 调用 _detect_platform
    platform_name = _detect_platform(data, platform)
    # 条件分支：platform_name == "session" and context_key
    if platform_name == "session" and context_key:
        # 按键/下标取值赋给 prefix
        prefix = context_key.split("_", 1)[0]
        # 条件分支：prefix in _KNOWN_PLATFORMS
        if prefix in _KNOWN_PLATFORMS:
            platform_name = prefix  # 将 prefix 赋给 platform_name
    # 赋值（含类型标注）：metadata
    metadata: dict[str, Any] = {
        "platform": platform_name,
        "last_seen_at": _utc_now(),
    }
    # 遍历：key in (*_SESSION_KEYS, *_CONVERSATION_KEYS, *_TRA
    for key in (*_SESSION_KEYS, *_CONVERSATION_KEYS, *_TRANSCRIPT_KEYS):
        # value ← 调用 _lookup_string
        value = _lookup_string(data, (key,))
        # 条件分支：value
        if value:
            metadata[key] = value  # 下标项 ← value
    return metadata  # 返回 metadata


def set_active_task(
    task_path: str,
    repo_root: Path,
    platform_input: dict[str, Any] | None = None,
    platform: str | None = None,
) -> ActiveTask | None:
    """
    设置：Set the active task in session scope.

    Returns None when no context key is available; callers should surface a
    user-facing error that explains how to provide session identity.
    """
    # canonical ← 调用 _canonical_task_ref
    canonical = _canonical_task_ref(task_path, repo_root)
    # 若为 None：canonical is None
    if canonical is None:
        return None  # 返回 None

    # context_key ← 调用 resolve_context_key
    context_key = resolve_context_key(platform_input, platform)
    # 若条件不成立：not context_key
    if not context_key:
        return None  # 返回 None

    # context_path ← 调用 _context_path
    context_path = _context_path(repo_root, context_key)
    # 逻辑运算结果赋给 context
    context = _read_json(context_path) or {}
    # 更新映射
    context.update(_context_metadata(platform_input, platform, context_key))
    context["current_task"] = canonical  # 下标项 ← canonical
    # 调用 context.setdefault
    context.setdefault("current_run", None)
    # 若条件不成立：not _write_json(context_path, context)
    if not _write_json(context_path, context):
        return None  # 返回 None
    # 返回 ActiveTask 的调用结果
    return ActiveTask(canonical, "session", context_key)


def clear_active_task(
    repo_root: Path,
    platform_input: dict[str, Any] | None = None,
    platform: str | None = None,
) -> ActiveTask:
    """清空/重置：Clear the active task by deleting the current session context file."""
    # context_key ← 调用 resolve_context_key
    context_key = resolve_context_key(platform_input, platform)
    # 若条件不成立：not context_key
    if not context_key:
        # 返回 ActiveTask 的调用结果
        return ActiveTask(None, "none")

    # previous ← 调用 resolve_active_task
    previous = resolve_active_task(repo_root, platform_input, platform)
    # context_path ← 调用 _context_path
    context_path = _context_path(repo_root, context_key)
    # 条件分支：context_path.is_file()
    if context_path.is_file():
        # 调用 _remove_file
        _remove_file(context_path)
    return previous  # 返回 previous


def clear_task_from_sessions(task_path: str, repo_root: Path) -> int:
    """移除：Delete all session runtime files that point at a task."""
    # 逻辑运算结果赋给 target
    target = _canonical_task_ref(task_path, repo_root) or normalize_task_ref(task_path)
    # 若条件不成立：not target
    if not target:
        return 0  # 返回 0

    # 初始化 cleared
    cleared = 0
    # sessions_dir ← 调用 _runtime_sessions_dir
    sessions_dir = _runtime_sessions_dir(repo_root)
    # 若条件不成立：not sessions_dir.is_dir()
    if not sessions_dir.is_dir():
        return cleared  # 返回 cleared

    # 遍历：session_path in sessions_dir.glob("*.json")
    for session_path in sessions_dir.glob("*.json"):
        # 逻辑运算结果赋给 context
        context = _read_json(session_path) or {}
        # current ← 调用 _string_value
        current = _string_value(context.get("current_task"))
        # 若条件不成立：not current
        if not current:
            continue  # 跳过本轮循环
        # 逻辑运算结果赋给 current_ref
        current_ref = _canonical_task_ref(current, repo_root) or normalize_task_ref(current)
        # 条件分支：current_ref != target
        if current_ref != target:
            continue  # 跳过本轮循环
        # 条件分支：session_path.is_file() and _remove_file(s…
        if session_path.is_file() and _remove_file(session_path):
            # 就地更新 cleared
            cleared += 1

    return cleared  # 返回 cleared


def get_current_task_source(
    repo_root: Path,
    platform_input: dict[str, Any] | None = None,
    platform: str | None = None,
) -> tuple[str, str | None, str | None]:
    """返回：Return (`source_type`, `context_key`, `task_path`) for compatibility."""
    # active ← 调用 resolve_active_task
    active = resolve_active_task(repo_root, platform_input, platform)
    return active.source_type, active.context_key, active.task_path  # 返回结果
