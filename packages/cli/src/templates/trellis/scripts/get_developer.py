#!/usr/bin/env python3
"""
获取当前开发者（developer）名称。

本脚本是薄封装，底层通过 ``common/paths.py`` 读取开发者信息。
"""

# 启用延迟注解求值
from __future__ import annotations

# 标准库：退出码与标准错误输出
import sys

# 从路径工具读取已初始化的开发者名
from common.paths import get_developer


def main() -> None:
    """命令行入口：打印开发者名；未初始化则报错退出。"""
    developer = get_developer()  # 读取当前 developer 配置
    # 条件分支：developer
    if developer:
        print(developer)  # 已初始化：输出名称到 stdout
    else:
        # 未初始化：错误信息走 stderr，进程以非 0 退出
        print("Developer not initialized", file=sys.stderr)
        sys.exit(1)  # 未初始化则失败退出


# 直接执行本文件时进入 CLI
if __name__ == "__main__":
    main()  # 启动 CLI 入口
