"""PE reader tests — header parse, arch detection, bad-file rejection."""
from __future__ import annotations

import struct
from pathlib import Path

import pytest

from fps_unlock.platform.pe_reader import PeReader


def _make_pe(path: Path, machine: int = 0x8664) -> None:
    buf = bytearray(0x200)
    buf[0:2] = b"MZ"
    struct.pack_into("<I", buf, 0x3C, 0x80)
    buf[0x80:0x84] = b"PE\x00\x00"
    struct.pack_into("<H", buf, 0x84, machine)
    struct.pack_into("<Q", buf, 0x80 + 0x30, 0x140000000)
    path.write_bytes(buf)


def test_arch_detected_x64(tmp_path: Path) -> None:
    target = tmp_path / "a.exe"
    _make_pe(target, machine=0x8664)
    pe = PeReader(target)
    pe.load()
    assert pe.arch == "x86_64"
    pe.close()


def test_rejects_non_pe(tmp_path: Path) -> None:
    target = tmp_path / "nope.bin"
    target.write_bytes(b"not a pe")
    with pytest.raises(ValueError):
        PeReader(target).load()