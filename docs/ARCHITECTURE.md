# Architecture

Service-oriented. Thin handlers at the edge (`handlers/`), business logic in
`services/`, data shapes in `models/`, platform-specific byte-poking isolated
in `platform/`. Nothing in `services/` opens a file handle on the target
except through `platform/pe_reader.py` and the adapters.

## Layers

- **entry/bootstrap** — `cli.py`. Parses args, loads config, delegates. No logic.
- **handlers** — `handlers/`. Thin wrappers for embedding the patcher in other tools.
- **services** — `services/`. ScanService, PatchService, ProfileService. All business logic.
- **models** — `models/`. Pydantic. EngineFingerprint, PatchPlan, PatchResult, FrameProfile.
- **platform** — `platform/`. PeReader (read-only mmap), adapters (one per engine).
- **utils** — `utils/`. BackupManager, logger factory.
- **config** — `config/`. TOML loader, pydantic schema.

## Data flow

    cli.patch -> PatchService.patch
        -> ProfileService.load
        -> ScanService.scan -> PeReader
        -> _build_plan -> PatchPlan
        -> BackupManager.snapshot
        -> pick_adapter(engine).apply(plan)
        -> PatchResult

## Invariants

- Every write is preceded by a backup unless `patch.always_backup = false`.
- `PatchService.patch` never raises — returns `PatchResult(ok=False, error=...)`.
- `PeReader` is read-only. Only adapters open the target for writing.