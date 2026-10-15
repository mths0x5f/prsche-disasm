#pragma once
#include "porsche/formatter_runtime_storage.hpp"
#include "porsche/formatter_output.hpp"
#include "porsche/exit_registry.hpp"

namespace porsche {
extern void* formatter_stdio_buffers_006afd60[2];
void __cdecl formatter_stdio_lock_pointer_005a36ea(FormatterOriginalDescriptor32*);
void __cdecl formatter_stdio_lock_index_005a3719(std::int32_t,FormatterOriginalDescriptor32*);
void __cdecl formatter_stdio_unlock_pointer_005a373c(FormatterOriginalDescriptor32*);
void __cdecl formatter_stdio_unlock_index_005a376b(std::int32_t,FormatterOriginalDescriptor32*);
int __cdecl formatter_stdio_temporary_buffer_005a533e(FormatterOriginalDescriptor32*);
void __cdecl formatter_stdio_finish_buffer_005a53cb(int,FormatterOriginalDescriptor32*);
int __cdecl formatter_stdio_flush_005a76a1(FormatterOriginalDescriptor32*);
int __cdecl formatter_stdio_printf_005a177b(const char*,...);
}
