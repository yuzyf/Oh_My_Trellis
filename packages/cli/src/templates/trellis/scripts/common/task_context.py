#!/usr/bin/env python3
"""
task_context 模块：Task JSONL context management.


提供:
cmd_add_context   - Add entry to JSONL context file
cmd_validate      - Validate JSONL context files
cmd_list_context  - List JSONL context entries


说明:
``cmd_init_context`` was removed in v0.5.0-beta.12. JSONL context files
are now seeded at ``task.py create`` time with a self-describing
``_example`` line; the AI agent curates real entries during planning when
the task needs sub-agent/spec context. See ``.trellis/workflow.md`` for the
current planning artifact contract.
"""

# 启用延迟注解求值等 future 特性
from __future__ import annotations

# 导入依赖
import argparse
import json
from pathlib import Path

from .log import Colors, colored
from .paths import get_repo_root
from .task_utils import resolve_task_dir


# 说明：=============================================================================
# 命令：add-context
# 说明：=============================================================================

def cmd_add_context(args: argparse.Namespace) -> int:
    """添加：Add entry to JSONL context file."""
    # repo_root ← 调用 get_repo_root
    repo_root = get_repo_root()
    # target_dir ← 调用 resolve_task_dir
    target_dir = resolve_task_dir(args.dir, repo_root)

    # 读取属性赋给 jsonl_name
    jsonl_name = args.file
    # 读取属性赋给 path
    path = args.path
    # 逻辑运算结果赋给 reason
    reason = args.reason or "Added manually"

    # 若条件不成立：not target_dir.is_dir()
    if not target_dir.is_dir():
        # 输出信息
        print(colored(f"Error: Directory not found: {target_dir}", Colors.RED))
        # 返回常量 1
        return 1

    # 支持简写
    if not jsonl_name.endswith(".jsonl"):
        # 拼出字符串赋给 jsonl_name
        jsonl_name = f"{jsonl_name}.jsonl"

    # 计算后赋给 jsonl_file
    jsonl_file = target_dir / jsonl_name
    # 计算后赋给 full_path
    full_path = repo_root / path

    # 初始化 entry_type
    entry_type = "file"
    # 条件分支：full_path.is_dir()
    if full_path.is_dir():
        # 初始化 entry_type
        entry_type = "directory"
        # 若条件不成立：not path.endswith("/")
        if not path.endswith("/"):
            # 拼出字符串赋给 path
            path = f"{path}/"
    # 条件分支：elif not full_path.is_file()
    elif not full_path.is_file():
        # 输出信息
        print(colored(f"Error: Path not found: {path}", Colors.RED))
        # 返回常量 1
        return 1

    # 检查是否已存在
    # 条件分支：jsonl_file.is_file()
    if jsonl_file.is_file():
        # content ← 调用 jsonl_file.read_text
        content = jsonl_file.read_text(encoding="utf-8")
        # 条件分支：f'"{path}"' in content
        if f'"{path}"' in content:
            # 输出信息
            print(colored(f"Warning: Entry already exists for {path}", Colors.YELLOW))
            return 0  # 返回 0

    # 添加条目
    # 声明带类型标注的字段/变量：entry
    entry: dict
    # 条件分支：entry_type == "directory"
    if entry_type == "directory":
        # 构造字典赋给 entry
        entry = {"file": path, "type": "directory", "reason": reason}
    else:
        # 构造字典赋给 entry
        entry = {"file": path, "reason": reason}

    # with 上下文：jsonl_file.open("a", …
    with jsonl_file.open("a", encoding="utf-8") as f:
        # 输出信息
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # 输出信息
    print(colored(f"Added {entry_type}: {path}", Colors.GREEN))
    return 0  # 返回 0


# 说明：=============================================================================
# 命令：validate
# 说明：=============================================================================

def cmd_validate(args: argparse.Namespace) -> int:
    """检查/校验：Validate JSONL context files."""
    # repo_root ← 调用 get_repo_root
    repo_root = get_repo_root()
    # target_dir ← 调用 resolve_task_dir
    target_dir = resolve_task_dir(args.dir, repo_root)

    # 若条件不成立：not target_dir.is_dir()
    if not target_dir.is_dir():
        # 输出信息
        print(colored("Error: task directory required", Colors.RED))
        # 返回常量 1
        return 1

    # 输出信息
    print(colored("=== Validating Context Files ===", Colors.BLUE))
    # 输出信息
    print(f"Target dir: {target_dir}")
    # 输出信息
    print()

    # 初始化 total_errors
    total_errors = 0
    # 遍历：jsonl_name in ["implement.jsonl", "check.jsonl"]
    for jsonl_name in ["implement.jsonl", "check.jsonl"]:
        # 计算后赋给 jsonl_file
        jsonl_file = target_dir / jsonl_name
        # errors ← 调用 _validate_jsonl
        errors = _validate_jsonl(jsonl_file, repo_root)
        # 就地更新 total_errors
        total_errors += errors

    # 输出信息
    print()
    # 条件分支：total_errors == 0
    if total_errors == 0:
        # 输出信息
        print(colored("✓ All validations passed", Colors.GREEN))
        return 0  # 返回 0
    else:
        # 输出信息
        print(colored(f"✗ Validation failed ({total_errors} errors)", Colors.RED))
        # 返回常量 1
        return 1


