"""Thin handlers — parse input, call a service, format output. No logic."""
from fps_unlock.handlers.scan_handler import ScanHandler
from fps_unlock.handlers.patch_handler import PatchHandler

__all__ = ["ScanHandler", "PatchHandler"]