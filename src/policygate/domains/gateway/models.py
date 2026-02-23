"""Domain models for repository routing configuration."""

from pydantic import BaseModel, Field


class TaskConfig(BaseModel):
    """Task mapping in router configuration."""

    description: str = Field(description="Task description")
    rules: list[str] = Field(default_factory=list, description="Rule aliases")
    scripts: list[str] = Field(default_factory=list, description="Script aliases")


class RuleConfig(BaseModel):
    """Rule descriptor from router configuration."""

    path: str = Field(description="Relative path to markdown rule file")
    description: str = Field(description="Rule description")


class ScriptConfig(BaseModel):
    """Script descriptor from router configuration."""

    path: str = Field(description="Relative path to script file")
    description: str = Field(description="Script description")


class RouterConfig(BaseModel):
    """Top-level router.yaml document."""

    tasks: dict[str, TaskConfig] = Field(default_factory=dict)
    rules: dict[str, RuleConfig] = Field(default_factory=dict)
    scripts: dict[str, ScriptConfig] = Field(default_factory=dict)


class CopiedScriptsResult(BaseModel):
    """Result payload for copied scripts."""

    destination_directory: str
    copied_files: list[str] = Field(default_factory=list)
