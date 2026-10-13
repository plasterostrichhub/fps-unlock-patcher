"""Patch plan/result models — the service layer speaks in these."""
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class PatchOp(StrEnum):
    NOP_VSYNC_WAIT = "nop_vsync_wait"
    PATCH_FRAMELIMIT_CONST = "patch_framelimit_const"
    HOOK_PRESENT = "hook_present"
    WRITE_CONFIG = "write_config"
    BACKUP = "backup"


class PatchPlan(BaseModel):
    """Ordered ops to apply. Built by PatchService, executed by adapters."""

    target: str
    target_fps: int
    ops: list[PatchOp]
    rva_writes: dict[int, bytes] = Field(default_factory=dict)
    config_overrides: dict[str, str] = Field(default_factory=dict)
    backup_path: str | None = None


class PatchResult(BaseModel):
    ok: bool
    target: str
    applied_ops: list[PatchOp]
    backup_path: str | None = None
    error: str | None = None
    elapsed_ms: int = 0

    def render(self) -> str:
        if not self.ok:
            return f"[red]patch failed[/red] {self.target}: {self.error}"
        ops = ", ".join(o.value for o in self.applied_ops)
        return (
            f"[green]patched[/green] {self.target}\n"
            f"  ops: {ops}\n"
            f"  backup: {self.backup_path}\n"
            f"  took: {self.elapsed_ms}ms"
        )