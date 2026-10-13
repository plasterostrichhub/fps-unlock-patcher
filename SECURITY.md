# Security

## Scope

fps-unlock-patcher writes to game binaries. That is the point. Reports about
"the tool modifies executables" are not vulnerabilities — they are the
feature. Read `docs/PATCHING.md` before filing.

## What counts as a vulnerability

- Arbitrary code execution triggered by a crafted target binary (PE parser
  bugs in `platform/pe_reader.py`).
- Backup bypass — a path where a write happens without the pre-write
  snapshot when `always_backup = true`.
- Path traversal in `ProfileService` via a crafted profile name.
- Privilege escalation via the native helper (`tools/fps_unlock_native/`).

## Reporting

Open a draft security advisory on the repository, or email the maintainer