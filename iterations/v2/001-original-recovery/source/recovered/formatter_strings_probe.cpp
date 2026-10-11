#include "porsche/formatter_strings.hpp"
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>

namespace {
alignas(4) unsigned char arena[1024];
bool memory_trace;
std::vector<std::string> events;
unsigned mask, active_value, popup_value;
int box_result, load_fail, mutation;
std::string hex_bytes(const unsigned char* bytes, std::size_t size) {
    const char* digits = "0123456789abcdef";
    std::string output;
    for (std::size_t i = 0; i < size; ++i) {
        output += digits[bytes[i] >> 4]; output += digits[bytes[i] & 15];
    }
    return output;
}
std::string hex_text(const char* text) {
    std::size_t n = 0;
    while (text[n]) ++n;
    return hex_bytes(reinterpret_cast<const unsigned char*>(text), n);
}
int __stdcall message_box_alternate(void* owner, const char* text, const char* caption, std::uint32_t flags) {
    events.push_back("alternate:" + std::to_string(reinterpret_cast<std::uintptr_t>(owner)) + ":" +
        hex_text(text) + ":" + hex_text(caption) + ":" + std::to_string(flags));
    return box_result + 1;
}
int __stdcall message_box(void* owner, const char* text, const char* caption, std::uint32_t flags) {
    events.push_back("message:" + std::to_string(reinterpret_cast<std::uintptr_t>(owner)) + ":" +
        hex_text(text) + ":" + hex_text(caption) + ":" + std::to_string(flags));
    return box_result;
}
void* __stdcall last_popup(void* owner) {
    events.push_back("popup:" + std::to_string(reinterpret_cast<std::uintptr_t>(owner)));
    if (mutation == 2) porsche::formatter_dialog_message_006b001c = &message_box_alternate;
    return reinterpret_cast<void*>(popup_value);
}
void* __stdcall active_window() {
    events.push_back("active");
    if (mutation == 1) porsche::formatter_dialog_popup_006b0024 = nullptr;
    if (mutation == 3) porsche::formatter_dialog_message_006b001c = &message_box_alternate;
    return reinterpret_cast<void*>(active_value);
}
void print_events() {
    std::printf("\"events\":[");
    for (std::size_t i = 0; i < events.size(); ++i)
        std::printf("%s\"%s\"", i ? "," : "", events[i].c_str());
    std::printf("]");
}
}

void formatter_strings_memory_trace(char access, const void* pointer, unsigned size, std::uint32_t value) {
    if (!memory_trace) return;
    const auto offset = reinterpret_cast<const unsigned char*>(pointer) - arena;
    if (offset < 0 || offset + size > sizeof(arena)) std::abort();
    events.push_back(std::string(1, access) + ":" + std::to_string(offset) + ":" +
                     std::to_string(size) + ":" + std::to_string(value));
}
namespace porsche {
void* __stdcall formatter_dialog_load_library(const char* name) {
    events.push_back("load:" + hex_text(name));
    return load_fail ? nullptr : reinterpret_cast<void*>(0x3000);
}
void* __stdcall formatter_dialog_get_proc_address(void* module, const char* name) {
    events.push_back("proc:" + std::to_string(reinterpret_cast<std::uintptr_t>(module)) + ":" + hex_text(name));
    const std::string symbol(name);
    if (symbol == "MessageBoxA") return mask & 1 ? reinterpret_cast<void*>(&message_box) : nullptr;
    if (symbol == "GetActiveWindow") return mask & 2 ? reinterpret_cast<void*>(&active_window) : nullptr;
    if (symbol == "GetLastActivePopup") return mask & 4 ? reinterpret_cast<void*>(&last_popup) : nullptr;
    std::abort();
}
}

int main() {
    using namespace porsche;
    char kind;
    while (std::cin >> kind) {
        events.clear();
        if (kind == 's') {
            unsigned operation, destination, source, count;
            std::string initial;
            std::cin >> operation >> destination >> source >> count >> initial;
            if (initial.size() != sizeof(arena) * 2) return 2;
            for (std::size_t i = 0; i < sizeof(arena); ++i)
                arena[i] = static_cast<unsigned char>(std::stoul(initial.substr(i * 2, 2), nullptr, 16));
            char* result;
            memory_trace = true;
            if (operation == 0) result = formatter_error_copy_005aa4e0(
                reinterpret_cast<char*>(arena + destination), reinterpret_cast<const char*>(arena + source));
            else if (operation == 1) result = formatter_error_concat_005aa4f0(
                reinterpret_cast<char*>(arena + destination), reinterpret_cast<const char*>(arena + source));
            else result = formatter_error_copy_n_005a28a0(
                reinterpret_cast<char*>(arena + destination), reinterpret_cast<const char*>(arena + source), count);
            memory_trace = false;
            std::printf("{\"kind\":\"string\",\"return_offset\":%u,\"arena\":\"%s\",",
                static_cast<unsigned>(reinterpret_cast<unsigned char*>(result) - arena), hex_bytes(arena, sizeof(arena)).c_str());
            print_events(); std::puts("}");
        } else if (kind == 'd') {
            unsigned seed, repeat;
            std::cin >> seed >> mask >> active_value >> popup_value >> box_result >> load_fail >> repeat >> mutation;
            formatter_dialog_message_006b001c = seed & 1 ? &message_box : nullptr;
            formatter_dialog_active_006b0020 = seed & 2 ? &active_window : nullptr;
            formatter_dialog_popup_006b0024 = seed & 4 ? &last_popup : nullptr;
            std::printf("{\"kind\":\"dialog\",\"returns\":[");
            for (unsigned i = 0; i < repeat; ++i) {
                int result = formatter_error_dialog_005acfb9("fatal text", "caption", 0x12010);
                std::printf("%s%d", i ? "," : "", result);
            }
            const int message_identity = formatter_dialog_message_006b001c == nullptr ? 0 :
                formatter_dialog_message_006b001c == &message_box ? 1 : 2;
            std::printf("],\"cells\":[%d,%d,%d],", message_identity,
                formatter_dialog_active_006b0020 != nullptr, formatter_dialog_popup_006b0024 != nullptr);
            print_events(); std::puts("}");
        } else return 3;
    }
}
