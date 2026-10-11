#pragma once
#include "porsche/formatter_runtime_storage.hpp"
#include <cstdint>

namespace porsche {
using FormatterAssignBoundary = void (__cdecl *)(int, void*, const void*);
using FormatterSignBoundary = int (__cdecl *)(const double*);
using FormatterExitBoundary = void (__cdecl *)(std::uint32_t);
extern FormatterAssignBoundary formatter_float_assign_005e5790;
extern FormatterSignBoundary formatter_float_sign_005e5798;
extern FormatterFloatBoundary formatter_float_alternate_005e579c;
extern std::int32_t formatter_error_mode_006afcf4;
extern std::int32_t formatter_app_type_005e52cc;
extern void (__cdecl *formatter_error_header_hook_006afec0)();
extern FormatterExitBoundary formatter_error_exit_005e52c8;

FormatterFloatBoundary __cdecl formatter_bootstrap_005a0f5d();
[[noreturn]] void __cdecl formatter_fatal_005a2e22(int message);
void __cdecl formatter_error_header_005a9736();
void __cdecl formatter_error_message_005a976f(int message);
void __cdecl formatter_quick_exit_005a247f(std::uint32_t code);

// Runtime float implementations are still unresolved. Types follow consumers;
// the two text functions are unpromoted code entries in the original listing.
void __cdecl formatter_float_convert_005a41e3(const void*, char*, int, int, int);
void __cdecl formatter_float_trim_005a3e8d(char*);
void __cdecl formatter_float_decimal_005a3e33(char*);
void __cdecl formatter_float_assign_body_005a3ef3(int, void*, const void*);
int __cdecl formatter_float_sign_body_005a3edb(const double*);

// Explicit unrecovered call boundaries, not host CRT substitutions.
char* __cdecl formatter_error_copy_005aa4e0(char*, const char*);
char* __cdecl formatter_error_concat_005aa4f0(char*, const char*);
char* __cdecl formatter_error_copy_n_005a28a0(char*, const char*, std::uint32_t);
int __cdecl formatter_error_dialog_005acfb9(const char*, const char*, std::uint32_t);
std::uint32_t __stdcall formatter_error_module_name(void*, char*, std::uint32_t);
void* __stdcall formatter_error_std_handle(std::int32_t);
int __stdcall formatter_error_write_file(void*, const void*, std::uint32_t,
                                        std::uint32_t*, void*);
} // namespace porsche
