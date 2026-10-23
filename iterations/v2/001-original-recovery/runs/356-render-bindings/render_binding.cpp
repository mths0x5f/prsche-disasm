#include "porsche/game_setup.hpp"
#include "porsche/splash_progress.hpp"
#include "porsche/render_loader.hpp"
#include <cstdint>

namespace porsche {
namespace {
using Proc0=void (__stdcall*)();
using Proc1=void (__stdcall*)(std::uint32_t);
Proc0 proc0(std::uint32_t slot){return reinterpret_cast<Proc0>(
    static_cast<std::uintptr_t>(render_thrash_exports_006bd910[slot]));}
Proc1 proc1(std::uint32_t slot){return reinterpret_cast<Proc1>(
    static_cast<std::uintptr_t>(render_thrash_exports_006bd910[slot]));}
}
void __stdcall game_setup_render_begin_006bd9b0(std::uint32_t mode){proc1(40)(mode);}
void __stdcall game_setup_render_reset_006bd91c(){proc0(3)();}
void __stdcall game_setup_render_prepare_006bd970(){proc0(24)();}
void __stdcall game_setup_render_update_006bd948(){proc0(14)();}
void __stdcall game_setup_render_finish_006bd978(std::uint32_t zero){proc1(26)(zero);}
void __stdcall splash_progress_thrash_window_006bd9b0(std::uint32_t mode){proc1(40)(mode);}
void __stdcall splash_progress_thrash_clear_window_006bd91c(){proc0(3)();}
void __stdcall splash_progress_thrash_pageflip_006bd948(){proc0(14)();}
void __stdcall splash_progress_thrash_sync_006bd978(std::uint32_t zero){proc1(26)(zero);}
}
