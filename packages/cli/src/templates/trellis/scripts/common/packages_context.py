#!/usr/bin/env python3
"""
packages_context 模块：Package discovery and context output.


提供:
get_packages_info           - Get structured package info
get_packages_section        - Build PACKAGES text section
get_context_packages_text   - Full packages text output (--mode packages)
get_context_packages_json   - Full packages JSON output (--mode packages --json)
"""

# 启用延迟注解求值等 future 特性
from __future__ import annotations

# 导入依赖
from pathlib import Path

from .config import _is_true_config_value, get_default_package, get_packages, get_spec_scope
from .paths import (
    DIR_SPEC,
    DIR_WORKFLOW,
    get_current_task,
    get_repo_root,
)
from .tasks import load_task


# 说明：=============================================================================
# 内部辅助
# 说明：=============================================================================

def _scan_spec_layers(spec_dir: Path, package: str | None = None) -> list[str]:
    """扫描 spec 目录，返回可用分层（子目录）。"""
    # 按条件取值赋给 target
    target = spec_dir / package if package else spec_dir
    # 若条件不成立：not target.is_dir()
    if not target.is_dir():
        return []  # 返回列表结果
    # 返回 sorted 的调用结果
    return sorted(
        d.name for d in target.iterdir() if d.is_dir() and d.name != "guides"
    )


def _get_active_task_package(repo_root: Path) -> str | None:
    """获取：Get the package field from the active task's task.json."""
    # current ← 调用 get_current_task
    current = get_current_task(repo_root)
    # 若条件不成立：not current
    if not current:
        return None  # 返回 None
    # ct ← 调用 load_task
    ct = load_task(repo_root / current)
    # 按条件返回不同值
    return ct.package if ct and ct.package else None


def _resolve_scope_set(
    packages: dict,
    spec_scope,
    task_pkg: str | None,
    default_pkg: str | None,
) -> set | None:
    """
    解析/解析出：Resolve spec_scope to a set of allowed package names, or None for full scan.
    """
    # 若条件不成立：not packages
    if not packages:
        return None  # 返回 None

    # 若为 None：spec_scope is None
    if spec_scope is None:
        return None  # 返回 None

    # 条件分支：isinstance(spec_scope, str) and spec_scop…
    if isinstance(spec_scope, str) and spec_scope == "active_task":
        # 条件分支：task_pkg and task_pkg in packages
        if task_pkg and task_pkg in packages:
            return {task_pkg}  # 返回结果
        # 条件分支：default_pkg and default_pkg in packages
        if default_pkg and default_pkg in packages:
            return {default_pkg}  # 返回结果
        return None  # 返回 None

    # 条件分支：isinstance(spec_scope, list)
    if isinstance(spec_scope, list):
        # 用推导式生成 valid
        valid = {e for e in spec_scope if e in packages}
        # 条件分支：valid
        if valid:
            return valid  # 返回 valid
        # 全部无效：回退
        # 条件分支：task_pkg and task_pkg in packages
        if task_pkg and task_pkg in packages:
            return {task_pkg}  # 返回结果
        # 条件分支：default_pkg and default_pkg in packages
        if default_pkg and default_pkg in packages:
            return {default_pkg}  # 返回结果
        return None  # 返回 None

    return None  # 返回 None


# 说明：=============================================================================
# 公开函数
# 说明：=============================================================================

