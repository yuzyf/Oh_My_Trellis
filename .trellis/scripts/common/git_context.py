#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
git_context 模块：Git and Session Context utilities.

Entry shim — delegates to session_context and packages_context.


提供:
output_json - Output context in JSON format
output_text - Output context in text format
"""

# 启用延迟注解求值等 future 特性
from __future__ import annotations

# 导入依赖
import json

from .git import run_git
from .session_context import (
    get_context_json,
    get_context_text,
    get_context_record_json,
    get_context_text_record,
    output_json,
    output_text,
)
from .packages_context import (
    get_context_packages_text,
    get_context_packages_json,
)
from .trellis_config import read_trellis_config
from .workflow_phase import (
    filter_platform,
    get_phase_index,
    get_step,
    resolve_effective_platform,
)

# 向后兼容别名——外部模块导入此名
_run_git_command = run_git


# 说明：=============================================================================
# 主入口
# 说明：=============================================================================

def main() -> None:
    """入口：CLI entry point."""
    # 局部导入 argparse
    import argparse

    # parser ← 调用 argparse.ArgumentParser
    parser = argparse.ArgumentParser(description="Get Session Context for AI Agent")
    # 注册 CLI 参数/子命令
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Output in JSON format (works with any --mode)",
    )
    # 注册 CLI 参数/子命令
    parser.add_argument(
        "--mode",
        "-m",
        choices=["default", "record", "packages", "phase"],
        default="default",
        help="Output mode: default (full context), record (for record-session), packages (package info only), phase (workflow step extraction)",
    )
    # 注册 CLI 参数/子命令
    parser.add_argument(
        "--step",
        help="Step id for --mode phase, e.g. 1.1, 2.2. Omit to get the Phase Index.",
    )
    # 注册 CLI 参数/子命令
    parser.add_argument(
        "--platform",
        help="Platform name for --mode phase, e.g. cursor, claude-code. Filters platform-tagged blocks.",
    )

    # args ← 调用 parser.parse_args
    args = parser.parse_args()

    # 条件分支：args.mode == "record"
    if args.mode == "record":
        # 条件分支：args.json
        if args.json:
            # 输出信息
            print(json.dumps(get_context_record_json(), indent=2, ensure_ascii=False))
        else:
            # 输出信息
            print(get_context_text_record())
    # 条件分支：args.mode == "packages"
    elif args.mode == "packages":
        # 条件分支：args.json
        if args.json:
            # 输出信息
            print(json.dumps(get_context_packages_json(), indent=2, ensure_ascii=False))
        else:
            # 输出信息
            print(get_context_packages_text())
    # 条件分支：args.mode == "phase"
    elif args.mode == "phase":
        # 按条件取值赋给 content
        content = get_step(args.step) if args.step else get_phase_index()
        # 若条件不成立：not content.strip()
        if not content.strip():
            # 条件分支：args.step
            if args.step:
                # 结束进程/解析：parser.exit
                parser.exit(2, f"Step not found: {args.step}\n")
            else:
                # 结束进程/解析：parser.exit
                parser.exit(2, "Phase Index section not found in workflow.md\n")
        # 条件分支：args.platform
        if args.platform:
            # effective ← 调用 resolve_effective_platform
            effective = resolve_effective_platform(
                args.platform, read_trellis_config()
            )
            # content ← 调用 filter_platform
            content = filter_platform(content, effective)
        # 输出信息
        print(content, end="")
    else:
        # 条件分支：args.json
        if args.json:
            # 调用 output_json
            output_json()
        else:
            # 调用 output_text
            output_text()


# 条件分支：__name__ == "__main__"
# 直接运行本文件时进入入口
if __name__ == "__main__":
    # 调用 main
    main()
