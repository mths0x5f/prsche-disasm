#include "../348-diagnostic-parsers/diagnostic_parsers.hpp"
#include "porsche/formatter_crt_runtime.hpp"
#include <cstdint>
#include <cstring>

namespace porsche {
// Porsche.exe SHA256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39,
// 005a30ee..005a3191. The continuation belongs to the shared CRT TLS block.
char* __cdecl application_diagnostic_tokenize_005a30ee(char* input,
    const char* separators) {
    auto* tls = static_cast<std::uint8_t*>(formatter_crt_thread_005a545c());
    std::uint8_t bits[32]{};
    const auto* cursor = reinterpret_cast<const std::uint8_t*>(separators);
    for (;;) {
        const std::uint8_t byte = *cursor++;
        bits[byte >> 3] |= static_cast<std::uint8_t>(1u << (byte & 7u));
        if (byte == 0) break;
    }
    char* current = input;
    if (current == nullptr) std::memcpy(&current,tls+0x18,sizeof(current));
    for (;;) {
        const auto byte = static_cast<std::uint8_t>(*current);
        if (byte == 0 || (bits[byte >> 3] & (1u << (byte & 7u))) == 0) break;
        ++current;
    }
    char* begin = current;
    for (;;) {
        const auto byte = static_cast<std::uint8_t>(*current);
        if (byte == 0) break;
        if ((bits[byte >> 3] & (1u << (byte & 7u))) != 0) {
            *current++ = 0;
            break;
        }
        ++current;
    }
    std::memcpy(tls+0x18,&current,sizeof(current));
    return begin == current ? nullptr : begin;
}
}
