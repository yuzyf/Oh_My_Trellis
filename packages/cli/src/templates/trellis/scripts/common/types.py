"""
Trellis 任务数据的核心类型定义。

提供:
    TaskData     — task.json 形状的 TypedDict（仅读路径类型提示）
    TaskInfo     — 已加载任务的冻结 dataclass（公开 API 类型）
    AgentRecord  — registry.json 中 agent 条目的 TypedDict
"""

# 启用延迟注解求值
from __future__ import annotations

# dataclass、路径与 TypedDict
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict


# 说明：=============================================================================
# task.json 形状（TypedDict — 仅用于读路径类型提示）
# 说明：=============================================================================

class TaskData(TypedDict, total=False):
    """磁盘上 task.json 的字段形状。

    仅用于读取时的类型标注。
    写回必须用原始 dict，以免丢失未知字段。
    """

    id: str  # 任务 ID
    name: str  # 任务名
    title: str  # 标题
    description: str  # 描述
    status: str  # 状态
    dev_type: str  # 开发类型
    scope: str | None  # 范围
    package: str | None  # 所属包
    priority: str  # 优先级
    creator: str  # 创建者
    assignee: str  # 指派人
    createdAt: str  # 创建时间
    completedAt: str | None  # 完成时间
    branch: str | None  # 关联分支
    base_branch: str | None  # 基线分支
    worktree_path: str | None  # worktree 路径
    commit: str | None  # 关联提交
    pr_url: str | None  # PR 链接
    subtasks: list[str]  # 子任务列表（旧字段）
    children: list[str]  # 子任务目录名
    parent: str | None  # 父任务
    relatedFiles: list[str]  # 相关文件
    notes: str  # 备注
    meta: dict  # 扩展元数据


# 说明：=============================================================================
# 已加载任务对象（冻结 dataclass — 公开 API 类型）
# 说明：=============================================================================

@dataclass(frozen=True)
class TaskInfo:
    """已加载任务的不可变视图。

    由 load_task() / iter_active_tasks() 创建。
    包含常用字段；原始 dict 保存在 raw 中，供写回与非常用字段访问。
    """

    dir_name: str  # 任务目录名
    directory: Path  # 任务目录绝对路径
    title: str  # 展示标题
    status: str  # 状态字符串
    assignee: str  # 指派人
    priority: str  # 优先级
    children: tuple[str, ...]  # 子任务目录名元组
    parent: str | None  # 父任务目录名
    package: str | None  # 所属包
    raw: dict  # 原始 dict — 写回与非常用字段用

    @property
    def name(self) -> str:
        """任务名：优先 name，其次 id，最后目录名。"""
        return self.raw.get("name") or self.raw.get("id") or self.dir_name  # name → id → 目录名 回退
    @property
    def description(self) -> str:
        """任务描述，缺省为空串。"""
        return self.raw.get("description", "")  # 无描述则空串
    @property
    def branch(self) -> str | None:
        """关联 git 分支。"""
        return self.raw.get("branch")  # 可能为 None
    @property
    def meta(self) -> dict:
        """扩展元数据 dict，缺省为空 dict。"""
        return self.raw.get("meta", {})  # 无 meta 则空 dict
# 说明：=============================================================================
# registry.json 中的 agent 条目
# 说明：=============================================================================

class AgentRecord(TypedDict, total=False):
    """registry.json 中单个 agent 条目的字段形状。"""

    id: str  # agent 标识
    pid: int  # 进程 ID
    task_dir: str  # 关联任务目录
    worktree_path: str  # worktree 路径
    branch: str  # 分支名
    platform: str  # 平台名
    started_at: str  # 启动时间
    status: str  # 状态