def _validate_jsonl(jsonl_file: Path, repo_root: Path) -> int:
    """
    检查/校验：Validate a single JSONL file.

    Seed rows (no ``file`` field — typically ``{"_example": "..."}``) are
    skipped silently; they are self-describing comments, not real entries.
    """
    # 读取属性赋给 file_name
    file_name = jsonl_file.name
    # 初始化 errors
    errors = 0

    # 若条件不成立：not jsonl_file.is_file()
    if not jsonl_file.is_file():
        # 输出信息
        print(f"  {colored(f'{file_name}: not found (skipped)', Colors.YELLOW)}")
        return 0  # 返回 0

    # 初始化 line_num
    line_num = 0
    # 初始化 real_entries
    real_entries = 0
    # 遍历：line in jsonl_file.read_text(encoding="utf-8").spl
    for line in jsonl_file.read_text(encoding="utf-8").splitlines():
        # 就地更新 line_num
        line_num += 1
        # 若条件不成立：not line.strip()
        if not line.strip():
            continue  # 跳过本轮循环

        # try：执行可能失败的逻辑
        try:
            # data ← 调用 json.loads
            data = json.loads(line)
        except json.JSONDecodeError:
            # 输出信息
            print(f"  {colored(f'{file_name}:{line_num}: Invalid JSON', Colors.RED)}")
            # 就地更新 errors
            errors += 1
            continue  # 跳过本轮循环

        # file_path ← 调用 data.get
        file_path = data.get("file")
        # entry_type ← 调用 data.get
        entry_type = data.get("type", "file")

        # 若条件不成立：not file_path
        if not file_path:
            # 种子行/注释行——静默跳过
            continue

        # 就地更新 real_entries
        real_entries += 1
        # 计算后赋给 full_path
        full_path = repo_root / file_path
        # 条件分支：entry_type == "directory"
        if entry_type == "directory":
            # 若条件不成立：not full_path.is_dir()
            if not full_path.is_dir():
                # 输出信息
                print(f"  {colored(f'{file_name}:{line_num}: Directory not found: {file_path}', Colors.RED)}")
                # 就地更新 errors
                errors += 1
        else:
            # 若条件不成立：not full_path.is_file()
            if not full_path.is_file():
                # 输出信息
                print(f"  {colored(f'{file_name}:{line_num}: File not found: {file_path}', Colors.RED)}")
                # 就地更新 errors
                errors += 1

    # 条件分支：errors == 0
    if errors == 0:
        # 输出信息
        print(f"  {colored(f'{file_name}: ✓ ({real_entries} entries)', Colors.GREEN)}")
    else:
        # 输出信息
        print(f"  {colored(f'{file_name}: ✗ ({errors} errors)', Colors.RED)}")

    return errors  # 返回 errors


# 说明：=============================================================================
# 命令：list-context
# 说明：=============================================================================

def cmd_list_context(args: argparse.Namespace) -> int:
    """列出/遍历：List JSONL context entries."""
    # repo_root ← 调用 get_repo_root
    repo_root = get_repo_root()
    # target_dir ← 调用 resolve_task_dir
    target_dir = resolve_task_dir(args.dir, repo_root)

    # 若条件不成立：not target_dir.is_dir()
    if not target_dir.is_dir():
        # 输出信息
        print(colored("Error: task directory required", Colors.RED))
        # 返回常量 1
        return 1

    # 输出信息
    print(colored("=== Context Files ===", Colors.BLUE))
    # 输出信息
    print()

    # 遍历：jsonl_name in ["implement.jsonl", "check.jsonl"]
    for jsonl_name in ["implement.jsonl", "check.jsonl"]:
        # 计算后赋给 jsonl_file
        jsonl_file = target_dir / jsonl_name
        # 若条件不成立：not jsonl_file.is_file()
        if not jsonl_file.is_file():
            continue  # 跳过本轮循环

        # 输出信息
        print(colored(f"[{jsonl_name}]", Colors.CYAN))

        # 初始化 count
        count = 0
        # 初始化 seed_only
        seed_only = True
        # 遍历：line in jsonl_file.read_text(encoding="utf-8").spl
        for line in jsonl_file.read_text(encoding="utf-8").splitlines():
            # 若条件不成立：not line.strip()
            if not line.strip():
                continue  # 跳过本轮循环

            # try：执行可能失败的逻辑
            try:
                # data ← 调用 json.loads
                data = json.loads(line)
            except json.JSONDecodeError:
                continue  # 跳过本轮循环

            # file_path ← 调用 data.get
            file_path = data.get("file")
            # 若条件不成立：not file_path
            if not file_path:
                # 种子行/注释行——不计入真实条目
                continue
            # 初始化 seed_only
            seed_only = False

            # 就地更新 count
            count += 1
            # entry_type ← 调用 data.get
            entry_type = data.get("type", "file")
            # reason ← 调用 data.get
            reason = data.get("reason", "-")

            # 条件分支：entry_type == "directory"
            if entry_type == "directory":
                # 输出信息
                print(f"  {colored(f'{count}.', Colors.GREEN)} [DIR] {file_path}")
            else:
                # 输出信息
                print(f"  {colored(f'{count}.', Colors.GREEN)} {file_path}")
            # 输出信息
            print(f"     {colored('→', Colors.YELLOW)} {reason}")

        # 条件分支：seed_only
        if seed_only:
            # 输出信息
            print(f"  {colored('(no curated entries yet — only seed row)', Colors.YELLOW)}")

        # 输出信息
        print()

    return 0  # 返回 0
