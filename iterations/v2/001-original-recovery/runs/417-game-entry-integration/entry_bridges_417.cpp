#include <cstdint>

namespace porsche {

// 402 forwarders (avoiding duplicate 00471b60 from run 290)
extern void __cdecl flush_subsystem_004b7070();
extern void __cdecl platform_flush_0059eb20();
struct SubsystemContext_00628c70 {
    void __thiscall release_0048ff30();
};
extern SubsystemContext_00628c70* global_subsystem_00628c70;
extern void* __cdecl memory_free_0059f050(void*);

void __cdecl application_main_function_004a54e0() {
    platform_flush_0059eb20();
}

void __cdecl application_main_function_004a54b0() {
    flush_subsystem_004b7070();
    SubsystemContext_00628c70* sub = global_subsystem_00628c70;
    if (sub != nullptr) {
        sub->release_0048ff30();
        memory_free_0059f050(sub);
        global_subsystem_00628c70 = nullptr;
    }
}

// 405 forwarders
void __cdecl application_main_function_0053c290(std::uint32_t va, std::uint32_t val, std::uint32_t bytes);
void __cdecl heap_fill_0053c290(void* p, std::uint32_t val, std::uint32_t bytes) {
    application_main_function_0053c290(reinterpret_cast<std::uint32_t>(p), val, bytes);
}

// 407 forwarders
void* __cdecl asset_path_locate_or_open_0059d8e0(const char* name, std::uint32_t flags);
void* __cdecl game_setup_resource_file_open_0059d8e0(const char* name, std::uint32_t flags) {
    return asset_path_locate_or_open_0059d8e0(name, flags);
}
void* __cdecl splash_progress_load_resource_0059d8e0(const char* name, std::uint32_t flags) {
    return asset_path_locate_or_open_0059d8e0(name, flags);
}

// 408 forwarders
void __cdecl app_loop_post_tick_pipeline_004b68f0();
void __cdecl application_main_function_004b68f0() {
    app_loop_post_tick_pipeline_004b68f0();
}

// 409 forwarders
void __cdecl cdrom_path_resolve_0059d650(const char* path);
void __cdecl resource_invalid_module_path_0059d650(const char* path) {
    cdrom_path_resolve_0059d650(path);
}
void __cdecl display_mode_probe_sync_004a88a0();
void __cdecl application_main_function_004a88a0() {
    display_mode_probe_sync_004a88a0();
}
void __cdecl audio_listener_update_004640b0();
void __cdecl application_main_function_004640b0() {
    audio_listener_update_004640b0();
}

// 404 forwarders
void __cdecl application_main_function_005a177b(const char* text, std::uint32_t code);
void __cdecl render_display_texture_report_005a177b(const char* text, std::uint32_t code) {
    application_main_function_005a177b(text, code);
}
void __cdecl startup_sequence_report_005a177b(std::uint32_t a, std::uint32_t b) {
    application_main_function_005a177b(reinterpret_cast<const char*>(a), b);
}

// 411 forwarders
void __cdecl ui_draw_screen_tree_0048cdf0();
void __cdecl application_main_function_0048cdf0() {
    ui_draw_screen_tree_0048cdf0();
}
void __cdecl startup_sequence_call_0048cdf0() {
    ui_draw_screen_tree_0048cdf0();
}


// 411 forwarder for 0048e1a0
struct UiScreenContext;
namespace {
struct UiScreenContextProxy {
    void __thiscall ui_screen_render_present_0048e1a0(std::uint32_t mode, std::uint32_t id, const char* title);
};
}
void __fastcall application_network_change_0048e1a0(void* ecx, void* /*edx*/, std::uint32_t mode, std::uint32_t id, std::uint32_t title) {
    reinterpret_cast<UiScreenContextProxy*>(ecx)->ui_screen_render_present_0048e1a0(mode, id, reinterpret_cast<const char*>(title));
}

} // namespace porsche
