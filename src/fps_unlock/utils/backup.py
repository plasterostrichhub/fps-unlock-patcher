"""Backup manager — snapshot before every write, never destructive."""
from __future__ import annotations

import shutil
import time
from pathlib import Path


class BackupManager:
    def __init__(self, backup_dir: Path) -> None:
        self._dir = backup_dir
        self._dir.mkdir(parents=True, exist_ok=True)

    def snapshot(self, target: Path) -> Path:
        stamp = time.strftime("%Y%m%d-%H%M%S")
        dest = self._dir / f"{target.stem}.{stamp}{target.suffix}.bak"
        shutil.copy2(target, dest)
        return dest

    def restore(self, backup: Path, target: Path) -> None:
        shutil.copy2(backup, target)