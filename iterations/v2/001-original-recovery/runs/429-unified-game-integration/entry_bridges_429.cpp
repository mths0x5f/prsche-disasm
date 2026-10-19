// Original Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39
//
// Run 429 bridges. Two C++ names for the SAME original function or cell are tied
// together only when the original call site matches the owner's ABI (argument
// count pushed, cdecl cleanup, return use). /alternatename keeps them one symbol,
// so no extra call frame exists. Nothing here provides data or stands in for an
// unrecovered body. Evidence (original call sites):
//
//   00471b70  004b6838 call, no arguments            -> frame_root_init_00471b70()
//   00565030  004a543f push 80h; call; add esp in 1c -> timer_setup_00565030(uint)
//   005a2c24  004a5c82 push esi; call; add esp,4; eax used
//                                                    -> formatter_text_alpha_005a2c24(int)
//   004237d0  004dd6ed push edi/eax/ecx; call; add esp,0ch
//                                                    -> application_context_clear_004237d0(void*,uint,uint)
//   005a177b  004a69e9 push value; push 005d1400; call; add esp,0ch
//                                                    -> formatter_stdio_printf_005a177b(const char*, ...)
//             (both 2-argument views below; the int result is discarded)
//   005e8e50  0048bea1 push 005e8e50 (address of the string)
//                                                    -> application_object_heap_name_005e8e50[32]
//   005debec  0057297a mov eax,[005debec]; test; je; push ebp; call eax; add esp,4
//                                                    -> adapter below (indirect call)
//
// Not bridged: 004dc850 and 0059d650 (the missing view and the defined owner
// differ in argument count), and 00532e10's negative/unmapped-index views, which
// are deliberate boundaries for unrecovered paths.
#include <cstdint>

#pragma comment(linker, "/alternatename:?startup_sequence_call_00471b70@porsche@@YAXXZ=?frame_root_init_00471b70@porsche@@YAXXZ")
#pragma comment(linker, "/alternatename:?startup_capacity_00565030@porsche@@YAXI@Z=?timer_setup_00565030@porsche@@YAXI@Z")
#pragma comment(linker, "/alternatename:?startup_drive_character_005a2c24@porsche@@YAHH@Z=?formatter_text_alpha_005a2c24@porsche@@YAHH@Z")
#pragma comment(linker, "/alternatename:?game_setup_movie_delta_004237d0@porsche@@YAXPAXII@Z=?application_context_clear_004237d0@porsche@@YAXPAXII@Z")
#pragma comment(linker, "/alternatename:?render_display_texture_report_005a177b@porsche@@YAXPBDI@Z=?formatter_stdio_printf_005a177b@porsche@@YAHPBDZZ")
#pragma comment(linker, "/alternatename:?startup_sequence_report_005a177b@porsche@@YAXII@Z=?formatter_stdio_printf_005a177b@porsche@@YAHPBDZZ")
#pragma comment(linker, "/alternatename:?network_group_text_005e8e50@porsche@@3PADA=?application_object_heap_name_005e8e50@porsche@@3PADA")

namespace porsche {

// 00572983..00572986: the caller already loaded and null-checked the pointer at
// 005debec; the original pushes one argument, calls it, and cleans 4 bytes.
void __cdecl render_event_invoke_callback_005debec(std::uint32_t callback, std::uint32_t argument) {
    reinterpret_cast<void(__cdecl*)(std::uint32_t)>(callback)(argument);
}

} // namespace porsche
