#!/usr/bin/env python3
"""
初始化工作流中的开发者（developer）。

用法:
    python3 init_developer.py <developer-name>

会创建:
    - ``.trellis/.developer`` 文件（开发者信息）
    - ``.trellis/workspace/<name>/`` 目录结构
"""

# 启用延迟注解求值；标准库与 common 依赖见下方 import 块
from __future__ import annotations

import sys  # 读取 argv 与设置进程退出码

from common.paths import (  # 工作流路径常量与读取已有 developer
    DIR_WORKFLOW,  # .trellis 目录名
    FILE_DEVELOPER,  # developer 标记文件名
    get_developer,  # 读取当前 developer
)
from common.developer import init_developer  # 实际初始化逻辑


def main() -> None:
    """命令行入口：校验参数后初始化 developer。"""
    # 缺少名称参数时打印用法（英文 runtime 文案）并以 1 退出
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <developer-name>")  # 用法行
        print()  # 空行分隔
        print("Example:")  # 示例标题
        print(f"  {sys.argv[0]} john")  # 示例命令
        sys.exit(1)  # 参数错误退出

    name = sys.argv[1]  # 开发者名称（位置参数）

    # 若已初始化则提示如何重建，并以 0 退出（视为已完成，非错误）
    existing = get_developer()  # 读取现有 developer 名
    # 条件分支：existing
    if existing:
        print(f"Developer already initialized: {existing}")  # 已存在提示
        print()  # 空行
        print(f"To reinitialize, remove {DIR_WORKFLOW}/{FILE_DEVELOPER} first")  # 重建指引
        sys.exit(0)  # 正常退出

    # 调用公共初始化；成功/失败映射为进程退出码
    if init_developer(name):
        sys.exit(0)  # 初始化成功
    else:
        sys.exit(1)  # 初始化失败


# 直接运行本脚本时进入 main
if __name__ == "__main__":
    main()  # 启动 CLI 入口
