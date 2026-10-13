"""Patch service — build a PatchPlan, dispatch to the right adapter."""
from __future__ import annotations

import time
from pathlib import Path

from fps_unlock.config.schema import AppConfig
from fps_unlock.models.patch import PatchOp, PatchPlan, PatchResult
from fps_unlock.platform.adapters import pick_adapter
from fps_unlock.services.profile_service import ProfileService
from fps_unlock.services.scan_service import ScanService
from fps_unlock.utils.backup import BackupManager
from fps_unlock.utils.logging import get_logger

log = get_logger(__name__)


class PatchService:
    """Orchestrates: scan -> plan -> backup -> apply -> verify."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._scanner = ScanService(config)
        self._profiles = ProfileService(config)
        self._backups = BackupManager(config.paths.backup_dir)

    def patch(self, target: Path, target_fps: int, profile_name: str) -> PatchResult:
        started = time.monotonic()
        try:
            profile = self._profiles.load(profile_name)
            fingerprint = self._scanner.scan(target)
            plan = self._build_plan(target, fingerprint, profile, target_fps)

            if self._config.patch.always_backup:
                plan.backup_path = str(self._backups.snapshot(target))

            if self._config.patch.dry_run:
                log.info("dry-run: plan=%s", plan.ops)
                return PatchResult(ok=True, target=str(target), applied_ops=[],
                                   backup_path=plan.backup_path)

            adapter = pick_adapter(fingerprint.engine)
            applied = adapter.apply(plan)
            return PatchResult(ok=True, target=str(target), applied_ops=applied,
                               backup_path=plan.backup_path,
                               elapsed_ms=int((time.monotonic() - started) * 1000))
        except Exception as exc:  # noqa: BLE001
            log.exception("patch failed")
            return PatchResult(ok=False, target=str(target), applied_ops=[],
                               error=str(exc),
                               elapsed_ms=int((time.monotonic() - started) * 1000))

    def _build_plan(self, target, fingerprint, profile, target_fps) -> PatchPlan:
        fps = target_fps or profile.target_fps or self._config.patch.default_target_fps
        ops: list[PatchOp] = [PatchOp.BACKUP]
        if profile.vsync_off:
            ops.append(PatchOp.NOP_VSYNC_WAIT)
        if fps:
            ops.append(PatchOp.PATCH_FRAMELIMIT_CONST)
        else:
            ops.append(PatchOp.HOOK_PRESENT)
        if profile.extra_config:
            ops.append(PatchOp.WRITE_CONFIG)
        return PatchPlan(
            target=str(target),
            target_fps=fps,
            ops=ops,
            rva_writes={rva: b"\x90" * 6 for rva in fingerprint.frame_limiter_rvas},
            config_overrides=profile.extra_config,
        )