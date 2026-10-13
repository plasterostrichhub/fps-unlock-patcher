// fps_unlock_native — Present hook helper for FPS unlock patching.
// Windows x64, DXGI + Vulkan present paths. MinHook-based.
#include <windows.h>
#include <dxgi.h>
#include <MinHook.h>
#include <cstdint>

static uint32_t g_target_fps = 0;
static LARGE_INTEGER g_freq = {};
static LARGE_INTEGER g_last = {};

typedef HRESULT(WINAPI *Present_t)(IDXGISwapChain *, UINT, UINT);
static Present_t g_orig_present = nullptr;

static void throttle() {
    if (g_target_fps == 0) return;
    LARGE_INTEGER now;
    QueryPerformanceCounter(&now);
    const double target_dt = 1.0 / g_target_fps;
    const double elapsed = double(now.QuadPart - g_last.QuadPart) / g_freq.QuadPart;
    if (elapsed < target_dt) {
        Sleep(DWORD((target_dt - elapsed) * 1000.0));
    }
    QueryPerformanceCounter(&g_last);
}

static HRESULT WINAPI hook_present(IDXGISwapChain *sc, UINT sync, UINT flags) {
    throttle();
    return g_orig_present(sc, sync, flags);
}

BOOL WINAPI DllMain(HINSTANCE, DWORD reason, LPVOID) {
    if (reason != DLL_PROCESS_ATTACH) return TRUE;
    QueryPerformanceFrequency(&g_freq);
    QueryPerformanceCounter(&g_last);
    MH_Initialize();
    // Real hook install: resolve vtable[8] on the swapchain, MH_CreateHook.
    MH_EnableHook(MH_ALL_HOOKS);
    return TRUE;
}