#pragma once
#include <cstdint>
#include "../345-diagnostic-devices/diagnostic_devices.hpp"

namespace porsche {
void __cdecl application_diagnostic_copy_lower_0055edf0(const char*,char*,std::uint32_t);
std::int32_t __cdecl application_diagnostic_prefix_0055eeb0(const char*,const char*);
std::int32_t __cdecl application_diagnostic_device_lookup_0055ee70(const char*);
std::int32_t __cdecl application_diagnostic_channel_lookup_0055f0f0(const char*);
// Original CRT children, still explicit boundaries. No host substitutions.
char* __cdecl application_diagnostic_tokenize_005a30ee(char*,const char*);
const char* __cdecl application_diagnostic_environment_inner_005a3071(const char*);
}
