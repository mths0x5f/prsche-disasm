#include "search_bindings_338.hpp"
#include <cstring>

namespace porsche {

// ABI aliases to existing Run172 original bodies, not new algorithms.
std::int32_t __cdecl compare_005ae3c0(const char* left, const char* right) {
    return formatter_search_compare_005ae3c0(left, right);
}

std::int32_t __cdecl render_settings_read_config_005a1e10(char* text, const char* needle) {
    const char* const found = formatter_search_substring_005a1e10(text, needle);
    static_assert(sizeof(found) == sizeof(std::int32_t), "original x86 EAX view");
    std::int32_t result;
    std::memcpy(&result, &found, sizeof(result));
    return result;
}

} // namespace porsche
