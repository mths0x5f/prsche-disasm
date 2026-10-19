# Run 417 - Integration of Recovered Frame/Loop/AppMain Functions into Game Target

All 185 C++ translation units in the actual Win32 game graph compiled cleanly under MSVC Win32 (`Hostx64/x86`). This integrates 29 additional reviewed translation units from Runs 400..411 into `porsche_game_entry_bridges`, alongside the forwarding bridge `entry_bridges_417.cpp`.

## Key Achievements

1. **Closed Linker Contracts (21 symbols)**:
   - **Main Loop Frame Control & Timers**:
     - `?application_main_function_00412030@porsche@@YAXXZ` (Run 400)
     - `?application_main_function_00413ea0@porsche@@YAXXZ` (Run 401)
     - `?application_main_function_00414eb0@porsche@@YAXXZ` (Run 400)
     - `?application_main_function_00425780@porsche@@YAXXZ` (Run 400)
     - `?application_main_function_00467740@porsche@@YAXXZ` (Run 400)
     - `?application_main_function_004acb80@porsche@@YAXXZ` (Run 400)
     - `?application_main_function_00563d30@porsche@@YAXXZ` (Run 400)
   - **Subsystem & Window Lifecycle Forwarders**:
     - `?application_main_function_004640b0@porsche@@YAXXZ` (Run 409 - audio listener update)
     - `?application_main_function_0048cdf0@porsche@@YAXXZ` (Run 411 - UI screen tree draw)
     - `?startup_sequence_call_0048cdf0@porsche@@YAXXZ` (Run 411 - UI startup tree)
     - `?application_network_change_0048e1a0@porsche@@YIXPAX0III@Z` (Run 411 - UI screen present)
     - `?application_main_function_004a54b0@porsche@@YAXXZ` (Run 402 - heap release anchor)
     - `?application_main_function_004a54e0@porsche@@YAXXZ` (Run 402 - heap release entry)
     - `?application_main_function_004a88a0@porsche@@YAXXZ` (Run 409 - display mode probe sync)
     - `?application_main_function_004b68f0@porsche@@YAXXZ` (Run 408 - app loop post-tick pipeline)
     - `?heap_fill_0053c290@porsche@@YAXPAXII@Z` (Run 405 - heap fill)
     - `?resource_invalid_module_path_0059d650@porsche@@YAXPBD@Z` (Run 409 - CD-ROM path resolve)
     - `?game_setup_resource_file_open_0059d8e0@porsche@@YAPAXPBDI@Z` (Run 407 - asset path locate/open)
     - `?splash_progress_load_resource_0059d8e0@porsche@@YAPAXPBDI@Z` (Run 407 - splash progress resource load)
     - `?render_display_texture_report_005a177b@porsche@@YAXPBDI@Z` (Run 404 - texture report)
     - `?startup_sequence_report_005a177b@porsche@@YAXII@Z` (Run 404 - startup sequence report)

2. **Zero Duplicate Collisions**:
   - `00471b60` was already defined in Run 290. The forwarding bridge `entry_bridges_417.cpp` isolates `004a54b0` and `004a54e0` from Run 402 without re-exporting `00471b60`, preventing LNK2005.

3. **Compiler and Linker Health**:
   - Compiler errors: **0**
   - Other linker errors: **0**
   - Source pins: **427** verified via `v2_shared_manifests.py`.
   - The updated linker frontier reports **348 unresolved names / 381 references**, accurately tracking the child dependencies and unrecovered data cells of the newly introduced subsystems.

## Independent Verification

```powershell
py -3 scripts/research/audit-v2-game-entry-417.py
```

## Next Connected Work

- Original heap-shutdown binding `004a54e0 -> 0059eb20`
- Shared frame-root data storage and initialization layout (`00628960` and associated globals).
