# Patching notes

## Frame limiter sites

Most engines cap FPS in one of three places:

1. **Hardcoded float compare** in the present loop — a `movss` load of a
   constant, compared against elapsed time. Patch the constant, or NOP the
   branch.
2. **Config value** — engine reads `FrameRateLimit=60` from an ini/json at
   startup. Patcher writes the config and the engine respects it.
3. **Vsync** — `D3DPRESENT_INTERVAL_DEFAULT` forces the monitor refresh.
   Flip to `D3DPRESENT_INTERVAL_IMMEDIATE` or NOP the wait.

`ScanService` reports which of the three it found per binary.

## Vsync unlock

`PatchOp.NOP_VSYNC_WAIT` writes `0x90` over the wait branch. On DXGI titles
this is usually a jump over the `WaitForVBlank` call; on Vulkan it's the
`vkWaitForFences` timeout.

## Present hook

When in-place patching fails (protected sections, packed binaries), fall
back to `HOOK_PRESENT` — load `fps_unlock_native.dll` and let it throttle
or unthrottle at the Present call. See `tools/fps_unlock_native/`.

## Rollback

Every patch writes a `.bak` next to the config's `backup_dir`. Restore with
`PatchService` -> `BackupManager.restore`, or manually copy the `.bak` back
over the exe.