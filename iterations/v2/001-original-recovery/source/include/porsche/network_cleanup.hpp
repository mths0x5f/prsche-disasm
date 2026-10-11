#pragma once
#include "porsche/network_services.hpp"
#include "porsche/network_lifecycle.hpp"

namespace porsche {

// Original BSS pointer cells; 0048c4d0 constructs them and 0048c580 clears
// them. They do not overlap the existing network/session/member owners.
extern void* network_cleanup_list_00628c60;
extern void* network_cleanup_lock_cell_00628c64;

// Original worker effects remain explicitly unresolved with their actual
// cdecl argument ABI. No production worker substitutes are supplied here.
void __cdecl network_cleanup_stop_worker_0055d9b0();
void __cdecl network_cleanup_destroy_worker_0055d1b0(void* worker);

} // namespace porsche
