#include "resource_constructor_329.hpp"

namespace porsche {
namespace {

// The original constructor pushes all 32 group bits, while 005682a0 reads
// only its low byte (00568309). Preserve that physical cdecl argument slot
// without changing the accepted allocator's uint8_t declaration or owner.
// This is an x86 transport adapter, not a second original allocator body.
FileOperation* allocate_with_group_word(
    std::uint32_t group_word, void* context_arg, std::uint32_t device_arg) {
    FileOperation* operation_result;
    __asm {
        push device_arg
        push context_arg
        push group_word
        push 6
        call operation_allocate_005682a0
        add esp, 16
        mov operation_result, eax
    }
    return operation_result;
}

} // namespace

// Porsche.exe SHA256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// 00568260..00568292, 51 bytes. Retain the allocation pointer across naming;
// name and queue are called even if it is null. Queue's raw EAX is returned.
std::uint32_t __cdecl request_exists_00568260(
    const char* path, std::uint32_t group, void* context) {
    const auto device = file_device_name_00568e90(path);
    auto* operation = allocate_with_group_word(group, context, device);
    operation_name_005684e0(operation, path);
    return operation_queue_00568200(operation);
}

} // namespace porsche
