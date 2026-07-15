"""
多平台 CLI 适配器（CLI Adapter）。

抽象 Claude Code、OpenCode、Cursor、iFlow、Codex、Kilo、Kiro、Gemini CLI、
Antigravity、Devin、Qoder、CodeBuddy、GitHub Copilot、Factory Droid、Pi Agent 等差异。

用法:
    from common.cli_adapter import CLIAdapter
    adapter = CLIAdapter("opencode")
    cmd = adapter.build_run_command(agent="dispatch", session_id="abc123", prompt="Start the pipeline")
"""

# 启用延迟注解求值等 future 特性
from __future__ import annotations

# 导入依赖
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Literal

# 按键/下标取值赋给 Platform
Platform = Literal[
    "claude",
    "opencode",
    "cursor",
    "iflow",
    "codex",
    "kilo",
    "kiro",
    "gemini",
    "antigravity",
    "devin",
    "qoder",
    "codebuddy",
    "copilot",
    "droid",
    "pi",
    "omp",
]


@dataclass
class CLIAdapter:
    """CLIAdapter 类：Adapter for different AI coding CLI tools."""

    # 声明带类型标注的字段/变量：platform
    platform: Platform

    # 说明：=========================================================================
    # Agent 名称映射
    # 说明：=========================================================================

    # OpenCode 有不可覆盖的内置 agent
    # 参见：https://github.com/sst/opencode/issues/4271
    # 注意：类级常量，不是 dataclass 字段
    # 赋值（含类型标注）：_AGENT_NAME_MAP
    _AGENT_NAME_MAP: ClassVar[dict[Platform, dict[str, str]]] = {
        "claude": {},  # 无需映射
        "opencode": {
            "plan": "trellis-plan",  # 'plan' 是 OpenCode 内置 agent
        },
    }

    def get_agent_name(self, agent: str) -> str:
        """
        获取：Get platform-specific agent name.


        参数:
                agent: Original agent name (e.g., 'plan', 'dispatch')


        返回:
                Platform-specific agent name (e.g., 'trellis-plan' for OpenCode)
            
        """
        # mapping ← 调用 self._AGENT_NAME_MAP.get
        mapping = self._AGENT_NAME_MAP.get(self.platform, {})
        # 返回 mapping.get 的调用结果
        return mapping.get(agent, agent)

    # 说明：=========================================================================
    # Agent 路径
    # 说明：=========================================================================

    @property
    def config_dir_name(self) -> str:
        """
        获取：Get platform-specific config directory name.


        返回:
                Directory name ('.claude', '.opencode', '.cursor', '.iflow', '.codex', '.kilocode', '.kiro', '.gemini', '.agent', '.devin', '.qoder', '.codebuddy', '.github/copilot', '.factory', or '.pi')
            
        """
        # 条件分支：self.platform == "opencode"
        if self.platform == "opencode":
            # 返回常量 '.opencode'
            return ".opencode"
        # 条件分支：self.platform == "cursor"
        elif self.platform == "cursor":
            # 返回常量 '.cursor'
            return ".cursor"
        # 条件分支：self.platform == "iflow"
        elif self.platform == "iflow":
            # 返回常量 '.iflow'
            return ".iflow"
        # 条件分支：self.platform == "codex"
        elif self.platform == "codex":
            # 返回常量 '.codex'
            return ".codex"
        # 条件分支：self.platform == "kilo"
        elif self.platform == "kilo":
            # 返回常量 '.kilocode'
            return ".kilocode"
        # 条件分支：self.platform == "kiro"
        elif self.platform == "kiro":
            # 返回常量 '.kiro'
            return ".kiro"
        # 条件分支：self.platform == "gemini"
        elif self.platform == "gemini":
            # 返回常量 '.gemini'
            return ".gemini"
        # 条件分支：self.platform == "antigravity"
        elif self.platform == "antigravity":
            # 返回常量 '.agent'
            return ".agent"
        # 条件分支：self.platform == "devin"
        elif self.platform == "devin":
            # 返回常量 '.devin'
            return ".devin"
        # 条件分支：self.platform == "qoder"
        elif self.platform == "qoder":
            # 返回常量 '.qoder'
            return ".qoder"
        # 条件分支：self.platform == "codebuddy"
        elif self.platform == "codebuddy":
            # 返回常量 '.codebuddy'
            return ".codebuddy"
        # 条件分支：self.platform == "copilot"
        elif self.platform == "copilot":
            # 返回常量 '.github/copilot'
            return ".github/copilot"
        # 条件分支：self.platform == "droid"
        elif self.platform == "droid":
            # 返回常量 '.factory'
            return ".factory"
        # 条件分支：self.platform == "pi"
        elif self.platform == "pi":
            # 返回常量 '.pi'
            return ".pi"
        # 条件分支：self.platform == "omp"
        elif self.platform == "omp":
            # 返回常量 '.omp'
            return ".omp"
        else:
            # 返回常量 '.claude'
            return ".claude"

    def get_config_dir(self, project_root: Path) -> Path:
        """
        获取：Get platform-specific config directory.


        参数:
                project_root: Project root directory


        返回:
                Path to config directory (.claude, .opencode, .cursor, .iflow, .codex, .kilocode, .kiro, .gemini, .agent, .devin, .qoder, .codebuddy, .github/copilot, .factory, or .pi)
            
        """
        # 返回 project_root / self.config_dir_name
        return project_root / self.config_dir_name

    def get_agent_path(self, agent: str, project_root: Path) -> Path:
        """
        获取：Get path to agent definition file.


        参数:
                agent: Agent name (original, before mapping)
                project_root: Project root directory


        返回:
                Path to agent definition file (.md for most platforms, .toml for Codex)
            
        """
        # mapped_name ← 调用 self.get_agent_name
        mapped_name = self.get_agent_name(agent)
        # 条件分支：self.platform == "codex"
        if self.platform == "codex":
            # 返回 self.get_config_dir(project_root) /…
            return self.get_config_dir(project_root) / "agents" / f"{mapped_name}.toml"
        # 返回 self.get_config_dir(project_root) /…
        return self.get_config_dir(project_root) / "agents" / f"{mapped_name}.md"

    def get_commands_path(self, project_root: Path, *parts: str) -> Path:
        """
        获取：Get path to commands directory or specific command file.


        参数:
                project_root: Project root directory
                *parts: Additional path parts (e.g., 'trellis', 'finish-work.md')


        返回:
                Path to commands directory or file


        说明:
                Cursor uses prefix naming: .cursor/commands/trellis-<name>.md
                Antigravity uses workflow directory: .agent/workflows/<name>.md
                Devin uses workflow directory: .devin/workflows/trellis-<name>.md
                Copilot uses prompt files: .github/prompts/<name>.prompt.md
                Pi uses prompt templates: .pi/prompts/trellis-<name>.md
                Claude/OpenCode use subdirectory: .claude/commands/trellis/<name>.md
            
        """
        # 条件分支：self.platform == "pi"
        if self.platform == "pi":
            # 计算后赋给 prompts_dir
            prompts_dir = self.get_config_dir(project_root) / "prompts"
            # 若条件不成立：not parts
            if not parts:
                return prompts_dir  # 返回 prompts_dir
            # 条件分支：len(parts) >= 2 and parts[0] == "trellis"
            if len(parts) >= 2 and parts[0] == "trellis":
                # 按键/下标取值赋给 filename
                filename = parts[-1]
                # 条件分支：filename.endswith(".md")
                if filename.endswith(".md"):
                    # 按键/下标取值赋给 filename
                    filename = filename[:-3]
                # 返回 prompts_dir / f"trellis-{filename}.…
                return prompts_dir / f"trellis-{filename}.md"
            # 返回 prompts_dir / Path(*parts)
            return prompts_dir / Path(*parts)
        # 条件分支：self.platform == "omp"
        if self.platform == "omp":
            # 计算后赋给 commands_dir
            commands_dir = self.get_config_dir(project_root) / "commands"
            # 若条件不成立：not parts
            if not parts:
                return commands_dir  # 返回 commands_dir
            # 条件分支：len(parts) >= 2 and parts[0] == "trellis"
            if len(parts) >= 2 and parts[0] == "trellis":
                # 按键/下标取值赋给 filename
                filename = parts[-1]
                # 条件分支：filename.endswith(".md")
                if filename.endswith(".md"):
                    # 按键/下标取值赋给 filename
                    filename = filename[:-3]
                # 返回 commands_dir / f"trellis-{filename}…
                return commands_dir / f"trellis-{filename}.md"
            # 返回 commands_dir / Path(*parts)
            return commands_dir / Path(*parts)


        # 条件分支：self.platform == "devin"
        if self.platform == "devin":
            # 计算后赋给 workflow_dir
            workflow_dir = self.get_config_dir(project_root) / "workflows"
            # 若条件不成立：not parts
            if not parts:
                return workflow_dir  # 返回 workflow_dir
            # 条件分支：len(parts) >= 2 and parts[0] == "trellis"
            if len(parts) >= 2 and parts[0] == "trellis":
                # 按键/下标取值赋给 filename
                filename = parts[-1]
                # 返回 workflow_dir / f"trellis-{filename}"
                return workflow_dir / f"trellis-{filename}"
            # 返回 workflow_dir / Path(*parts)
            return workflow_dir / Path(*parts)

        # 条件分支：self.platform in ("antigravity", "kilo")
        if self.platform in ("antigravity", "kilo"):
            # 计算后赋给 workflow_dir
            workflow_dir = self.get_config_dir(project_root) / "workflows"
            # 若条件不成立：not parts
            if not parts:
                return workflow_dir  # 返回 workflow_dir
            # 条件分支：len(parts) >= 2 and parts[0] == "trellis"
            if len(parts) >= 2 and parts[0] == "trellis":
                # 按键/下标取值赋给 filename
                filename = parts[-1]
                # 返回 workflow_dir / filename
                return workflow_dir / filename
            # 返回 workflow_dir / Path(*parts)
            return workflow_dir / Path(*parts)

        # 条件分支：self.platform == "copilot"
        if self.platform == "copilot":
            # 计算后赋给 prompts_dir
            prompts_dir = project_root / ".github" / "prompts"
            # 若条件不成立：not parts
            if not parts:
                return prompts_dir  # 返回 prompts_dir
            # 条件分支：len(parts) >= 2 and parts[0] == "trellis"
            if len(parts) >= 2 and parts[0] == "trellis":
                # 按键/下标取值赋给 filename
                filename = parts[-1]
                # 条件分支：filename.endswith(".md")
                if filename.endswith(".md"):
                    # 按键/下标取值赋给 filename
                    filename = filename[:-3]
                # 返回 prompts_dir / f"{filename}.prompt.m…
                return prompts_dir / f"{filename}.prompt.md"
            # 返回 prompts_dir / Path(*parts)
            return prompts_dir / Path(*parts)

        # 若条件不成立：not parts
        if not parts:
            # 返回 self.get_config_dir(project_root) /…
            return self.get_config_dir(project_root) / "commands"

        # Cursor 用前缀命名而非子目录
        # 条件分支：self.platform == "cursor" and len(parts) …
        if self.platform == "cursor" and len(parts) >= 2 and parts[0] == "trellis":
            # 把 trellis/<name>.md 转为 trellis-<name>.md
            # 按键/下标取值赋给 filename
            filename = parts[-1]
            # 返回 self.get_config_dir(project_root) /…
            return (
                self.get_config_dir(project_root) / "commands" / f"trellis-{filename}"
            )

        # 返回 self.get_config_dir(project_root) /…
        return self.get_config_dir(project_root) / "commands" / Path(*parts)

    def get_trellis_command_path(self, name: str) -> str:
        """
        获取：Get relative path to a trellis command file.


        参数:
                name: Command name without extension (e.g., 'finish-work', 'check')


        返回:
                Relative path string for use in JSONL entries


        说明:
                Cursor: .cursor/commands/trellis-<name>.md
                Codex: .agents/skills/trellis-<name>/SKILL.md
                Kiro: .kiro/skills/trellis-<name>/SKILL.md
                Gemini: .gemini/commands/trellis/<name>.toml
                Antigravity: .agent/workflows/<name>.md
                Devin: .devin/workflows/trellis-<name>.md
                Pi: .pi/prompts/trellis-<name>.md
                Others: .{platform}/commands/trellis/<name>.md
            
        """
        # 条件分支：self.platform == "cursor"
        if self.platform == "cursor":
            return f".cursor/commands/trellis-{name}.md"  # 返回格式化字符串
        # 条件分支：self.platform == "codex"
        elif self.platform == "codex":
            # 0.5.0-beta.0 起所有 skill 目录加 `trellis-` 前缀
            # （详见该版本 manifest 中的 60+ 重命名项）
            return f".agents/skills/trellis-{name}/SKILL.md"
        # 条件分支：self.platform == "kiro"
        elif self.platform == "kiro":
            return f".kiro/skills/trellis-{name}/SKILL.md"  # 返回格式化字符串
        # 条件分支：self.platform == "gemini"
        elif self.platform == "gemini":
            return f".gemini/commands/trellis/{name}.toml"  # 返回格式化字符串
        # 条件分支：self.platform == "antigravity"
        elif self.platform == "antigravity":
            return f".agent/workflows/{name}.md"  # 返回格式化字符串
        # 条件分支：self.platform == "devin"
        elif self.platform == "devin":
            return f".devin/workflows/trellis-{name}.md"  # 返回格式化字符串
        # 条件分支：self.platform == "kilo"
        elif self.platform == "kilo":
            return f".kilocode/workflows/{name}.md"  # 返回格式化字符串
        # 条件分支：self.platform == "copilot"
        elif self.platform == "copilot":
            return f".github/prompts/{name}.prompt.md"  # 返回格式化字符串
        # 条件分支：self.platform == "droid"
        elif self.platform == "droid":
            return f".factory/commands/trellis/{name}.md"  # 返回格式化字符串
        # 条件分支：self.platform == "pi"
        elif self.platform == "pi":
            return f".pi/prompts/trellis-{name}.md"  # 返回格式化字符串
        # 条件分支：self.platform == "omp"
        elif self.platform == "omp":
            return f".omp/commands/trellis-{name}.md"  # 返回格式化字符串
        else:
            return f"{self.config_dir_name}/commands/trellis/{name}.md"  # 返回格式化字符串

    # 说明：=========================================================================
    # 环境变量
    # 说明：=========================================================================

    def get_non_interactive_env(self) -> dict[str, str]:
        """
        获取：Get environment variables for non-interactive mode.


        返回:
                Dict of environment variables to set
            
        """
        # 条件分支：self.platform == "opencode"
        if self.platform == "opencode":
            # 返回 {"OPENCODE_NON_INTERACTIVE": "1"}
            return {"OPENCODE_NON_INTERACTIVE": "1"}
        # 条件分支：self.platform == "iflow"
        elif self.platform == "iflow":
            # 返回 {"IFLOW_NON_INTERACTIVE": "1"}
            return {"IFLOW_NON_INTERACTIVE": "1"}
        # 条件分支：self.platform == "codex"
        elif self.platform == "codex":
            # 返回 {"CODEX_NON_INTERACTIVE": "1"}
            return {"CODEX_NON_INTERACTIVE": "1"}
        # 条件分支：self.platform == "kiro"
        elif self.platform == "kiro":
            # 返回 {"KIRO_NON_INTERACTIVE": "1"}
            return {"KIRO_NON_INTERACTIVE": "1"}
        # 条件分支：self.platform == "gemini"
        elif self.platform == "gemini":
            return {}  # Gemini CLI 没有非交互环境变量
        # 条件分支：self.platform == "antigravity"
        elif self.platform == "antigravity":
            return {}  # 返回字典结果
        # 条件分支：self.platform == "devin"
        elif self.platform == "devin":
            return {}  # 返回字典结果
        # 条件分支：self.platform == "qoder"
        elif self.platform == "qoder":
            return {}  # 返回字典结果
        # 条件分支：self.platform == "codebuddy"
        elif self.platform == "codebuddy":
            return {}  # 返回字典结果
        # 条件分支：self.platform == "copilot"
        elif self.platform == "copilot":
            return {}  # 返回字典结果
        # 条件分支：self.platform == "droid"
        elif self.platform == "droid":
            return {}  # 返回字典结果
        # 条件分支：self.platform == "pi"
        elif self.platform == "pi":
            return {}  # 返回字典结果
        # 条件分支：self.platform == "omp"
        elif self.platform == "omp":
            return {}  # 返回字典结果
        else:
            # 返回 {"CLAUDE_NON_INTERACTIVE": "1"}
            return {"CLAUDE_NON_INTERACTIVE": "1"}

    # 说明：=========================================================================
    # CLI 命令构建
    # 说明：=========================================================================

    def build_run_command(
        self,
        agent: str,
        prompt: str,
        session_id: str | None = None,
        skip_permissions: bool = True,
        verbose: bool = True,
        json_output: bool = True,
    ) -> list[str]:
        """
        创建：Build CLI command for running an agent.


        参数:
                agent: Agent name (will be mapped if needed)
                prompt: Prompt to send to the agent
                session_id: Optional session ID (Claude Code only for creation)
                skip_permissions: Whether to skip permission prompts
                verbose: Whether to enable verbose output
                json_output: Whether to use JSON output format


        返回:
                List of command arguments
            
        """
        # mapped_agent ← 调用 self.get_agent_name
        mapped_agent = self.get_agent_name(agent)

        # 条件分支：self.platform == "opencode"
        if self.platform == "opencode":
            # 构造列表赋给 cmd
            cmd = ["opencode", "run"]
            # 扩展列表
            cmd.extend(["--agent", mapped_agent])

            # 注意：OpenCode 的 'run' 模式默认非交互
            # 没有与 Claude Code --dangerously-skip-permissions 对等的选项
            # 参见：https://github.com/anomalyco/opencode/issues/9070

            # 条件分支：json_output
            if json_output:
                # 扩展列表
                cmd.extend(["--format", "json"])

            # 条件分支：verbose
            if verbose:
                # 扩展列表
                cmd.extend(["--log-level", "DEBUG", "--print-logs"])

            # 注意：OpenCode 创建时不支持 --session-id
            # Session ID 需在启动后从日志提取

            # 追加到列表
            cmd.append(prompt)

        # 条件分支：self.platform == "iflow"
        elif self.platform == "iflow":
            # 构造列表赋给 cmd
            cmd = ["iflow", "-y", "-p"]
            # 追加到列表
            cmd.append(f"${mapped_agent} {prompt}")
        # 条件分支：self.platform == "codex"
        elif self.platform == "codex":
            # 构造列表赋给 cmd
            cmd = ["codex", "exec"]
            # 追加到列表
            cmd.append(prompt)
        # 条件分支：self.platform == "kiro"
        elif self.platform == "kiro":
            # 构造列表赋给 cmd
            cmd = ["kiro", "run", prompt]
        # 条件分支：self.platform == "gemini"
        elif self.platform == "gemini":
            # 构造列表赋给 cmd
            cmd = ["gemini"]
            # 追加到列表
            cmd.append(prompt)
        # 条件分支：self.platform == "antigravity"
        elif self.platform == "antigravity":
            # 抛出异常：ValueError( "Antigravity workflows …
            raise ValueError(
                "Antigravity workflows are UI slash commands; CLI agent run is not supported."
            )
        # 条件分支：self.platform == "devin"
        elif self.platform == "devin":
            # 抛出异常：ValueError( "Devin workflows are UI…
            raise ValueError(
                "Devin workflows are UI slash commands; CLI agent run is not supported."
            )
        # 条件分支：self.platform == "qoder"
        elif self.platform == "qoder":
            # 构造列表赋给 cmd
            cmd = ["qodercli", "-p", prompt]
        # 条件分支：self.platform == "codebuddy"
        elif self.platform == "codebuddy":
            # 抛出异常：ValueError( "CodeBuddy does not sup…
            raise ValueError(
                "CodeBuddy does not support non-interactive mode (no CLI agent)"
            )
        # 条件分支：self.platform == "copilot"
        elif self.platform == "copilot":
            # 抛出异常：ValueError( "GitHub Copilot is IDE-…
            raise ValueError(
                "GitHub Copilot is IDE-only; CLI agent run is not supported."
            )
        # 条件分支：self.platform == "droid"
        elif self.platform == "droid":
            # 抛出异常：ValueError( "Factory Droid CLI agen…
            raise ValueError(
                "Factory Droid CLI agent run is not yet supported."
            )
        # 条件分支：self.platform == "pi"
        elif self.platform == "pi":
            # 构造列表赋给 cmd
            cmd = ["pi", "-p", prompt]
        # 条件分支：self.platform == "omp"
        elif self.platform == "omp":
            # 抛出异常：ValueError( "OMP uses native task t…
            raise ValueError(
                "OMP uses native task tool for agent runs; CLI agent run is not supported."
            )

        else:  # Claude Code CLI 分支
            # 构造列表赋给 cmd
            cmd = ["claude", "-p"]
            # 扩展列表
            cmd.extend(["--agent", mapped_agent])

            # 条件分支：session_id
            if session_id:
                # 扩展列表
                cmd.extend(["--session-id", session_id])

            # 条件分支：skip_permissions
            if skip_permissions:
                # 追加到列表
                cmd.append("--dangerously-skip-permissions")

            # 条件分支：json_output
            if json_output:
                # 扩展列表
                cmd.extend(["--output-format", "stream-json"])

            # 条件分支：verbose
            if verbose:
                # 追加到列表
                cmd.append("--verbose")

            # 追加到列表
            cmd.append(prompt)

        return cmd  # 返回 cmd

    def build_resume_command(self, session_id: str) -> list[str]:
        """
        创建：Build CLI command for resuming a session.


        参数:
                session_id: Session ID to resume (ignored for iFlow)


        返回:
                List of command arguments
            
        """
        # 条件分支：self.platform == "opencode"
        if self.platform == "opencode":
            # 返回 ["opencode", "run", "--session", se…
            return ["opencode", "run", "--session", session_id]
        # 条件分支：self.platform == "iflow"
        elif self.platform == "iflow":
            # iFlow 用 -c 继续最近一次对话
            # iFlow 不支持 session ID，故忽略 session_id
            # 返回 ["iflow", "-c"]
            return ["iflow", "-c"]
        # 条件分支：self.platform == "codex"
        elif self.platform == "codex":
            # 返回 ["codex", "resume", session_id]
            return ["codex", "resume", session_id]
        # 条件分支：self.platform == "kiro"
        elif self.platform == "kiro":
            # 返回 ["kiro", "resume", session_id]
            return ["kiro", "resume", session_id]
        # 条件分支：self.platform == "gemini"
        elif self.platform == "gemini":
            # 返回 ["gemini", "--resume", session_id]
            return ["gemini", "--resume", session_id]
        # 条件分支：self.platform == "antigravity"
        elif self.platform == "antigravity":
            # 抛出异常：ValueError( "Antigravity workflows …
            raise ValueError(
                "Antigravity workflows are UI slash commands; CLI resume is not supported."
            )
        # 条件分支：self.platform == "devin"
        elif self.platform == "devin":
            # 抛出异常：ValueError( "Devin workflows are UI…
            raise ValueError(
                "Devin workflows are UI slash commands; CLI resume is not supported."
            )
        # 条件分支：self.platform == "qoder"
        elif self.platform == "qoder":
            # 返回 ["qodercli", "--resume", session_id]
            return ["qodercli", "--resume", session_id]
        # 条件分支：self.platform == "codebuddy"
        elif self.platform == "codebuddy":
            # 抛出异常：ValueError( "CodeBuddy does not sup…
            raise ValueError(
                "CodeBuddy does not support non-interactive mode (no CLI agent)"
            )
        # 条件分支：self.platform == "copilot"
        elif self.platform == "copilot":
            # 抛出异常：ValueError( "GitHub Copilot is IDE-…
            raise ValueError(
                "GitHub Copilot is IDE-only; CLI resume is not supported."
            )
        # 条件分支：self.platform == "droid"
        elif self.platform == "droid":
            # 抛出异常：ValueError( "Factory Droid CLI resu…
            raise ValueError(
                "Factory Droid CLI resume is not yet supported."
            )
        # 条件分支：self.platform == "pi"
        elif self.platform == "pi":
            # 返回 ["pi", "-c", session_id]
            return ["pi", "-c", session_id]
        # 条件分支：self.platform == "omp"
        elif self.platform == "omp":
            # 抛出异常：ValueError( "OMP uses native task t…
            raise ValueError(
                "OMP uses native task tool for agent runs; CLI resume is not supported."
            )
        else:
            # 返回 ["claude", "--resume", session_id]
            return ["claude", "--resume", session_id]

    def get_resume_command_str(self, session_id: str, cwd: str | None = None) -> str:
        """
        获取：Get human-readable resume command string.


        参数:
                session_id: Session ID to resume
                cwd: Optional working directory to cd into


        返回:
                Command string for display
            
        """
        # cmd ← 调用 self.build_resume_command
        cmd = self.build_resume_command(session_id)
        # cmd_str ← 调用 " ".join
        cmd_str = " ".join(cmd)

        # 条件分支：cwd
        if cwd:
            return f"cd {cwd} && {cmd_str}"  # 返回格式化字符串
        return cmd_str  # 返回 cmd_str

    # 说明：=========================================================================
    # 平台检测辅助
    # 说明：=========================================================================

    @property
    def is_opencode(self) -> bool:
        """检查/校验：Check if platform is OpenCode."""
        # 返回 self.platform == "opencode"
        return self.platform == "opencode"

    @property
    def is_claude(self) -> bool:
        """检查/校验：Check if platform is Claude Code."""
        # 返回 self.platform == "claude"
        return self.platform == "claude"

    @property
    def is_cursor(self) -> bool:
        """检查/校验：Check if platform is Cursor."""
        # 返回 self.platform == "cursor"
        return self.platform == "cursor"

    @property
    def is_iflow(self) -> bool:
        """检查/校验：Check if platform is iFlow CLI."""
        # 返回 self.platform == "iflow"
        return self.platform == "iflow"

    @property
    def cli_name(self) -> str:
        """
        获取：Get CLI executable name.

            Note: Cursor doesn't have a CLI tool, returns None-like value.
            
        """
        # 条件分支：self.is_opencode
        if self.is_opencode:
            # 返回常量 'opencode'
            return "opencode"
        # 条件分支：self.is_cursor
        elif self.is_cursor:
            # 返回常量 'cursor'
            return "cursor"  # 注意：Cursor 仅 IDE，无 CLI
        # 条件分支：self.platform == "iflow"
        elif self.platform == "iflow":
            # 返回常量 'iflow'
            return "iflow"
        # 条件分支：self.platform == "kiro"
        elif self.platform == "kiro":
            # 返回常量 'kiro'
            return "kiro"
        # 条件分支：self.platform == "gemini"
        elif self.platform == "gemini":
            # 返回常量 'gemini'
            return "gemini"
        # 条件分支：self.platform == "antigravity"
        elif self.platform == "antigravity":
            # 返回常量 'agy'
            return "agy"
        # 条件分支：self.platform == "devin"
        elif self.platform == "devin":
            # 返回常量 'devin'
            return "devin"
        # 条件分支：self.platform == "qoder"
        elif self.platform == "qoder":
            # 返回常量 'qodercli'
            return "qodercli"
        # 条件分支：self.platform == "codebuddy"
        elif self.platform == "codebuddy":
            # 返回常量 'codebuddy'
            return "codebuddy"
        # 条件分支：self.platform == "copilot"
        elif self.platform == "copilot":
            # 返回常量 'copilot'
            return "copilot"
        # 条件分支：self.platform == "droid"
        elif self.platform == "droid":
            # 返回常量 'droid'
            return "droid"
        # 条件分支：self.platform == "pi"
        elif self.platform == "pi":
            # 返回常量 'pi'
            return "pi"
        # 条件分支：self.platform == "omp"
        elif self.platform == "omp":
            # 返回常量 'omp'
            return "omp"
        else:
            # 返回常量 'claude'
            return "claude"

    @property
    def supports_cli_agents(self) -> bool:
        """
        检查/校验：Check if platform supports running agents via CLI.

            Claude Code, OpenCode, iFlow, and Codex support CLI agent execution.
            Cursor is IDE-only and doesn't support CLI agents.
            
        """
        # 返回 self.platform in ("claude", "openco…
        return self.platform in ("claude", "opencode", "iflow", "codex", "pi")

    @property
    def requires_agent_definition_file(self) -> bool:
        """
        检查/校验：Check if platform requires an agent definition file (.md/.toml) to run.

            Claude Code, OpenCode, iFlow: require agent .md files (--agent flag).
            Codex: auto-discovers agents from .codex/agents/*.toml, no --agent flag.
            
        """
        # 返回 self.platform in ("claude", "openco…
        return self.platform in ("claude", "opencode", "iflow")

    # 说明：=========================================================================
    # Session ID 处理
    # 说明：=========================================================================

    @property
    def supports_session_id_on_create(self) -> bool:
        """
        检查/校验：Check if platform supports specifying session ID on creation.

            Claude Code: Yes (--session-id)
            OpenCode: No (auto-generated, extract from logs)
            iFlow: No (no session ID support)
            
        """
        # 返回 self.platform == "claude"
        return self.platform == "claude"

    def extract_session_id_from_log(self, log_content: str) -> str | None:
        """
        extract_session_id_from_log：Extract session ID from log output (OpenCode only).

            OpenCode generates session IDs in format: ses_xxx


        参数:
                log_content: Log file content


        返回:
                Session ID if found, None otherwise
            
        """
        # 局部导入 re
        import re

        # OpenCode session ID 模式
        # match ← 调用 re.search
        match = re.search(r"ses_[a-zA-Z0-9]+", log_content)
        # 条件分支：match
        if match:
            # 返回 match.group 的调用结果
            return match.group(0)
        return None  # 返回 None


