#define WIN32_LEAN_AND_MEAN
#include <windows.h>

namespace porsche {
// Original IAT005b2208 imports this exact KERNEL32 stdcall API. Modern
// platform binding only; no emulated console/debugger behavior is supplied.
void __stdcall application_diagnostic_output_debug_string(const char* message) {
    ::OutputDebugStringA(message);
}
}
