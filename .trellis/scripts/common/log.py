"""
终端输出工具：颜色与结构化日志。

``Colors`` 与 ``log_*`` 函数的单一来源，供所有 Trellis 脚本复用。
"""

# 启用延迟注解求值
from __future__ import annotations


class Colors:
    """终端 ANSI 颜色码常量。"""

    RED = "\033[0;31m"  # 红色（错误）
    GREEN = "\033[0;32m"  # 绿色（成功）
    YELLOW = "\033[1;33m"  # 黄色（警告）
    BLUE = "\033[0;34m"  # 蓝色（信息）
    CYAN = "\033[0;36m"  # 青色
    DIM = "\033[2m"  # 暗色/弱化显示
    NC = "\033[0m"  # 复位（No Color）


def colored(text: str, color: str) -> str:
    """给文本套上 ANSI 颜色，并在末尾复位。"""
    return f"{color}{text}{Colors.NC}"  # 颜色 + 正文 + 复位


def log_info(msg: str) -> None:
    """打印带 [INFO] 前缀的信息级日志。"""
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {msg}")  # 蓝色 INFO


def log_success(msg: str) -> None:
    """打印带 [SUCCESS] 前缀的成功日志。"""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {msg}")  # 绿色 SUCCESS


def log_warn(msg: str) -> None:
    """打印带 [WARN] 前缀的警告日志。"""
    print(f"{Colors.YELLOW}[WARN]{Colors.NC} {msg}")  # 黄色 WARN


def log_error(msg: str) -> None:
    """打印带 [ERROR] 前缀的错误日志。"""
    print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}")  # 红色 ERROR
