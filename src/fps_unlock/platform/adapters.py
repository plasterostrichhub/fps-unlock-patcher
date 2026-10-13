"""Platform adapters — one per engine family. All implement PatchAdapter."""
from __future__ import annotations

from typing import Protocol

from fps_unlock.models.engine import EngineKind
from fps_unlock.models.patch import PatchOp, PatchPlan


class PatchAdapter(Protocol):
    def apply(self, plan: PatchPlan) -> list[PatchOp]: ...


class UnrealAdapter:
    def apply(self, plan: PatchPlan) -> list[PatchOp]:
        return _write_ops(plan)


class UnityAdapter:
    def apply(self, plan: PatchPlan) -> list[PatchOp]:
        return _write_ops(plan)


class GenericDxAdapter:
    def apply(self, plan: PatchPlan) -> list[PatchOp]:
        return _write_ops(plan)


def _write_ops(plan: PatchPlan) -> list[PatchOp]:
    # Real impl: open target RW, seek each rva, write bytes, flush.
    # Kept as a thin stub so the adapter contract is testable.
    return list(plan.ops)


def pick_adapter(engine: EngineKind) -> PatchAdapter:
    return {
        EngineKind.UNREAL: UnrealAdapter,
        EngineKind.UNITY: UnityAdapter,
        EngineKind.SOURCE2: GenericDxAdapter,
        EngineKind.GAMEMAKER: GenericDxAdapter,
        EngineKind.CUSTOM_DX: GenericDxAdapter,
        EngineKind.CUSTOM_VK: GenericDxAdapter,
    }.get(engine, GenericDxAdapter)()