# 说明：=============================================================================
# 工厂函数
# 说明：=============================================================================


def get_cli_adapter(platform: str = "claude") -> CLIAdapter:
    """
    获取：Get CLI adapter for the specified platform.


    参数:
        platform: Platform name ('claude', 'opencode', 'cursor', 'iflow', 'codex', 'kilo', 'kiro', 'gemini', 'antigravity', 'devin', 'qoder', 'codebuddy', 'copilot', 'droid', or 'pi')


    返回:
        CLIAdapter instance


    异常:
        ValueError: If platform is not supported


    说明:
        'windsurf' is accepted as a deprecated alias for 'devin' (Windsurf was
        renamed to Devin) and normalized before validation.
    """
    # 废弃别名：Windsurf 已更名为 Devin
    # 条件分支：platform == "windsurf"
    if platform == "windsurf":
        # 初始化 platform
        platform = "devin"
    # 条件分支：platform not in ( "claude", "opencode", "…
    if platform not in (
        "claude",
        "opencode",
        "cursor",
        "iflow",
        "codex",
        "kilo",
        "kiro",
        "gemini",
        "antigravity",
        "devin",
        "qoder",
        "codebuddy",
        "copilot",
        "droid",
        "pi",
        "omp",
    ):
        # 抛出异常：ValueError( f"Unsupported platform:…
        raise ValueError(
            f"Unsupported platform: {platform} (must be 'claude', 'opencode', 'cursor', 'iflow', 'codex', 'kilo', 'kiro', 'gemini', 'antigravity', 'devin', 'qoder', 'codebuddy', 'copilot', 'droid', 'pi', or 'omp')"
        )

    # 返回 CLIAdapter 的调用结果
    return CLIAdapter(platform=platform)  # type: ignore


