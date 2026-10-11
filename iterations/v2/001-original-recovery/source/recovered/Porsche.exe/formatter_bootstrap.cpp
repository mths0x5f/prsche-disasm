#include "porsche/formatter_bootstrap.hpp"
#include "porsche/formatter_runtime.hpp"
#include "porsche/exit_shutdown.hpp"

namespace porsche {
namespace {
// All default callback adapters represent the same original nine-byte entry.
// Native C++ requires distinct symbols for incompatible types. Native pointer
// equality is therefore not original-address equality (005abee8).
[[noreturn]] void __cdecl default_assign(int, void*, const void*) {
    formatter_fatal_005a2e22(2);
}
[[noreturn]] int __cdecl default_sign(const double*) {
    formatter_fatal_005a2e22(2);
}
struct Message { int code; const char* text; };
const Message messages[] = {
    {2, "R6002\r\n- floating point not loaded\r\n"},
    {8, "R6008\r\n- not enough space for arguments\r\n"},
    {9, "R6009\r\n- not enough space for environment\r\n"},
    {10, "\r\nabnormal program termination\r\n"},
    {16, "R6016\r\n- not enough space for thread data\r\n"},
    {17, "R6017\r\n- unexpected multithread lock error\r\n"},
    {18, "R6018\r\n- unexpected heap error\r\n"},
    {19, "R6019\r\n- unable to open console device\r\n"},
    {24, "R6024\r\n- not enough space for _onexit/atexit table\r\n"},
    {25, "R6025\r\n- pure virtual function call\r\n"},
    {26, "R6026\r\n- not enough space for stdio initialization\r\n"},
    {27, "R6027\r\n- not enough space for lowio initialization\r\n"},
    {28, "R6028\r\n- unable to initialize heap\r\n"},
    {120, "DOMAIN error\r\n"}, {121, "SING error\r\n"},
    {122, "TLOSS error\r\n"}, {252, "\r\n"}, {255, "runtime error "},
    // Original scan stops at005e6008 and compares this readable zero DWORD.
    // Code0 consequently reaches a null text; it is not silently filtered.
    {0, nullptr}
};
}
FormatterAssignBoundary formatter_float_assign_005e5790 = &default_assign;
FormatterSignBoundary formatter_float_sign_005e5798 = &default_sign;
FormatterFloatBoundary formatter_float_alternate_005e579c =
    &formatter_default_float_failure_005abee8;
std::int32_t formatter_error_mode_006afcf4 = 0;
std::int32_t formatter_app_type_005e52cc = 2;
void (__cdecl *formatter_error_header_hook_006afec0)() = nullptr;
FormatterExitBoundary formatter_error_exit_005e52c8 = &formatter_quick_exit_005a247f;

void __cdecl formatter_default_float_failure_005abee8(const void*, char*, int, int, int) {
    formatter_fatal_005a2e22(2);
}
void __cdecl formatter_default_text_failure_005abee8(char*) {
    formatter_fatal_005a2e22(2);
}
FormatterFloatBoundary __cdecl formatter_bootstrap_005a0f5d() {
    formatter_float_post_005e578c = &formatter_float_trim_005a3e8d;
    formatter_float_boundary_005e5788 = &formatter_float_convert_005a41e3;
    formatter_float_assign_005e5790 = &formatter_float_assign_body_005a3ef3;
    formatter_float_post_005e5794 = &formatter_float_decimal_005a3e33;
    formatter_float_sign_005e5798 = &formatter_float_sign_body_005a3edb;
    formatter_float_alternate_005e579c = &formatter_float_convert_005a41e3;
    return &formatter_float_convert_005a41e3;
}
void __cdecl formatter_quick_exit_005a247f(std::uint32_t code) {
    exit_shutdown_execute_005a2490(code, 1, 0);
}
[[noreturn]] void __cdecl formatter_fatal_005a2e22(int message) {
    if (formatter_error_mode_006afcf4 == 1) formatter_error_header_005a9736();
    formatter_error_message_005a976f(message);
    formatter_error_exit_005e52c8(255);
    // Original has no RET or epilogue after the indirect terminal CALL.
    __assume(0);
}
void __cdecl formatter_error_header_005a9736() {
    if (formatter_error_mode_006afcf4 == 1 ||
        (formatter_error_mode_006afcf4 == 0 && formatter_app_type_005e52cc == 1)) {
        formatter_error_message_005a976f(252);
        // Read the hook after the first message, as in the original.
        if (auto hook = formatter_error_header_hook_006afec0) hook();
        formatter_error_message_005a976f(255);
    }
}
void __cdecl formatter_error_message_005a976f(int message) {
    unsigned index = 0;
    while (index < 18 && messages[index].code != message) ++index;
    if (messages[index].code != message) return;
    const char* text = messages[index].text;
    if (formatter_error_mode_006afcf4 == 1 ||
        (formatter_error_mode_006afcf4 == 0 && formatter_app_type_005e52cc == 1)) {
        std::uint32_t written = static_cast<std::uint32_t>(message);
        const auto length = formatter_strlen_005a6730(text);
        void* handle = formatter_error_std_handle(-12);
        formatter_error_write_file(handle, text, length, &written, nullptr);
        return;
    }
    if (message == 252) return;
    char name[260];
    if (!formatter_error_module_name(nullptr, name, 260))
        formatter_error_copy_005aa4e0(name, "<program name unknown>");
    char* display_name = name;
    if (formatter_strlen_005a6730(name) + 1 > 60) {
        display_name = name + formatter_strlen_005a6730(name) - 59;
        formatter_error_copy_n_005a28a0(display_name, "...", 3);
    }
    char display[160];
    formatter_error_copy_005aa4e0(display, "Runtime Error!\n\nProgram: ");
    formatter_error_concat_005aa4f0(display, display_name);
    formatter_error_concat_005aa4f0(display, "\n\n");
    formatter_error_concat_005aa4f0(display, text);
    formatter_error_dialog_005acfb9(display, "Microsoft Visual C++ Runtime Library", 0x12010);
}
} // namespace porsche
