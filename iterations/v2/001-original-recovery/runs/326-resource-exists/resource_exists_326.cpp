#include "resource_exists_326.hpp"

namespace porsche {

// Porsche.exe SHA256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// Indexed 00561b80..00561b93, 20 bytes. The group is read for each invocation.
std::int32_t __cdecl file_exists_00561b80(const char* path) {
    return resource_exists_request_00533f00(path, resource_leaf_group_005df770);
}

// Indexed 00533f00..00533f33, 52 bytes. ESI retains the request ID across wait;
// the wait result is ignored and EAX from completion is returned without a
// boolean conversion. Constructor/context and OS/queue behavior remain open.
std::int32_t __cdecl resource_exists_request_00533f00(
    const char* path, std::uint32_t group) {
    const auto id = request_exists_00568260(path, group, nullptr);
    if (id == 0) return 0;
    file_wait_00567f70(id);
    return static_cast<std::int32_t>(operation_complete_00567df0(id));
}

} // namespace porsche
