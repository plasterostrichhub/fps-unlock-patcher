"""Frame profile — a named, reusable patch recipe."""
from __future__ import annotations

from pydantic import BaseModel, Field


class FrameProfile(BaseModel):
    name: str
    engine: str
    target_fps: int = 0
    vsync_off: bool = True
    present_hook: str | None = None
    extra_config: dict[str, str] = Field(default_factory=dict)
    description: str = ""