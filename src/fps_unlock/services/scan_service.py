"""Scan service — fingerprint a game binary, locate frame limiter sites."""
from __future__ import annotations

from pathlib import Path

from fps_unlock.config.schema import AppConfig
from fps_unlock.models.engine import EngineFingerprint
from fps_unlock.platform.pe_reader import PeReader
from fps_unlock.utils.logging import get_logger

log = get_logger(__name__)


class ScanService:
    """Reads a PE, detects engine, returns an EngineFingerprint.

    Side effects: none (read-only). Raises FileNotFoundError if target missing.
    """

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def scan(self, target: Path) -> EngineFingerprint:
        log.info("scanning %s", target)
        pe = PeReader(target)
        pe.load()
        engine, confidence = self._fingerprint(pe)
        return EngineFingerprint(
            engine=engine,
            confidence=confidence,
            pe_arch=pe.arch,
            image_base=pe.image_base,
            frame_limiter_rvas=pe.find_frame_limiter_sites(),
            vsync_flag_offset=pe.find_vsync_flag(),
            present_hook_hint=pe.present_hook_hint(),
            notes=pe.notes,
        )

    def _fingerprint(self, pe: PeReader):
        for needle, kind, conf in (
            (b"UnrealEngine", "unreal", 0.95),
            (b"UnityPlayer", "unity", 0.95),
            (b"Source2", "source2", 0.9),
            (b"YoYo Games", "gamemaker", 0.85),
        ):
            if pe.contains(needle):
                from fps_unlock.models.engine import EngineKind

                return EngineKind(kind), conf
        from fps_unlock.models.engine import EngineKind

        return EngineKind.UNKNOWN, 0.2