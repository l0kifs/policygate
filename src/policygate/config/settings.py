from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration settings.
    """

    model_config = SettingsConfigDict(
        env_prefix="POLICYGATE__",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application settings
    app_name: str = Field(default="policygate", description="Application name")
    app_version: str = Field(default="0.1.1", description="Application version")

    # GitHub repository integration
    github_repository_url: str = Field(
        default="",
        description="GitHub repository URL containing router.yaml, rules/, and scripts/",
    )
    github_access_token: str = Field(
        default="",
        description="GitHub access token for repository access",
    )

    # Local repository cache
    local_repo_data_dir: str = Field(
        default="~/.policygate/repo_data",
        description="Local repository cache path",
    )
    repository_refresh_interval_seconds: int = Field(
        default=1800,
        description="Minimal interval between remote refresh checks",
    )


def get_settings() -> Settings:
    """
    Get configuration settings.
    """
    return Settings()
