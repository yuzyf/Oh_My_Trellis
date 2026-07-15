"""
Trellis 工作流脚本的公共工具包。

本模块向其他 Trellis 脚本提供可复用能力；导入本包时会自动处理 Windows 控制台编码。
"""

# 用于在 Windows 上重配标准流编码
import io
import sys

# 说明：=============================================================================
# Windows 编码修复（必须靠前，在任何其它输出之前）
# 说明：=============================================================================
# 在 Windows 上，stdout 默认常为系统代码页（如 GBK/CP936）。
# 打印非 ASCII 时可能触发 UnicodeEncodeError。
#
# 任何从 common 导入的脚本都会自动获得该修复。
# 说明：=============================================================================


def _configure_stream(stream: object) -> object:
    """将流配置为 UTF-8 编码（主要用于 Windows）。"""
    # 优先 reconfigure()（Python 3.7+，更可靠）
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")  # 原地改为 UTF-8 # type: ignore[union-attr]
        return stream  # 返回已配置的原流
    # 回退：detach 后用 TextIOWrapper 重新包装
    elif hasattr(stream, "detach"):
        return io.TextIOWrapper(  # 新建 UTF-8 文本包装层
            stream.detach(),  # 剥离旧包装拿到底层 buffer # type: ignore[union-attr]
            encoding="utf-8",
            errors="replace",
        )
    return stream  # 无法配置则原样返回


# 仅在 Windows 上替换标准流
if sys.platform == "win32":
    sys.stdout = _configure_stream(sys.stdout)  # 标准输出 UTF-8 # type: ignore[assignment]
    sys.stderr = _configure_stream(sys.stderr)  # 标准错误 UTF-8 # type: ignore[assignment]
    sys.stdin = _configure_stream(sys.stdin)  # 标准输入 UTF-8 # type: ignore[assignment]


def configure_encoding() -> None:
    """配置 stdout/stderr/stdin 为 UTF-8（Windows）。

    从 common 导入时已自动调用；不导入 common 的脚本可手动调用。
    可重复调用，保持幂等。
    """
    global sys  # 显式使用模块级 sys
    if sys.platform == "win32":  # 仅 Windows 需要重配控制台编码
        sys.stdout = _configure_stream(sys.stdout)  # 标准输出 UTF-8 # type: ignore[assignment]
        sys.stderr = _configure_stream(sys.stderr)  # 标准错误 UTF-8 # type: ignore[assignment]
        sys.stdin = _configure_stream(sys.stdin)  # 标准输入 UTF-8 # type: ignore[assignment]


# 再导出路径相关常量与函数，方便 `from common import ...`
from .paths import (
    DIR_WORKFLOW,
    DIR_WORKSPACE,
    DIR_TASKS,
    DIR_ARCHIVE,
    DIR_SPEC,
    DIR_SCRIPTS,
    FILE_DEVELOPER,
    FILE_CURRENT_TASK,
    FILE_TASK_JSON,
    FILE_JOURNAL_PREFIX,
    get_repo_root,
    get_developer,
    check_developer,
    get_tasks_dir,
    get_workspace_dir,
    get_active_journal_file,
    count_lines,
    get_current_task,
    get_current_task_abs,
    normalize_task_ref,
    resolve_task_ref,
    set_current_task,
    clear_current_task,
    has_current_task,
    generate_task_date_prefix,
)

# 再导出活跃任务解析 API
from .active_task import (
    ActiveTask,
    clear_active_task,
    resolve_active_task,
    resolve_context_key,
    set_active_task,
)
