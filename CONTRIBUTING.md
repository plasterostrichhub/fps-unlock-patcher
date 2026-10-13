# Contributing

## Setup

    python -m venv .venv
    .venv\Scripts\activate
    pip install -e ".[dev]"

## Layout

- `src/fps_unlock/` — the patcher package. Services own logic, handlers stay thin.
- `tools/fps_unlock_native/` — optional C++ Present hook helper.
- `tests/` — pytest. Every service gets at least one test.

## Adding an engine adapter

1. Add the `EngineKind` value in `models/engine.py`.
2. Add a detection needle in `ScanService._fingerprint`.
3. Implement a `PatchAdapter` in `platform/adapters.py`.
4. Wire it into `pick_adapter`.
5. Add a test that the adapter returns the ops from a fake `PatchPlan`.

## Style

`ruff` + `mypy --strict` on `src/`. Run before pushing:

    ruff check src tests
    mypy src
    pytest

## Commit messages

Short, imperative. `scan: detect gamemaker YoYo signature`, not
`added detection for gamemaker`.