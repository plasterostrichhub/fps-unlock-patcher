"""Config schema. Defaults are sane for a fresh install."""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class PathsConfig(BaseModel):
    profiles_dir: Path = Path("profiles")
    backup_dir: Path = Path("backups")
    log_dir: Path = Path("logs")


class PatchConfig(BaseModel):
    default_target_fps: int = 0
    always_backup: bool = True
    dry_run: bool = False


class AppConfig(BaseModel):
    paths: PathsConfig = Field(default_factory=PathsConfig)
    patch: PatchConfig = Field(default_factory=PatchConfig)
    verbosity: str = "info"