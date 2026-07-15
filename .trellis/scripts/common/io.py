"""
JSON 文件读写工具。

提供 ``read_json`` / ``write_json``，作为所有 Trellis 脚本 JSON 文件操作的单一入口。
"""

# 启用延迟注解求值
from __future__ import annotations

# JSON 编解码、底层 fd、原子写临时文件、路径类型
import json
import os
import tempfile
from pathlib import Path


def read_json(path: Path) -> dict | None:
    """读取并解析 JSON 文件。

    文件不存在、非法 JSON 或无法读取时返回 None。
    """
    try:  # 读文件并解析 JSON
        # 以 UTF-8 读全文并反序列化
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        # 缺失/坏 JSON/IO 错误统一视为“无数据”
        return None


def write_json(path: Path, data: dict) -> bool:
    """将 dict 以美化格式写入 JSON 文件。

    写入是原子的：先写同目录临时文件，再 rename 覆盖目标。
    中途崩溃或 Ctrl-C 不会截断已有文件，避免 task.json 损坏导致任务从列表“消失”。

    成功返回 True，失败返回 False。
    """
    # 美化缩进、保留非 ASCII 字符
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    try:  # 原子写：先写临时文件
        # 在目标同目录创建临时文件，保证 os.replace 原子
        fd, tmp = tempfile.mkstemp(
            dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp"
        )
        try:  # 写入临时文件内容
            # 写入临时文件
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(payload)  # 把序列化后的 JSON 写入临时文件
            # 原子替换为目标路径
            os.replace(tmp, path)  # 原子替换到目标路径
        except BaseException:
            # 任意失败都尽量删除临时文件后继续抛出
            try:  # 可能失败的 IO 操作
                os.unlink(tmp)  # 失败时尽量删除残留临时文件
            except OSError:
                pass
            raise  # 清理后继续抛出原异常
        return True  # 成功
    except (OSError, IOError):
        return False  # 外层 IO 失败
