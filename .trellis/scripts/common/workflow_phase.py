#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
workflow_phase 模块：Workflow Phase Extraction.

Extracts step-level content from .trellis/workflow.md and optionally filters
platform-specific blocks.

Platform marker syntax in workflow.md:

[Claude Code, Cursor, ...]
agent-capable content
[/Claude Code, Cursor, ...]


提供:
get_phase_index   - Extract the Phase Index section (no --step)
get_step          - Extract a single step (#### X.X) section
filter_platform   - Strip platform blocks that don't include the given name
"""

# 启用延迟注解求值等 future 特性
from __future__ import annotations

# 导入依赖
import re

from .paths import DIR_WORKFLOW, get_repo_root


# 定义函数 _workflow_md_path
def _workflow_md_path():
    # 返回 get_repo_root() / DIR_WORKFLOW / "w…
    return get_repo_root() / DIR_WORKFLOW / "workflow.md"

# 匹配本身就是平台标记的行："[A, B, C]" 或 "[/A, B, C]"
# _MARKER_RE ← 调用 re.compile
_MARKER_RE = re.compile(r"^\[(/?)([A-Za-z][^\[\]]*)\]\s*$")

# 步骤标题："#### 1.0 Title" 或 "#### 1.0 ..."
# _STEP_HEADING_RE ← 调用 re.compile
_STEP_HEADING_RE = re.compile(r"^####\s+(\d+\.\d+)\b.*$")

# Phase Index 由此开始；随后是 Phase 1/2/3 步骤正文；到 Breadcrumbs 结束。
# 初始化 _PHASE_INDEX_HEADING
_PHASE_INDEX_HEADING = "## Phase Index"


# 定义函数 _read_workflow
def _read_workflow() -> str:
    # path ← 调用 _workflow_md_path
    path = _workflow_md_path()
    # 若条件不成立：not path.exists()
    if not path.exists():
        # 抛出异常：FileNotFoundError(f"workflow.md not…
        raise FileNotFoundError(f"workflow.md not found: {path}")
    # 返回 path.read_text 的调用结果
    return path.read_text(encoding="utf-8")


def _parse_marker(line: str) -> tuple[bool, list[str]] | None:
    """
    解析：Parse a platform marker line.


    返回:
        (is_closing, [platform_names]) if line is a marker, else None.
    """
    # m ← 调用 _MARKER_RE.match
    m = _MARKER_RE.match(line)
    # 若条件不成立：not m
    if not m:
        return None  # 返回 None
    is_closing = m.group(1) == "/"  # 设置 is_closing
    # 用推导式生成 names
    names = [p.strip() for p in m.group(2).split(",") if p.strip()]
    return is_closing, names  # 返回结果


def get_phase_index() -> str:
    """
    返回：Return the compact Phase Index summary from workflow.md.

    SessionStart and no-step phase context use this small summary as their
    orientation payload. Detailed Phase 1/2/3 instructions are loaded with
    ``get_step`` on demand. ``[workflow-state:STATUS]`` tag blocks are
    consumed by the per-turn hook, so they're stripped from this output.
    """
    # text ← 调用 _read_workflow
    text = _read_workflow()
    # lines ← 调用 text.splitlines
    lines = text.splitlines()

    # start 置为 None（带类型）
    start: int | None = None
    # end 置为 None（带类型）
    end: int | None = None
    # 遍历：i, line in enumerate(lines)
    for i, line in enumerate(lines):
        # stripped ← 调用 line.strip
        stripped = line.strip()
        # 若为 None：start is None and stripped == _PHASE_INDE…
        if start is None and stripped == _PHASE_INDEX_HEADING:
            start = i  # 将 i 赋给 start
            continue  # 跳过本轮循环
        # 若已有值：start is not None and stripped == "## Phase 1: Pla
        if start is not None and stripped == "## Phase 1: Plan":
            end = i  # 将 i 赋给 end
            # 跳出循环
            break

    # 若为 None：start is None
    if start is None:
        return ""  # 返回空字符串
    # 若为 None：end is None
    if end is None:
        # end ← 调用 len
        end = len(lines)

    # section ← 调用 "\n".join(lines[start:end]).r…
    section = "\n".join(lines[start:end]).rstrip()
    # 剥离 [workflow-state:STATUS]...[/workflow-state:STATUS] 块，因为
    # 它们由 inject-workflow-state.py 按轮次单独注入。
    # 局部导入 re
    import re as _re
    # tag_re ← 调用 _re.compile
    tag_re = _re.compile(
        r"\[workflow-state:([A-Za-z0-9_-]+)\]\s*\n.*?\n\s*\[/workflow-state:\1\]\n?",
        _re.DOTALL,
    )
    # 返回 tag_re.sub("", section).rstrip() + …
    return tag_re.sub("", section).rstrip() + "\n"


def get_step(step_id: str) -> str:
    """
    返回：Return the `#### X.X` section matching step_id (header + body).

    Body ends at the next `####` or `---` or `##` heading (whichever comes first).
    """
    # text ← 调用 _read_workflow
    text = _read_workflow()
    # lines ← 调用 text.splitlines
    lines = text.splitlines()

    # start 置为 None（带类型）
    start: int | None = None
    # 遍历：i, line in enumerate(lines)
    for i, line in enumerate(lines):
        # m ← 调用 _STEP_HEADING_RE.match
        m = _STEP_HEADING_RE.match(line)
        # 条件分支：m and m.group(1) == step_id
        if m and m.group(1) == step_id:
            start = i  # 将 i 赋给 start
            # 跳出循环
            break
    # 若为 None：start is None
    if start is None:
        return ""  # 返回空字符串

    # end ← 调用 len
    end: int = len(lines)
    # 遍历：j in range(start + 1, len(lines))
    for j in range(start + 1, len(lines)):
        # 按键/下标取值赋给 line
        line = lines[j]
        # 条件分支：line.startswith("#### ")
        if line.startswith("#### "):
            end = j  # 将 j 赋给 end
            # 跳出循环
            break
        # 条件分支：line.startswith("## ")
        if line.startswith("## "):
            end = j  # 将 j 赋给 end
            # 跳出循环
            break
        # 位于第 0 列的水平分隔线
        # 条件分支：line.strip() == "---"
        if line.strip() == "---":
            end = j  # 将 j 赋给 end
            # 跳出循环
            break

    return "\n".join(lines[start:end]).rstrip() + "\n"  # 返回计算结果


def _platform_matches(platform: str, block_names: list[str]) -> bool:
    """大小写不敏感的模糊匹配：接受 cursor / Cursor / CURSOR 等形式。"""
    # needle ← 调用 platform.lower().replace("-",…
    needle = platform.lower().replace("-", "").replace("_", "").replace(" ", "")
    # 遍历：name in block_names
    for name in block_names:
        # hay ← 调用 name.lower().replace("-", "")…
        hay = name.lower().replace("-", "").replace("_", "").replace(" ", "")
        # 条件分支：needle == hay
        if needle == hay:
            return True  # 返回 True
    return False  # 返回 False


def resolve_effective_platform(platform: str, config: dict) -> str:
    """
    映射：Map ``codex`` to a dispatch-mode-namespaced virtual platform name.

    When ``--platform codex`` is passed, return ``"codex-inline"`` (default)
    or ``"codex-sub-agent"`` based on ``.trellis/config.yaml`` ``codex.dispatch_mode``.
    ``filter_platform`` then surfaces blocks whose marker lists include the
    namespaced name (e.g. ``[codex-sub-agent, ...]`` or ``[codex-inline, Kilo,
    Antigravity, Devin]``).

    Default is ``inline`` because Codex sub-agents run with ``fork_turns="none"``
    isolation and can't inherit the parent session's task context — inline
    keeps the main agent in charge so context isn't lost. Invalid / missing
    values also fall back to inline.

    Other platforms are returned unchanged.
    """
    # 条件分支：platform == "codex"
    if platform == "codex":
        # 初始化 mode
        mode = "inline"
        # 按条件取值赋给 codex_cfg
        codex_cfg = config.get("codex") if isinstance(config, dict) else None
        # 条件分支：isinstance(codex_cfg, dict)
        if isinstance(codex_cfg, dict):
            # cfg_mode ← 调用 codex_cfg.get
            cfg_mode = codex_cfg.get("dispatch_mode")
            # 条件分支：cfg_mode in ("inline", "sub-agent")
            if cfg_mode in ("inline", "sub-agent"):
                mode = cfg_mode  # 将 cfg_mode 赋给 mode
        return f"codex-{mode}"  # 返回格式化字符串
    return platform  # 返回 platform


def filter_platform(content: str, platform: str) -> str:
    """保留不在任何 `[...]` 块内的行，以及属于当前平台块内的行。"""
    # lines ← 调用 content.splitlines
    lines = content.splitlines()
    # 赋值（含类型标注）：out
    out: list[str] = []

    # 初始化 in_block
    in_block = False
    # 初始化 keep_block
    keep_block = False

    # 遍历：line in lines
    for line in lines:
        # marker ← 调用 _parse_marker
        marker = _parse_marker(line)
        # 若已有值：marker is not None
        if marker is not None:
            is_closing, names = marker  # 元组解包 ← marker
            # 若条件不成立：not is_closing
            if not is_closing:
                # 初始化 in_block
                in_block = True
                # keep_block ← 调用 _platform_matches
                keep_block = _platform_matches(platform, names)
            else:
                # 初始化 in_block
                in_block = False
                # 初始化 keep_block
                keep_block = False
            continue  # 丢弃标记行本身

        # 条件分支：in_block
        if in_block:
            # 条件分支：keep_block
            if keep_block:
                # 追加到列表
                out.append(line)
            continue  # 跳过本轮循环
        # 追加到列表
        out.append(line)

    # 折叠因丢弃标记可能产生的连续 3 行以上空行
    # 赋值（含类型标注）：collapsed
    collapsed: list[str] = []
    # 初始化 blank_run
    blank_run = 0
    # 遍历：line in out
    for line in out:
        # 条件分支：line.strip() == ""
        if line.strip() == "":
            # 就地更新 blank_run
            blank_run += 1
            # 条件分支：blank_run <= 2
            if blank_run <= 2:
                # 追加到列表
                collapsed.append(line)
        else:
            # 初始化 blank_run
            blank_run = 0
            # 追加到列表
            collapsed.append(line)

    # 返回 "\n".join(collapsed).rstrip() + "\n"
    return "\n".join(collapsed).rstrip() + "\n"
