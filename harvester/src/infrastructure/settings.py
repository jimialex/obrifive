from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class HarvesterSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HARVESTER_", env_file=".env", extra="ignore")

    data_dir: Path = Field(default=Path(".data/artifacts"))
    inbox_dir: Path = Field(default=Path(".data/inbox"))
    http_timeout_seconds: float = Field(default=30.0, gt=0)
    max_download_bytes: int = Field(default=25 * 1024 * 1024, gt=0)
    user_agent: str = Field(default="ObrifiveHarvester/0.1 (+https://obrifive.com)")