def get_packages_info(repo_root: Path) -> list[dict]:
    """
    获取：Get structured package info for monorepo projects.

    Returns list of dicts with keys: name, path, type, default, specLayers,
    isSubmodule, isGitRepo.
    Returns empty list for single-repo projects.
    """
    # packages ← 调用 get_packages
    packages = get_packages(repo_root)
    # 若条件不成立：not packages
    if not packages:
        return []  # 返回列表结果

    # default_pkg ← 调用 get_default_package
    default_pkg = get_default_package(repo_root)
    # 计算后赋给 spec_dir
    spec_dir = repo_root / DIR_WORKFLOW / DIR_SPEC
    # result 初始化为空列表
    result = []

    # 遍历：pkg_name, pkg_config in packages.items()
    for pkg_name, pkg_config in packages.items():
        # 按条件取值赋给 pkg_path
        pkg_path = pkg_config.get("path", pkg_name) if isinstance(pkg_config, dict) else str(pkg_config)
        # 按条件取值赋给 pkg_type
        pkg_type = pkg_config.get("type", "local") if isinstance(pkg_config, dict) else "local"
        # 按条件取值赋给 pkg_git
        pkg_git = pkg_config.get("git", False) if isinstance(pkg_config, dict) else False
        # layers ← 调用 _scan_spec_layers
        layers = _scan_spec_layers(spec_dir, pkg_name)

        # 追加到列表
        result.append({
            "name": pkg_name,
            "path": pkg_path,
            "type": pkg_type,
            "default": pkg_name == default_pkg,
            "specLayers": layers,
            "isSubmodule": pkg_type == "submodule",
            "isGitRepo": _is_true_config_value(pkg_git),
        })

    return result  # 返回 result


def get_packages_section(repo_root: Path) -> str:
    """创建：Build the PACKAGES section for text output."""
    # 计算后赋给 spec_dir
    spec_dir = repo_root / DIR_WORKFLOW / DIR_SPEC
    # pkg_info ← 调用 get_packages_info
    pkg_info = get_packages_info(repo_root)

    # 赋值（含类型标注）：lines
    lines: list[str] = []
    # 追加到列表
    lines.append("## PACKAGES")

    # 若条件不成立：not pkg_info
    if not pkg_info:
        # 追加到列表
        lines.append("(single-repo mode)")
        # layers ← 调用 _scan_spec_layers
        layers = _scan_spec_layers(spec_dir)
        # 条件分支：layers
        if layers:
            # 追加到列表
            lines.append(f"Spec layers: {', '.join(layers)}")
        return "\n".join(lines)  # 返回 join(...) 的结果

    # default_pkg ← 调用 get_default_package
    default_pkg = get_default_package(repo_root)

    # 遍历：pkg in pkg_info
    for pkg in pkg_info:
        # 按条件取值赋给 layers_str
        layers_str = f"  [{', '.join(pkg['specLayers'])}]" if pkg["specLayers"] else ""
        # 按条件取值赋给 submodule_tag
        submodule_tag = "  (submodule)" if pkg["isSubmodule"] else ""
        # 按条件取值赋给 git_repo_tag
        git_repo_tag = "  (git repo)" if pkg["isGitRepo"] else ""
        # 按条件取值赋给 default_tag
        default_tag = "  *" if pkg["default"] else ""
        # 追加到列表
        lines.append(
            f"- {pkg['name']:<16} {pkg['path']:<20}{layers_str}{submodule_tag}{git_repo_tag}{default_tag}"
        )

    # 条件分支：default_pkg
    if default_pkg:
        # 追加到列表
        lines.append(f"Default package: {default_pkg}")

    return "\n".join(lines)  # 返回 join(...) 的结果


