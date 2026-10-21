// Porsche.exe SHA256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// 00561ca0..00561cde(63B);00561ce0..00561df3(276B), supplementary index327.
#include "resource_open_334.hpp"
#include "../313-pr9-resource-open/resource_open_313.hpp"
#include "porsche/fe_stream.hpp"
#include "porsche/shared_runtime_globals.hpp"

#include <cstring>

namespace porsche {
namespace {

std::int32_t pointer_bits(void* pointer) {
    const auto word = static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(pointer));
    std::int32_t result;
    std::memcpy(&result, &word, sizeof(result));
    return result;
}

void diagnostic(std::uint32_t line, const char* format, const char* path) {
    diagnostic_file_005deb74_set("\\real\\cmn\\hlsfile.c");
    diagnostic_line_005deb78 = line;
    // This original consumer pushes two arguments through the canonical cell,
    // whose C++ declaration is also used by one-argument callers. Keep that
    // storage/type unchanged and reproduce the proven x86 stack transport.
    __asm {
        mov eax, path
        push eax
        mov ecx, format
        push ecx
        call dword ptr [diagnostic_handler_005debf0]
        add esp, 8
    }
}

} // namespace

void* __cdecl file_open_00561ca0(const char* path, std::uint32_t flags) {
    ResourceAtomicContext context; // +04 is deliberately uninitialized/unread.
    context.path = path;
    context.opaque_08 = flags;
    const std::uint32_t group = resource_leaf_group_005df770;
    context.callback_diagnostic_flag = 1;
    const std::uint32_t device = file_device_name_00568e90(path);
    const std::int32_t result = resource_leaf_atomic_dispatch_00568d50(
        resource_open_callback_00561ce0, device, group, &context);
    std::uint32_t word;
    std::memcpy(&word, &result, sizeof(word));
    return reinterpret_cast<void*>(static_cast<std::uintptr_t>(word));
}

std::int32_t __cdecl resource_open_callback_00561ce0(
    std::uint32_t group, void* opaque_context) {
    const auto* context = static_cast<const ResourceAtomicContext*>(opaque_context);
    const char* const saved_path = context->path;
    // The original reuses its incoming group argument slot as the handle output.
    void* handle = reinterpret_cast<void*>(static_cast<std::uintptr_t>(group));
    if (!file_open_00533b90(saved_path, 1, group, &handle)) {
        if (context->callback_diagnostic_flag != 0) {
            diagnostic(0xda, "FILE_load - unable to open file %s\n", saved_path);
        }
        return 0;
    }

    const std::uint32_t nested_group = group - 1u;
    const std::int32_t size = size_00533de0(handle, nested_group);
    const std::uint32_t flags = context->opaque_08;
    void* const buffer = allocate_00531ca0(saved_path, size, flags);
    if (buffer == nullptr) {
        if (context->callback_diagnostic_flag != 0) {
            diagnostic(0xd2, "FILE_load - unable to reserve memory for file %s\n", saved_path);
        }
        close_00533da0(handle, nested_group);
        return 0;
    }

    (void)read_00533bf0(handle, 0, buffer, static_cast<std::uint32_t>(size), nested_group);
    (void)close_00533da0(handle, nested_group);
    const ResourceOpenTransform transform = resource_open_transform_006ad750;
    if (transform == nullptr) {
        return pointer_bits(buffer);
    }
    void* const result = transform(buffer, saved_path, flags);
    if (result == nullptr) {
        (void)free_00531f90(buffer);
    }
    return pointer_bits(result);
}

} // namespace porsche
