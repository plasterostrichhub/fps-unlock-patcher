"""Patch service tests — plan shape, dry-run, backup path."""
from __future__ import annotations

from pathlib import Path

import pytest

from fps_unlock.config.schema import AppConfig, PatchConfig, PathsConfig
from fps_unlock.services.patch_service import PatchService


@pytest.fixture()
def config(tmp_path: Path) -> AppConfig:
    return AppConfig(
        paths=PathsConfig(
            profiles_dir=tmp_path / "profiles",
            backup_dir=tmp_path / "backups",
            log_dir=tmp_path / "logs",
        ),
        patch=PatchConfig(always_backup=True, dry_run=False),
    )


def test_dry_run_returns_ok_without_writing(config: AppConfig, tmp_path: Path) -> None:
    config.patch.dry_run = True
    target = tmp_path / "game.exe"
    target.write_bytes(b"MZ" + b"\x00" * 0x100)
    result = PatchService(config).patch(target, target_fps=0, profile_name="default")
    assert result.ok is True
    assert result.applied_ops == []


def test_backup_created_before_patch(config: AppConfig, tmp_path: Path) -> None:
    target = tmp_path / "game.exe"
    target.write_bytes(b"MZ" + b"\x00" * 0x100)
    result = PatchService(config).patch(target, target_fps=144, profile_name="default")
    assert result.backup_path is not None
    assert Path(result.backup_path).is_file()