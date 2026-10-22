#include "startup_device.hpp"
#include "porsche/render_display.hpp"
#include "porsche/startup_input.hpp"
#include "porsche/window_create.hpp"
#include "porsche/window_handlers.hpp"
#include "porsche/file_threads.hpp"

#include <cstdint>

namespace porsche {

// Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// 00536e50..00537017: DirectInput 5.0 mouse startup, not a display provider.
static_assert(sizeof(void*)==4,"original DirectInput state requires Win32");
std::uint32_t startup_mouse_mode_0069e078=0;
std::uint32_t startup_mouse_slot0_0069e07c=0;
std::uint32_t startup_mouse_slot1_0069e080=0;
std::uint32_t startup_mouse_slot2_0069e084=0;
std::uint8_t startup_mouse_flags_0069e088[4]={};
void* startup_directinput_0069e098=nullptr;
void* startup_mouse_device_0069e09c=nullptr;
std::uint32_t startup_mouse_initialized_0069e0a0=0;
std::uint32_t startup_mouse_exit_registered_0069e0a4=0;

namespace {
// Original operand 00536eb6 -> 005bf9a0; 00536ecd -> 005bf8c0.
constexpr StartupGuid create_device_guid_005bf9a0={0x6f1d2b60,0xd5a0,0x11cf,{0xbf,0xc7,0x44,0x45,0x53,0x54,0,0}};
constexpr StartupGuid query_interface_guid_005bf8c0={0x5944e682,0xc92e,0x11cf,{0xbf,0xc7,0x44,0x45,0x53,0x54,0,0}};
constexpr StartupGuid axis_x={0xa36d02e0,0xc9f3,0x11cf,{0xbf,0xc7,0x44,0x45,0x53,0x54,0,0}};
constexpr StartupGuid axis_y={0xa36d02e1,0xc9f3,0x11cf,{0xbf,0xc7,0x44,0x45,0x53,0x54,0,0}};
constexpr StartupGuid axis_z={0xa36d02e2,0xc9f3,0x11cf,{0xbf,0xc7,0x44,0x45,0x53,0x54,0,0}};
struct ObjectFormat {const StartupGuid* guid;std::uint32_t offset,type,flags;};
struct DataFormat {std::uint32_t size,object_size,flags,data_size,object_count;const ObjectFormat* objects;};
struct PropertyValue {std::uint32_t size,header_size,object,how,value;};
static_assert(sizeof(StartupGuid)==16 && sizeof(ObjectFormat)==16 && sizeof(DataFormat)==24 && sizeof(PropertyValue)==20);
const ObjectFormat mouse_objects[7]={
    {&axis_x,0,0x00ffff03,0},{&axis_y,4,0x00ffff03,0},{&axis_z,8,0x80ffff03,0},
    {nullptr,12,0x00ffff0c,0},{nullptr,13,0x00ffff0c,0},
    {nullptr,14,0x80ffff0c,0},{nullptr,15,0x80ffff0c,0}};
const DataFormat mouse_format={24,16,2,16,7,mouse_objects};

template<class Function> Function method(void* object,std::uint32_t slot) {
    return reinterpret_cast<Function>((*reinterpret_cast<void***>(object))[slot]);
}
using CreateDevice=std::uint32_t (__stdcall*)(void*,const StartupGuid*,void**,void*);
using QueryInterface=std::uint32_t (__stdcall*)(void*,const StartupGuid*,void**);
using Release=std::uint32_t (__stdcall*)(void*);
using SetDataFormat=std::uint32_t (__stdcall*)(void*,const DataFormat*);
using SetProperty=std::uint32_t (__stdcall*)(void*,const void*,const PropertyValue*);
}

std::uint32_t __cdecl startup_subsystem_result_00536e50() {
    // The original property-result word aliases cursor.x on the x86 stack.
    StartupPoint cursor;
    if (!startup_mouse_initialized_0069e0a0) {
        startup_mouse_initialized_0069e0a0=1;
        startup_frame_init_00572690();
        window_handler_register_0053a800(0x20a,
            static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(&startup_mouse_callback_00537020)));
    }
    if (!startup_directinput_0069e098) {
        const auto create_result=startup_directinput_create_0056e940(
            window_module_handle(nullptr),0x500,&startup_directinput_0069e098,nullptr);
        if (create_result) {
            startup_directinput_cleanup_00537070();
        } else {
            void* temporary=nullptr;
            const auto device_result=method<CreateDevice>(startup_directinput_0069e098,3)(
                startup_directinput_0069e098,&create_device_guid_005bf9a0,&temporary,nullptr);
            if (device_result) {
                startup_directinput_cleanup_00537070();
            } else {
                const auto query_result=method<QueryInterface>(temporary,0)(
                    temporary,&query_interface_guid_005bf8c0,&startup_mouse_device_0069e09c);
                method<Release>(temporary,2)(temporary);
                if (query_result) {
                    startup_directinput_cleanup_00537070();
                } else if (method<SetDataFormat>(startup_mouse_device_0069e09c,11)(
                        startup_mouse_device_0069e09c,&mouse_format)) {
                    startup_directinput_cleanup_00537070();
                } else {
                    const PropertyValue property={20,16,0,0,1};
                    const auto property_result=method<SetProperty>(startup_mouse_device_0069e09c,6)(
                        startup_mouse_device_0069e09c,
                        reinterpret_cast<const void*>(static_cast<std::uintptr_t>(2)),&property);
                    cursor.x=property_result==0 ? 1 : 0;
                    if (property_result) startup_directinput_cleanup_00537070();
                }
            }
        }
    }

    startup_mouse_mode_0069e078=2;
    startup_mouse_slot0_0069e07c=0;
    startup_mouse_slot1_0069e080=0;
    startup_mouse_slot2_0069e084=0;
    for (auto& flag:startup_mouse_flags_0069e088) flag=0;
    (void)startup_mouse_mode_005370c0(8,2);
    (void)startup_mouse_mode_005370c0(9,1);
    render_display_video_base_00537600(0,0,0,
        render_display_texture_width_005deac8,render_display_texture_height_005deacc,100);
    if (startup_directinput_0069e098)
        (void)startup_mouse_mode_005370c0(7,4);
    if (!startup_mouse_exit_registered_0069e0a4) {
        thread_exit_register_00557380(startup_mouse_exit_005370b0);
        startup_mouse_exit_registered_0069e0a4=1;
    }
    (void)startup_get_cursor_pos(&cursor);
    if (startup_screen_to_client(startup_window_handle_00557460(),&cursor)) {
        (void)startup_mouse_mode_005370c0(3,static_cast<std::uint32_t>(cursor.x));
        (void)startup_mouse_mode_005370c0(4,static_cast<std::uint32_t>(cursor.y));
    }
    return startup_mouse_initialized_0069e0a0;
}

void __cdecl startup_subsystem_00536e50() {
    (void)startup_subsystem_result_00536e50();
}

} // namespace porsche