# 打包元组赋给 _ALL_PLATFORM_CONFI…
_ALL_PLATFORM_CONFIG_DIRS = (
    ".claude",
    ".cursor",
    ".iflow",
    ".opencode",
    ".codex",
    ".kilocode",
    ".kiro",
    ".gemini",
    ".agent",
    ".devin",
    ".windsurf",  # 废弃：更名前的 Devin 配置目录（仍作平台信号）
    ".qoder",
    ".codebuddy",
    ".github/copilot",
    ".factory",
    ".pi",
    ".omp",
)
"""Platform-specific config directory names used by detect_platform exclusion
checks. `.agents/skills/` is NOT listed here: it is a shared cross-platform
layer (written by Codex, also consumed by Amp/Cline/Warp/etc. via the
agentskills.io standard), not a single-platform signal. Its presence must not
block detection of Kiro, Antigravity, Devin, or other platforms."""


def _has_other_platform_dir(project_root: Path, exclude: set[str]) -> bool:
    """检查/校验：Check if any platform config dir exists besides those in *exclude*."""
    # 返回 any 的调用结果
    return any(
        (project_root / d).is_dir()
        for d in _ALL_PLATFORM_CONFIG_DIRS
        if d not in exclude
    )


def detect_platform(project_root: Path) -> Platform:
    """
    detect_platform：Auto-detect platform based on existing config directories.

    Detection order:
    1. TRELLIS_PLATFORM environment variable (if set)
    2. .opencode directory exists → opencode
    3. .iflow directory exists → iflow
    4. .cursor directory exists (without .claude) → cursor
    5. .codex exists and no other platform dirs → codex
    6. .kilocode directory exists → kilo
    7. .kiro/skills exists and no other platform dirs → kiro
    8. .gemini directory exists → gemini
    9. .agent/workflows exists and no other platform dirs → antigravity
    10. .devin/workflows (or legacy .windsurf/workflows) exists and no other platform dirs → devin
    11. .codebuddy directory exists → codebuddy
    12. .qoder directory exists → qoder
    13. .pi directory exists → pi
    14. Default → claude


    参数:
        project_root: Project root directory


    返回:
        Detected platform ('claude', 'opencode', 'cursor', 'iflow', 'codex', 'kilo', 'kiro', 'gemini', 'antigravity', 'devin', 'qoder', 'codebuddy', 'copilot', 'droid', 'pi', or default 'claude')
    """
    # 局部导入 os
    import os

    # 优先检查环境变量
    # env_platform ← 调用 os.environ.get("TRELLIS_PLATF…
    env_platform = os.environ.get("TRELLIS_PLATFORM", "").lower()
    # 废弃别名：Windsurf 已更名为 Devin
    # 条件分支：env_platform == "windsurf"
    if env_platform == "windsurf":
        # 初始化 env_platform
        env_platform = "devin"
    # 条件分支：env_platform in ( "claude", "opencode", "…
    if env_platform in (
        "claude",
        "opencode",
        "cursor",
        "iflow",
        "codex",
        "kilo",
        "kiro",
        "gemini",
        "antigravity",
        "devin",
        "qoder",
        "codebuddy",
        "copilot",
        "droid",
        "pi",
        "omp",
    ):
        return env_platform  # 返回 env_platform # type: ignore

    # 检查 .opencode 目录（OpenCode）
    # 条件分支：(project_root / ".opencode").is_dir()
    if (project_root / ".opencode").is_dir():
        # 返回常量 'opencode'
        return "opencode"

    # 检查 .iflow 目录（iFlow）
    # 条件分支：(project_root / ".iflow").is_dir()
    if (project_root / ".iflow").is_dir():
        # 返回常量 'iflow'
        return "iflow"

    # 检查 .cursor 目录（Cursor）
    # 仅在不存在 .claude 时识别为 cursor（避免混淆）
    # 条件分支：(project_root / ".cursor").is_dir() and n…
    if (project_root / ".cursor").is_dir() and not (project_root / ".claude").is_dir():
        # 返回常量 'cursor'
        return "cursor"

    # 检查 .gemini 目录（Gemini CLI）
    # 条件分支：(project_root / ".gemini").is_dir()
    if (project_root / ".gemini").is_dir():
        # 返回常量 'gemini'
        return "gemini"

    # 检查 .codex 目录（Codex）
    # 仅有 .agents/skills/ 不会触发 codex 检测（共享约定）
    # 条件分支：(project_root / ".codex").is_dir() and no…
    if (project_root / ".codex").is_dir() and not _has_other_platform_dir(
        project_root, {".codex", ".agents"}
    ):
        # 返回常量 'codex'
        return "codex"

    # 检查 .kilocode 目录（Kilo）
    # 条件分支：(project_root / ".kilocode").is_dir()
    if (project_root / ".kilocode").is_dir():
        # 返回常量 'kilo'
        return "kilo"

    # 仅当无其它平台配置时检查 Kiro skills 目录
    # 条件分支：(project_root / ".kiro" / "skills").is_di…
    if (project_root / ".kiro" / "skills").is_dir() and not _has_other_platform_dir(
        project_root, {".kiro"}
    ):
        # 返回常量 'kiro'
        return "kiro"

    # 仅当无其它平台配置时检查 Antigravity workflow 目录
    # 条件分支：( project_root / ".agent" / "workflows" )…
    if (
        project_root / ".agent" / "workflows"
    ).is_dir() and not _has_other_platform_dir(
        project_root, {".agent", ".gemini"}
    ):
        # 返回常量 'antigravity'
        return "antigravity"

    # 仅当无其它平台配置时检查 Devin workflow 目录
    # 存在。`.windsurf/workflows` 为更名前遗留路径（仍识别
    # 为 devin 以保持兼容，直至用户执行 `trellis update --migrate`）
    # 条件分支：( (project_root / ".devin" / "workflows")…
    if (
        (project_root / ".devin" / "workflows").is_dir()
        or (project_root / ".windsurf" / "workflows").is_dir()
    ) and not _has_other_platform_dir(
        project_root, {".devin", ".windsurf"}
    ):
        # 返回常量 'devin'
        return "devin"

    # 检查 .codebuddy 目录（CodeBuddy）
    # 条件分支：(project_root / ".codebuddy").is_dir()
    if (project_root / ".codebuddy").is_dir():
        # 返回常量 'codebuddy'
        return "codebuddy"

    # 检查 .qoder 目录（Qoder）
    # 条件分支：(project_root / ".qoder").is_dir()
    if (project_root / ".qoder").is_dir():
        # 返回常量 'qoder'
        return "qoder"

    # 检查 .github/copilot 目录（GitHub Copilot）
    # 条件分支：(project_root / ".github" / "copilot").is…
    if (project_root / ".github" / "copilot").is_dir():
        # 返回常量 'copilot'
        return "copilot"

    # 检查 .factory 目录（Factory Droid）
    # 条件分支：(project_root / ".factory").is_dir()
    if (project_root / ".factory").is_dir():
        # 返回常量 'droid'
        return "droid"

    # 检查 .pi 目录（Pi Agent）
    # 条件分支：(project_root / ".pi").is_dir()
    if (project_root / ".pi").is_dir():
        # 返回常量 'pi'
        return "pi"

    # 检查 .omp 目录（OMP）
    # 条件分支：(project_root / ".omp").is_dir()
    if (project_root / ".omp").is_dir():
        # 返回常量 'omp'
        return "omp"

    # 回退：检出仅含 Codex 共享 skills 层
    # （.agents/skills/trellis-* 目录）且无显式平台配置目录
    # 出现在新鲜克隆：.codex/ 被 gitignore 或不存在，但
    # 共享 skills 已提交到 git。必须防止这种情况：
    # 同时存在 .claude/ 或其它平台目录——.agents/skills/
    # 可与任意平台合法共存，作为共享消费
    # 层（Amp/Cline/Warp 等）。
    # 计算后赋给 agents_skills
    agents_skills = project_root / ".agents" / "skills"
    # 条件分支：agents_skills.is_dir() and not _has_other…
    if agents_skills.is_dir() and not _has_other_platform_dir(
        project_root, set()
    ):
        # try：执行可能失败的逻辑
        try:
            # 遍历：entry in agents_skills.iterdir()
            for entry in agents_skills.iterdir():
                # 条件分支：entry.is_dir() and entry.name.startswith(…
                if entry.is_dir() and entry.name.startswith("trellis-"):
                    # 返回常量 'codex'
                    return "codex"
        except OSError:
            # 占位（无操作）
            pass

    # 返回常量 'claude'
    return "claude"


def get_cli_adapter_auto(project_root: Path) -> CLIAdapter:
    """
    获取：Get CLI adapter with auto-detected platform.


    参数:
        project_root: Project root directory


    返回:
        CLIAdapter instance for detected platform
    """
    # platform ← 调用 detect_platform
    platform = detect_platform(project_root)
    # 返回 CLIAdapter 的调用结果
    return CLIAdapter(platform=platform)
