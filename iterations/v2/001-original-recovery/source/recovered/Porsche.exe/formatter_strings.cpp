#include "porsche/formatter_strings.hpp"
#include <cstring>

#if defined(PORSCHE_FORMATTER_MEMORY_TRACE)
// Private differential build only. No observer or branch in production.
extern void formatter_strings_memory_trace(char, const void*, unsigned, std::uint32_t);
#endif

namespace porsche {
namespace {
void trace(char access, const void* pointer, unsigned size, std::uint32_t value) {
#if defined(PORSCHE_FORMATTER_MEMORY_TRACE)
    formatter_strings_memory_trace(access, pointer, size, value);
#else
    (void)access; (void)pointer; (void)size; (void)value;
#endif
}
std::uint8_t read8(const unsigned char* p) {
    const auto value = *p; trace('r', p, 1, value); return value;
}
std::uint32_t read32(const unsigned char* p) {
    std::uint32_t value;
    std::memcpy(&value, p, 4); trace('r', p, 4, value); return value;
}
void write8(unsigned char* p, std::uint8_t value) {
    *p = value; trace('w', p, 1, value);
}
void write16(unsigned char* p, std::uint16_t value) {
    std::memcpy(p, &value, 2); trace('w', p, 2, value);
}
void write32(unsigned char* p, std::uint32_t value) {
    std::memcpy(p, &value, 4); trace('w', p, 4, value);
}
bool aligned(const void* p) { return (reinterpret_cast<std::uintptr_t>(p) & 3u) == 0; }
bool probe_zero(std::uint32_t value) {
    return (((~value) ^ (value + 0x7efefeffu)) & 0x81010100u) != 0;
}

// 005aa551..005aa5cf is shared by both original entries. The two DWORD
// reads and terminator-specific byte/word/DWORD stores are intentional.
void copy_suffix(unsigned char* destination, const unsigned char* source) {
    while (!aligned(source)) {
        const auto value = read8(source++);
        if (!value) { write8(destination, 0); return; }
        write8(destination++, value);
    }
    for (;;) {
        const bool candidate = probe_zero(read32(source));
        const auto value = read32(source);
        source += 4;
        if (candidate) {
            if ((value & 0xffu) == 0) { write8(destination, 0); return; }
            if ((value & 0xff00u) == 0) {
                write16(destination, static_cast<std::uint16_t>(value)); return;
            }
            if ((value & 0xff0000u) == 0) {
                write16(destination, static_cast<std::uint16_t>(value));
                write8(destination + 2, 0); return;
            }
            if ((value & 0xff000000u) == 0) { write32(destination, value); return; }
        }
        write32(destination, value);
        destination += 4;
    }
}
void pad(unsigned char* destination, std::uint32_t count, bool align_first) {
    if (align_first) {
        while (count && !aligned(destination)) {
            write8(destination++, 0); --count;
        }
    }
    while (count >= 4) { write32(destination, 0); destination += 4; count -= 4; }
    while (count--) write8(destination++, 0);
}
}

char* __cdecl formatter_error_copy_005aa4e0(char* destination, const char* source) {
    copy_suffix(reinterpret_cast<unsigned char*>(destination),
                reinterpret_cast<const unsigned char*>(source));
    return destination;
}
char* __cdecl formatter_error_concat_005aa4f0(char* destination, const char* source) {
    auto* cursor = reinterpret_cast<unsigned char*>(destination);
    while (!aligned(cursor)) {
        if (!read8(cursor++)) { --cursor; goto found; }
    }
    for (;;) {
        const bool candidate = probe_zero(read32(cursor));
        cursor += 4;
        if (!candidate) continue;
        const auto value = read32(cursor - 4);
        if ((value & 0xffu) == 0) { cursor -= 4; break; }
        if ((value & 0xff00u) == 0) { cursor -= 3; break; }
        if ((value & 0xff0000u) == 0) { cursor -= 2; break; }
        if ((value & 0xff000000u) == 0) { --cursor; break; }
    }
found:
    copy_suffix(cursor, reinterpret_cast<const unsigned char*>(source));
    return destination;
}
char* __cdecl formatter_error_copy_n_005a28a0(char* destination, const char* source,
                                          std::uint32_t count) {
    if (!count) return destination;
    auto* out = reinterpret_cast<unsigned char*>(destination);
    auto* in = reinterpret_cast<const unsigned char*>(source);
    while (!aligned(in)) {
        const auto value = read8(in++);
        write8(out++, value);
        if (--count == 0) return destination;
        if (!value) { pad(out, count, true); return destination; }
    }
    std::uint32_t words = count >> 2;
    const auto tail = count & 3u;
    while (words) {
        const bool candidate = probe_zero(read32(in));
        auto value = read32(in);
        in += 4;
        if (candidate) {
            bool terminal = true;
            if ((value & 0xffu) == 0) value = 0;
            else if ((value & 0xff00u) == 0) value &= 0xffu;
            else if ((value & 0xff0000u) == 0) value &= 0xffffu;
            else if ((value & 0xff000000u) != 0) terminal = false;
            if (terminal) {
                write32(out, value); out += 4;
                pad(out, (--words) * 4 + tail, false);
                return destination;
            }
        }
        write32(out, value); out += 4; --words;
    }
    for (std::uint32_t remaining = tail; remaining;) {
        const auto value = read8(in++);
        write8(out++, value); --remaining;
        if (!value) { pad(out, remaining, false); return destination; }
    }
    return destination;
}

FormatterDialogBoundary formatter_dialog_message_006b001c = nullptr;
FormatterActiveWindowBoundary formatter_dialog_active_006b0020 = nullptr;
FormatterLastPopupBoundary formatter_dialog_popup_006b0024 = nullptr;

int __cdecl formatter_error_dialog_005acfb9(const char* text, const char* caption,
                                         std::uint32_t flags) {
    if (!formatter_dialog_message_006b001c) {
        void* module = formatter_dialog_load_library("user32.dll");
        if (!module) return 0;
        formatter_dialog_message_006b001c = reinterpret_cast<FormatterDialogBoundary>(
            formatter_dialog_get_proc_address(module, "MessageBoxA"));
        if (!formatter_dialog_message_006b001c) return 0;
        formatter_dialog_active_006b0020 = reinterpret_cast<FormatterActiveWindowBoundary>(
            formatter_dialog_get_proc_address(module, "GetActiveWindow"));
        formatter_dialog_popup_006b0024 = reinterpret_cast<FormatterLastPopupBoundary>(
            formatter_dialog_get_proc_address(module, "GetLastActivePopup"));
    }
    void* owner = nullptr;
    if (auto active = formatter_dialog_active_006b0020) {
        owner = active();
        if (owner) {
            if (auto popup = formatter_dialog_popup_006b0024) owner = popup(owner);
        }
    }
    // The original rereads the mutable message callback after owner callbacks.
    return formatter_dialog_message_006b001c(owner, text, caption, flags);
}
} // namespace porsche
