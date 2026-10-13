"""Config loader — TOML on disk, pydantic in memory."""
from __future__ import annotations

import tomllib
from pathlib import Path

from fps_unlock.config.schema import AppConfig

DEFAULT_CONFIG_PATHS = (
    Path("fps-unlock.toml"),
    Path.home() / ".config" / "fps-unlock" / "config.toml",
)


def load_config(path: Path | None = None) -> AppConfig:
    candidates = [path] if path else list(DEFAULT_CONFIG_PATHS)
    for candidate in candidates:
        if candidate and candidate.is_file():
            with candidate.open("rb") as fh:
                return AppConfig.model_validate(tomllib.load(fh))
    return AppConfig()