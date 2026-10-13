"""Thin handler around ScanService — for embedding in other tools."""
from __future__ import annotations

from pathlib import Path

from fps_unlock.config.schema import AppConfig
from fps_unlock.models.engine import EngineFingerprint
from fps_unlock.services.scan_service import ScanService


class ScanHandler:
    def __init__(self, config: AppConfig) -> None:
        self._service = ScanService(config)

    def handle(self, target: Path) -> EngineFingerprint:
        return self._service.scan(target)