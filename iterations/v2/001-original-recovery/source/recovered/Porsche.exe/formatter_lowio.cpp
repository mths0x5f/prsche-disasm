#include "porsche/formatter_lowio.hpp"
#include <cstring>

namespace porsche {
namespace {
std::uint32_t read32(const void* pointer) {
    std::uint32_t value; std::memcpy(&value, pointer, 4); return value;
}
void write32(void* pointer, std::uint32_t value) { std::memcpy(pointer, &value, 4); }
std::int32_t signed32(std::uint32_t value) {
    std::int32_t result; std::memcpy(&result, &value, 4); return result;
}
std::uint8_t* bank(unsigned index) {
    return const_cast<std::uint8_t*>(formatter_cleanup_handle_table_006c01e0[index]);
}
std::uint8_t* record(std::uint32_t id) { return bank(id >> 5) + (id & 31u) * 36; }
void initialize_bank(unsigned index) {
    auto* cursor = bank(index);
    // The original rereads the cell to form each loop's end pointer.
    while (cursor < bank(index) + 0x480) {
        cursor[4] = 0;
        write32(cursor, 0xffffffffu);
        write32(cursor + 8, 0);
        cursor[5] = 10;
        cursor += 36;
    }
}
void prepare_lock(std::uint8_t* entry) {
    if (read32(entry + 8) == 0) {
        exit_registry_lock_api_005a4ba4(17);
        if (read32(entry + 8) == 0) {
            formatter_lowio_critical_initialize(entry + 12);
            write32(entry + 8, read32(entry + 8) + 1);
        }
        exit_registry_unlock_api_005a4c05(17);
    }
}
std::int32_t invalid_handle() {
    *formatter_lowio_errno_005a669e() = 9;
    *formatter_lowio_doserrno_005a66a7() = 0;
    return -1;
}
std::int32_t standard_id(std::uint32_t id) {
    return id == 0 ? -10 : id == 1 ? -11 : -12;
}
}

std::uint32_t __cdecl formatter_lowio_initialize_005a953e() {
    auto* first = static_cast<std::uint8_t*>(exit_registry_malloc_005a3be5(0x480));
    if (!first) formatter_fatal_005a2e22(27);
    formatter_cleanup_handle_table_006c01e0[0] = first;
    formatter_cleanup_handle_limit_006c02e0 = 32;
    initialize_bank(0);
    FormatterLowioStartupInfo32 startup;
    formatter_lowio_startup_info(&startup);
    if (startup.reserved_bytes && startup.reserved) {
        const std::int32_t declared_count = signed32(read32(startup.reserved));
        const auto* flags = startup.reserved + 4;
        // Original handle-array address uses the UNCLAMPED signed count.
        const auto address = reinterpret_cast<std::uintptr_t>(flags) +
                             static_cast<std::uint32_t>(declared_count);
        const auto* handles = reinterpret_cast<const std::uint8_t*>(address);
        std::int32_t count = declared_count < 2048 ? declared_count : 2048;
        if (signed32(formatter_cleanup_handle_limit_006c02e0) < count) {
            unsigned index = 1;
            do {
                auto* allocation = static_cast<std::uint8_t*>(exit_registry_malloc_005a3be5(0x480));
                if (!allocation) { count = signed32(formatter_cleanup_handle_limit_006c02e0); break; }
                formatter_cleanup_handle_limit_006c02e0 += 32;
                formatter_cleanup_handle_table_006c01e0[index] = allocation;
                initialize_bank(index++);
            } while (signed32(formatter_cleanup_handle_limit_006c02e0) < count);
        }
        for (std::int32_t id = 0; id < count; ++id, ++flags, handles += 4) {
            const auto handle = read32(handles);
            if (handle == 0xffffffffu || !(*flags & 1u)) continue;
            if (!(*flags & 8u) && !formatter_lowio_file_type(handle)) continue;
            auto* entry = record(static_cast<std::uint32_t>(id));
            // A file-type boundary may mutate the inherited payload.
            write32(entry, read32(handles));
            entry[4] = *flags;
        }
    }
    for (std::uint32_t id = 0; id < 3; ++id) {
        auto* entry = record(id);
        if (read32(entry) != 0xffffffffu) { entry[4] |= 0x80; continue; }
        entry[4] = 0x81;
        const auto handle = formatter_lowio_get_standard(standard_id(id));
        std::uint32_t type;
        if (handle == 0xffffffffu || !(type = formatter_lowio_file_type(handle))) {
            entry[4] |= 0x40;
            continue;
        }
        type &= 0xffu;
        write32(entry, handle);
        if (type == 2) entry[4] |= 0x40;
        else if (type == 3) entry[4] |= 8;
    }
    return formatter_lowio_set_count(formatter_cleanup_handle_limit_006c02e0);
}
std::int32_t __cdecl formatter_lowio_allocate_005ab4c6() {
    exit_registry_lock_api_005a4ba4(18);
    std::int32_t result = -1;
    for (unsigned index = 0; index < 64; ++index) {
        if (bank(index)) {
            auto* cursor = bank(index);
            while (cursor < bank(index) + 0x480) {
                if (!(cursor[4] & 1u)) {
                    prepare_lock(cursor);
                    formatter_lowio_critical_enter(cursor + 12);
                    if (!(cursor[4] & 1u)) {
                        write32(cursor, 0xffffffffu);
                        const auto difference = static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(cursor) -
                                                                          reinterpret_cast<std::uintptr_t>(bank(index)));
                        result = signed32(difference) / 36 + static_cast<std::int32_t>(index * 32);
                        if (result != -1) goto done;
                        break; // Original -1 result advances directly to the next bank.
                    } else formatter_lowio_critical_leave(cursor + 12);
                }
                cursor += 36;
            }
        } else {
            auto* allocation = static_cast<std::uint8_t*>(exit_registry_malloc_005a3be5(0x480));
            if (!allocation) goto done;
            formatter_cleanup_handle_limit_006c02e0 += 32;
            formatter_cleanup_handle_table_006c01e0[index] = allocation;
            initialize_bank(index);
            result = static_cast<std::int32_t>(index * 32);
            formatter_lowio_lock_005ab726(static_cast<std::uint32_t>(result));
            goto done;
        }
    }
done:
    exit_registry_unlock_api_005a4c05(18);
    return result;
}
std::int32_t __cdecl formatter_lowio_attach_005ab5e9(std::uint32_t id, std::uint32_t handle) {
    if (id >= formatter_cleanup_handle_limit_006c02e0 || read32(record(id)) != 0xffffffffu)
        return invalid_handle();
    if (formatter_app_type_005e52cc == 1 && id < 3)
        formatter_lowio_set_standard(standard_id(id), handle);
    // The original reloads the bank cell after SetStdHandle.
    write32(record(id), handle);
    return 0;
}
std::int32_t __cdecl formatter_lowio_detach_005ab665(std::uint32_t id) {
    if (id >= formatter_cleanup_handle_limit_006c02e0 || !(record(id)[4] & 1u) ||
        read32(record(id)) == 0xffffffffu) return invalid_handle();
    if (formatter_app_type_005e52cc == 1 && id < 3)
        formatter_lowio_set_standard(standard_id(id), 0);
    write32(record(id), 0xffffffffu);
    return 0;
}
std::uint32_t __cdecl formatter_lowio_handle_005ab6e4(std::uint32_t id) {
    if (id >= formatter_cleanup_handle_limit_006c02e0 || !(record(id)[4] & 1u))
        return static_cast<std::uint32_t>(invalid_handle());
    return read32(record(id));
}
void __cdecl formatter_lowio_lock_005ab726(std::uint32_t id) {
    auto* entry = record(id);
    prepare_lock(entry);
    // Reloads the bank cell after lazy initialization/lock callbacks.
    formatter_lowio_critical_enter(record(id) + 12);
}
void __cdecl formatter_lowio_unlock_005ab785(std::uint32_t id) {
    formatter_lowio_critical_leave(record(id) + 12);
}
} // namespace porsche
