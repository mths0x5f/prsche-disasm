#include "porsche/formatter_bootstrap.hpp"
#include "porsche/exit_shutdown.hpp"
#if defined(PORSCHE_FORMATTER_CONNECTED_STRINGS)
#include "porsche/formatter_strings.hpp"
#endif
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

namespace {
std::vector<std::string> events;
unsigned module_length;
bool module_fail;
int hook_mode;
struct Terminal {};
std::string hex(const char* s) {
    std::string out;
    const char* digits = "0123456789abcdef";
    for (; *s; ++s) {
        unsigned c = static_cast<unsigned char>(*s);
        out += digits[c >> 4]; out += digits[c & 15];
    }
    return out;
}
void __cdecl header_hook() {
    events.push_back("hook:" + std::to_string(hook_mode));
    if (hook_mode >= 0) porsche::formatter_error_mode_006afcf4 = hook_mode;
}
void __cdecl terminal(std::uint32_t code) {
    events.push_back("exit:" + std::to_string(code)); throw Terminal{};
}
}
namespace porsche {
void __cdecl formatter_float_convert_005a41e3(const void*, char*, int, int, int) { std::abort(); }
void __cdecl formatter_float_trim_005a3e8d(char*) { std::abort(); }
void __cdecl formatter_float_decimal_005a3e33(char*) { std::abort(); }
void __cdecl formatter_float_assign_body_005a3ef3(int, void*, const void*) { std::abort(); }
int __cdecl formatter_float_sign_body_005a3edb(const double*) { std::abort(); }
#if !defined(PORSCHE_FORMATTER_CONNECTED_STRINGS)
char* __cdecl formatter_error_copy_005aa4e0(char* d, const char* s) {
    events.push_back("copy:" + hex(s)); return std::strcpy(d, s);
}
char* __cdecl formatter_error_concat_005aa4f0(char* d, const char* s) {
    events.push_back("concat:" + hex(s)); return std::strcat(d, s);
}
char* __cdecl formatter_error_copy_n_005a28a0(char* d, const char* s, std::uint32_t n) {
    events.push_back("copy_n:" + std::to_string(n) + ":" + hex(s));
    return std::strncpy(d, s, n);
}
int __cdecl formatter_error_dialog_005acfb9(const char* t, const char* caption, std::uint32_t flags) {
    events.push_back("dialog:" + std::to_string(flags) + ":" + hex(caption) + ":" + hex(t)); return 17;
}
#else
int __stdcall connected_message(void* owner,const char* t,const char* caption,std::uint32_t flags) {
    if(owner)std::abort();
    events.push_back("dialog:"+std::to_string(flags)+":"+hex(caption)+":"+hex(t));return 17;
}
void* __stdcall formatter_dialog_load_library(const char*) {std::abort();}
void* __stdcall formatter_dialog_get_proc_address(void*,const char*) {std::abort();}
#endif
std::uint32_t __stdcall formatter_error_module_name(void* module, char* out, std::uint32_t size) {
    events.push_back("module:" + std::to_string(module == nullptr) + ":" + std::to_string(size));
    if (module_fail) return 0;
    for (unsigned i = 0; i < module_length; ++i) out[i] = static_cast<char>('A' + i % 26);
    out[module_length] = 0; return module_length;
}
void* __stdcall formatter_error_std_handle(std::int32_t id) {
    events.push_back("handle:" + std::to_string(id)); return reinterpret_cast<void*>(0x1234);
}
int __stdcall formatter_error_write_file(void* handle, const void* data, std::uint32_t n,
                                        std::uint32_t* written, void* overlap) {
    events.push_back("write:" + std::to_string(reinterpret_cast<std::uintptr_t>(handle)) + ":" +
        std::to_string(n) + ":" + std::to_string(*written) + ":" +
        std::to_string(overlap == nullptr) + ":" + hex(static_cast<const char*>(data)));
    *written = n; return 1;
}
void __cdecl exit_shutdown_execute_005a2490(std::uint32_t code, std::int32_t skip, std::uint32_t after) {
    events.push_back("shutdown:" + std::to_string(code) + ":" + std::to_string(skip) + ":" + std::to_string(after));
}
}
int main(int argc, char** argv) {
    using namespace porsche;
    if (argc == 2 && std::strcmp(argv[1], "--initial") == 0) {
        const bool ok = formatter_error_mode_006afcf4 == 0 &&
            formatter_app_type_005e52cc == 2 && formatter_error_header_hook_006afec0 == nullptr &&
            formatter_error_exit_005e52c8 == &formatter_quick_exit_005a247f &&
            formatter_float_boundary_005e5788 == &formatter_default_float_failure_005abee8 &&
            formatter_float_post_005e578c == &formatter_default_text_failure_005abee8 &&
            formatter_float_post_005e5794 == &formatter_default_text_failure_005abee8 &&
            formatter_float_alternate_005e579c == &formatter_default_float_failure_005abee8 &&
            formatter_float_assign_005e5790 != nullptr && formatter_float_sign_005e5798 != nullptr;
        std::printf("{\"initial_native_identities\":%s}\n", ok ? "true" : "false");
        return ok ? 0 : 4;
    }
    if (argc != 9) return 2;
    const int kind = std::atoi(argv[1]);
    formatter_error_mode_006afcf4 = std::atoi(argv[2]);
    formatter_app_type_005e52cc = std::atoi(argv[3]);
    const int message = std::atoi(argv[4]);
    hook_mode = std::atoi(argv[5]);
    formatter_error_header_hook_006afec0 = hook_mode == -2 ? nullptr : &header_hook;
    module_length = static_cast<unsigned>(std::atoi(argv[6]));
    module_fail = std::atoi(argv[7]) != 0;
    formatter_error_exit_005e52c8 = &terminal;
#if defined(PORSCHE_FORMATTER_CONNECTED_STRINGS)
    formatter_dialog_message_006b001c=&connected_message;
    formatter_dialog_active_006b0020=nullptr;
    formatter_dialog_popup_006b0024=nullptr;
#endif
    bool terminated = false;
    bool writer = false;
    try {
        switch (kind) {
        case 0: formatter_default_float_failure_005abee8(nullptr, nullptr, 0, 0, 0); break;
        case 1: formatter_default_text_failure_005abee8(nullptr); break;
        case 2: formatter_fatal_005a2e22(message); break;
        case 3: formatter_error_header_005a9736(); break;
        case 4: formatter_error_message_005a976f(message); break;
        case 5: writer = formatter_bootstrap_005a0f5d() == &formatter_float_convert_005a41e3 &&
            formatter_float_boundary_005e5788 == &formatter_float_convert_005a41e3 &&
            formatter_float_post_005e578c == &formatter_float_trim_005a3e8d &&
            formatter_float_assign_005e5790 == &formatter_float_assign_body_005a3ef3 &&
            formatter_float_post_005e5794 == &formatter_float_decimal_005a3e33 &&
            formatter_float_sign_005e5798 == &formatter_float_sign_body_005a3edb &&
            formatter_float_alternate_005e579c == &formatter_float_convert_005a41e3; break;
        case 6: formatter_quick_exit_005a247f(static_cast<std::uint32_t>(message)); break;
        case 7: formatter_float_assign_005e5790(0, nullptr, nullptr); break;
        case 8: formatter_float_sign_005e5798(nullptr); break;
        default: return 3;
        }
    } catch (const Terminal&) { terminated = true; }
    std::printf("{\"name\":\"%s\",\"terminated\":%s,\"mode\":%d,\"app\":%d,\"writer\":%s,\"events\":[",
        argv[8], terminated ? "true" : "false", formatter_error_mode_006afcf4,
        formatter_app_type_005e52cc, writer ? "true" : "false");
    for (std::size_t i = 0; i < events.size(); ++i)
        std::printf("%s\"%s\"", i ? "," : "", events[i].c_str());
    std::puts("]}");
}
