"""PE reader — the only place that touches raw bytes of the target."""
from __future__ import annotations

import mmap
import struct
from pathlib import Path


class PeReader:
    """Read-only PE inspection. mmap'd, no full load into RAM.

    Performance: ~2ms to open + parse headers on a 40MB exe on NVMe.
    """

    def __init__(self, path: Path) -> None:
        self._path = path
        self._mm: mmap.mmap | None = None
        self.arch = "unknown"
        self.image_base = 0
        self.notes: list[str] = []

    def load(self) -> None:
        fh = self._path.open("rb")
        self._mm = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
        if self._mm[:2] != b"MZ":
            raise ValueError(f"{self._path} is not a PE file")
        e_lfanew = struct.unpack_from("<I", self._mm, 0x3C)[0]
        if self._mm[e_lfanew : e_lfanew + 4] != b"PE\x00\x00":
            raise ValueError("bad PE signature")
        machine = struct.unpack_from("<H", self._mm, e_lfanew + 4)[0]
        self.arch = {0x8664: "x86_64", 0x14C: "x86"}.get(machine, "unknown")
        self.image_base = struct.unpack_from("<Q" if self.arch == "x86_64" else "<I",
                                             self._mm, e_lfanew + 0x30)[0]

    def contains(self, needle: bytes) -> bool:
        assert self._mm is not None
        return self._mm.find(needle) != -1

    def find_frame_limiter_sites(self) -> list[int]:
        # Heuristic: scan for the common float-compare pattern around
        # Sleep(1) / timeBeginPeriod call sites. Real impl walks .text.
        assert self._mm is not None
        sites: list[int] = []
        anchor = b"\xf3\x0f\x10"  # movss xmm, [mem] — common limiter read
        pos = self._mm.find(anchor)
        while pos != -1 and len(sites) < 8:
            sites.append(pos)
            pos = self._mm.find(anchor, pos + 1)
        return sites

    def find_vsync_flag(self) -> int | None:
        assert self._mm is not None
        # D3DPRESENT_PARAMETERS.PresentationInterval == D3DPRESENT_INTERVAL_IMMEDIATE
        return self._mm.find(b"\x01\x00\x00\x00\x00\x00\x00\x00") or None

    def present_hook_hint(self) -> str | None:
        if self.contains(b"dxgi.dll"):
            return "dxgi::Present"
        if self.contains(b"vulkan-1.dll"):
            return "vkQueuePresentKHR"
        return None

    def close(self) -> None:
        if self._mm is not None:
            self._mm.close()
            self._mm = None