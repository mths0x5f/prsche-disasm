#include "shutdown_helpers_311.hpp"

namespace porsche {

void __cdecl application_main_function_004a54b0() {
    (void)install_paths_cleanup_004b7070();
    void* const network = startup_network_00628c70;
    if (network != nullptr) {
        static_cast<ShutdownNetwork311*>(network)->destroy_0048ff30();
        (void)application_release_0059f050(network);
        startup_network_00628c70 = nullptr;
    }
}

// Original 004a54e0 is a five-byte tail jump, preserving its caller's return
// address for the unrecovered 0059eb20 boundary.
#if defined(_MSC_VER) && defined(_M_IX86)
__declspec(naked) void __cdecl application_main_function_004a54e0() {
    __asm jmp platform_flush_0059eb20
}
#else
void __cdecl application_main_function_004a54e0() {
    platform_flush_0059eb20();
}
#endif

} // namespace porsche