def get_context_packages_text(repo_root: Path | None = None) -> str:
    """获取：Get packages context as formatted text (for --mode packages)."""
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # pkg_info ← 调用 get_packages_info
    pkg_info = get_packages_info(repo_root)
    # 赋值（含类型标注）：lines
    lines: list[str] = []

    # 若条件不成立：not pkg_info
    if not pkg_info:
        # 计算后赋给 spec_dir
        spec_dir = repo_root / DIR_WORKFLOW / DIR_SPEC
        # 追加到列表
        lines.append("Single-repo project (no packages configured)")
        # 追加到列表
        lines.append("")
        # layers ← 调用 _scan_spec_layers
        layers = _scan_spec_layers(spec_dir)
        # 条件分支：layers
        if layers:
            # 追加到列表
            lines.append(f"Spec layers: {', '.join(layers)}")
        return "\n".join(lines)  # 返回 join(...) 的结果

    # 解析/定位 scope for annotations
    # 逻辑运算结果赋给 packages_dict
    packages_dict = get_packages(repo_root) or {}
    # default_pkg ← 调用 get_default_package
    default_pkg = get_default_package(repo_root)
    # spec_scope ← 调用 get_spec_scope
    spec_scope = get_spec_scope(repo_root)
    # task_pkg ← 调用 _get_active_task_package
    task_pkg = _get_active_task_package(repo_root)
    # scope_set ← 调用 _resolve_scope_set
    scope_set = _resolve_scope_set(packages_dict, spec_scope, task_pkg, default_pkg)

    # 追加到列表
    lines.append("## PACKAGES")
    # 追加到列表
    lines.append("")
    # 遍历：pkg in pkg_info
    for pkg in pkg_info:
        # 按条件取值赋给 default_tag
        default_tag = " (default)" if pkg["default"] else ""
        # 按条件取值赋给 type_tag
        type_tag = f" [{pkg['type']}]" if pkg["type"] != "local" else ""
        # 按条件取值赋给 git_tag
        git_tag = " [git repo]" if pkg["isGitRepo"] else ""

        # 作用域标注
        # 初始化 scope_tag
        scope_tag = ""
        # 若已有值：scope_set is not None and pkg["name"] not in scope
        if scope_set is not None and pkg["name"] not in scope_set:
            # 初始化 scope_tag
            scope_tag = " (out of scope)"

        # 追加到列表
        lines.append(f"### {pkg['name']}{default_tag}{type_tag}{git_tag}{scope_tag}")
        # 追加到列表
        lines.append(f"Path: {pkg['path']}")
        # 条件分支：pkg["specLayers"]
        if pkg["specLayers"]:
            # 追加到列表
            lines.append(f"Spec layers: {', '.join(pkg['specLayers'])}")
            # 遍历：layer in pkg["specLayers"]
            for layer in pkg["specLayers"]:
                # 追加到列表
                lines.append(f"  - .trellis/spec/{pkg['name']}/{layer}/index.md")
        else:
            # 追加到列表
            lines.append("Spec: not configured")
        # 追加到列表
        lines.append("")

    # 同时展示共享指南
    # 计算后赋给 guides_dir
    guides_dir = repo_root / DIR_WORKFLOW / DIR_SPEC / "guides"
    # 条件分支：guides_dir.is_dir()
    if guides_dir.is_dir():
        # 追加到列表
        lines.append("### Shared Guides (always included)")
        # 追加到列表
        lines.append("Path: .trellis/spec/guides/index.md")
        # 追加到列表
        lines.append("")

    return "\n".join(lines)  # 返回 join(...) 的结果


def get_context_packages_json(repo_root: Path | None = None) -> dict:
    """获取：Get packages context as a dictionary (for --mode packages --json)."""
    # 若为 None：repo_root is None
    if repo_root is None:
        # repo_root ← 调用 get_repo_root
        repo_root = get_repo_root()

    # pkg_info ← 调用 get_packages_info
    pkg_info = get_packages_info(repo_root)

    # 若条件不成立：not pkg_info
    if not pkg_info:
        # 计算后赋给 spec_dir
        spec_dir = repo_root / DIR_WORKFLOW / DIR_SPEC
        # layers ← 调用 _scan_spec_layers
        layers = _scan_spec_layers(spec_dir)
        # 返回 { "mode": "single-repo", "specLayer…
        return {
            "mode": "single-repo",
            "specLayers": layers,
        }

    # default_pkg ← 调用 get_default_package
    default_pkg = get_default_package(repo_root)
    # spec_scope ← 调用 get_spec_scope
    spec_scope = get_spec_scope(repo_root)
    # task_pkg ← 调用 _get_active_task_package
    task_pkg = _get_active_task_package(repo_root)

    # 返回 { "mode": "monorepo", "packages": p…
    return {
        "mode": "monorepo",
        "packages": pkg_info,
        "defaultPackage": default_pkg,
        "specScope": spec_scope,
        "activeTaskPackage": task_pkg,
    }
