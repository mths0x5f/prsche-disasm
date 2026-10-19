#include "0053c290.hpp"
#include <mmintrin.h>

namespace porsche {

// Original Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// 0053c290..0053c2dc: borrowed dispatch order from PR #7
// a349d056a0dc981b770e34121c5d2b5476295393, corrected to canonical
// heap_fill ABI/storage and original fill-callee roles.
void __cdecl heap_fill_0053c290(void* destination, std::uint32_t value, std::uint32_t bytes) {
    if (copy_flag_005deb1c != 0) {
        heap_fill_sse_005b0b00(destination, value, bytes);
        return;
    }
    if (copy_flag_005deb18 != 0) {
        heap_fill_mmx_005b0a40(destination, value, bytes);
        _mm_empty();
        return;
    }
    heap_fill_scalar_005b0980(destination, value, bytes);
}

} // namespace porsche
