"""Engine fingerprint models — what we detected in the target binary."""
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class EngineKind(StrEnum):
    UNREAL = "unreal"
    UNITY = "unity"
    SOURCE2 = "source2"
    GAMEMAKER = "gamemaker"
    CUSTOM_DX = "custom_dx"
    CUSTOM_VK = "custom_vk"
    UNKNOWN = "unknown"


class EngineFingerprint(BaseModel):
    """Result of a scan. Immutable snapshot of what the binary is."""

    engine: EngineKind
    confidence: float = Field(ge=0.0, le=1.0)
    pe_arch: str
    image_base: int
    frame_limiter_rvas: list[int] = Field(default_factory=list)
    vsync_flag_offset: int | None = None
    present_hook_hint: str | None = None
    notes: list[str] = Field(default_factory=list)