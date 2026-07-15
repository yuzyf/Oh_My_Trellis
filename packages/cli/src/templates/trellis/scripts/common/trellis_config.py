#!/usr/bin/env python3
"""
trellis_config 模块：Standalone reader for .trellis/config.yaml.

Mirrors a minimal subset of common.config so callers (hooks, workflow_phase)
can read configuration without importing the full task/repo helpers. Returns
an empty dict on missing/malformed files so callers stay simple.
"""

# 启用延迟注解求值等 future 特性
from __future__ import annotations

# 导入依赖
from pathlib import Path
from typing import Optional


# 初始化 CONFIG_REL_PATH
CONFIG_REL_PATH = ".trellis/config.yaml"


# 定义函数 _unquote
def _unquote(value: str) -> str:
    # 条件分支：len(value) >= 2 and value[0] == value[-1]…
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        # 返回下标/键取值 value[1:-1]
        return value[1:-1]
    return value  # 返回 value


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


# 定义函数 _next_content_line
def _next_content_line(lines: list[str], start: int) -> tuple[int, str]:
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


# 定义函数 _parse_yaml_block
def _parse_yaml_block(
    lines: list[str], start: int, min_indent: int, target: dict
) -> int:
    i = start  # 将 start 赋给 i
    # current_list 置为 None（带类型）
    current_list: list | None = None

    # while 循环：i < len(lines)
    while i < len(lines):
        # 按键/下标取值赋给 line
        line = lines[i]
        # stripped ← 调用 line.strip
        stripped = line.strip()

        # 若条件不成立：not stripped or stripped.startswith("#")
        if not stripped or stripped.startswith("#"):
            # 就地更新 i
            i += 1
            continue  # 跳过本轮循环

        # 计算后赋给 indent
        indent = len(line) - len(line.lstrip())
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
                target[key] = value  # 下标项 ← value
                # 就地更新 i
                i += 1
            else:
                # next_i, next_line ← 调用 _next_content_line
                next_i, next_line = _next_content_line(lines, i + 1)
                # 条件分支：next_i >= len(lines)
                if next_i >= len(lines):
                    # target[key] 初始化为空字典
                    target[key] = {}
                    i = next_i  # 将 next_i 赋给 i
                # 条件分支：next_line.strip().startswith("- ")
                elif next_line.strip().startswith("- "):
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
                        # 赋值（含类型标注）：nested
                        nested: dict = {}
                        target[key] = nested  # 下标项 ← nested
                        # i ← 调用 _parse_yaml_block
                        i = _parse_yaml_block(lines, i + 1, next_indent, nested)
                    else:
                        # target[key] 初始化为空字典
                        target[key] = {}
                        # 就地更新 i
                        i += 1
        else:
            # 就地更新 i
            i += 1

    return i  # 返回 i


def parse_simple_yaml(content: str) -> dict:
    """解析：Parse a small subset of YAML. See common.config for full doc."""
    # lines ← 调用 content.splitlines
    lines = content.splitlines()
    # 赋值（含类型标注）：result
    result: dict = {}
    # 调用 _parse_yaml_block
    _parse_yaml_block(lines, 0, 0, result)
    return result  # 返回 result


def read_trellis_config(repo_root: Optional[Path] = None) -> dict:
    """加载/读取：Read .trellis/config.yaml. Returns {} on missing or malformed file."""
    # 逻辑运算结果赋给 root
    root = repo_root or Path.cwd()
    # 计算后赋给 config_file
    config_file = root / CONFIG_REL_PATH
    # try：执行可能失败的逻辑
    try:
        # content ← 调用 config_file.read_text
        content = config_file.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return {}  # 返回字典结果
    # try：执行可能失败的逻辑
    try:
        # parsed ← 调用 parse_simple_yaml
        parsed = parse_simple_yaml(content)
    except Exception:
        return {}  # 返回字典结果
    # 按条件返回不同值
    return parsed if isinstance(parsed, dict) else {}
