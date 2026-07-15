"""
Git 命令执行工具。

作为所有 Trellis 脚本运行 git 命令的单一入口（single source of truth）。
"""

# 启用延迟注解求值，便于类型提示互引
from __future__ import annotations

# 子进程执行与路径类型
import subprocess
from pathlib import Path


def run_git(args: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """执行一条 git 命令，返回 (returncode, stdout, stderr)。

    通过 ``-c i18n.logOutputEncoding=UTF-8`` 固定 UTF-8 输出，
    保证 Windows / macOS / Linux 行为一致。
    """
    try:  # 子进程执行 git，捕获异常
        # 在用户参数前注入 UTF-8 日志编码配置
        git_args = ["git", "-c", "i18n.logOutputEncoding=UTF-8"] + args
        # 捕获 stdout/stderr；文本模式并用 utf-8 解码
        result = subprocess.run(
            git_args,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        # 原样返回退出码与标准输出/错误
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        # 启动失败等异常：统一映射为 returncode=1、空 stdout、stderr 为异常信息
        return 1, "", str(e)
