"""Profile service — CRUD over FrameProfile TOML files."""
from __future__ import annotations

from pathlib import Path

import tomli_w
import tomllib

from fps_unlock.config.schema import AppConfig
from fps_unlock.models.profile import FrameProfile


class ProfileService:
    def __init__(self, config: AppConfig) -> None:
        self._dir = config.paths.profiles_dir
        self._dir.mkdir(parents=True, exist_ok=True)

    def list_profiles(self) -> list[FrameProfile]:
        return [self._read(p) for p in sorted(self._dir.glob("*.toml"))]

    def load(self, name: str) -> FrameProfile:
        path = self._dir / f"{name}.toml"
        if not path.is_file():
            return FrameProfile(name=name, engine="unknown", target_fps=0)
        return self._read(path)

    def save(self, profile: FrameProfile) -> Path:
        path = self._dir / f"{profile.name}.toml"
        with path.open("wb") as fh:
            tomli_w.dump(profile.model_dump(mode="json"), fh)
        return path

    def _read(self, path: Path) -> FrameProfile:
        with path.open("rb") as fh:
            return FrameProfile.model_validate(tomllib.load(fh))