"""Thin handler around PatchService — no business logic here."""
from __future__ import annotations

from pathlib import Path

from fps_unlock.config.schema import AppConfig
from fps_unlock.models.patch import PatchResult
from fps_unlock.services.patch_service import PatchService


class PatchHandler:
    def __init__(self, config: AppConfig) -> None:
        self._service = PatchService(config)

    def handle(self, target: Path, target_fps: int, profile: str) -> PatchResult:
        return self._service.patch(target, target_fps, profile)