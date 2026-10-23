#pragma once
#include <cstdint>
namespace porsche {
// Only previously unowned bytes of original 005de650..005de67f.
// These arrays do not imply physical adjacency to the canonical shutdown fields.
extern std::uint8_t cursor_snapshot_prefix_005de650[12];
extern std::uint8_t cursor_snapshot_suffix_005de65e[30];
void __cdecl startup_cursor_state_save_00570ed0(void* snapshot);
void __cdecl startup_cursor_state_restore_00570f00(const void* snapshot);
}
