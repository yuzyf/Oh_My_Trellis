#!/usr/bin/env python3
"""
获取会话上下文（session context），供 AI Agent 使用。

用法:
    python3 get_context.py           以文本格式输出上下文
    python3 get_context.py --json    以 JSON 格式输出上下文
"""

# 启用延迟注解求值
from __future__ import annotations

# 实际逻辑在 common.git_context.main，本文件仅为薄入口
from common.git_context import main


# 作为脚本直接运行时调用入口
if __name__ == "__main__":
    main()  # 委托给 git_context 的 main
