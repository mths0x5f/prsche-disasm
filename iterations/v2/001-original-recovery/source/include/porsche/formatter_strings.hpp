#pragma once
#include "porsche/formatter_bootstrap.hpp"

namespace porsche {
using FormatterDialogBoundary = int (__stdcall *)(void*, const char*, const char*, std::uint32_t);
using FormatterActiveWindowBoundary = void* (__stdcall *)();
using FormatterLastPopupBoundary = void* (__stdcall *)(void*);
extern FormatterDialogBoundary formatter_dialog_message_006b001c;
extern FormatterActiveWindowBoundary formatter_dialog_active_006b0020;
extern FormatterLastPopupBoundary formatter_dialog_popup_006b0024;

// OS imports remain typed boundaries; the original lazily resolves user32.
void* __stdcall formatter_dialog_load_library(const char*);
void* __stdcall formatter_dialog_get_proc_address(void*, const char*);
} // namespace porsche
