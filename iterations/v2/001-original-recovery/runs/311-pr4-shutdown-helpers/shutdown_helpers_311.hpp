#pragma once

#include "porsche/application_alloc.hpp"
#include "porsche/install_paths.hpp"
#include "porsche/startup_services.hpp"

namespace porsche {

// Porsche.exe 0048ff30: ECX is the receiver, RET 0. The callee is still a
// typed external boundary; this package does not claim its implementation.
struct ShutdownNetwork311 {
    void __thiscall destroy_0048ff30();
};

// Porsche.exe 0059eb20 is an unrecovered external boundary.
void __cdecl platform_flush_0059eb20();

void __cdecl application_main_function_004a54b0();
void __cdecl application_main_function_004a54e0();

} // namespace porsche
