#include "frame_init.hpp"
#include "../364-mouse-startup-children/startup_mouse_children.hpp"
#include "porsche/render_driver_calls.hpp"
#include "porsche/render_event_route.hpp"
namespace porsche {
static_assert(sizeof(std::uintptr_t)==4,"original callback cells are DWORDs");
std::uint32_t startup_cursor_z_005deab8=0;
std::uint32_t startup_frame_counter_006a644c=0;
// Raw PE defaults are all005367b0; transport its canonical native address.
std::uintptr_t startup_frame_callback_005debe0=reinterpret_cast<std::uintptr_t>(&render_event_default_callback_005367b0);
std::uintptr_t startup_frame_callback_005debe4=reinterpret_cast<std::uintptr_t>(&render_event_default_callback_005367b0);
std::uintptr_t startup_frame_callback_005debe8=reinterpret_cast<std::uintptr_t>(&render_event_default_callback_005367b0);
// Porsche.exe ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39.
// 00572640..00572667, complete RET, copy all three original DWORDs.
std::uint32_t __cdecl startup_frame_copy_00572640() {
    startup_cursor_x_005deab0=static_cast<std::int32_t>(render_driver_limit_a_006a6448);
    startup_cursor_y_005deab4=static_cast<std::int32_t>(render_driver_limit_b_006a6444);
    startup_cursor_z_005deab8=render_driver_limit_c_006a6440;
    return startup_cursor_z_005deab8;
}
// INC/DEC do not define EAX. Unsigned storage preserves modulo2^32 behavior.
void __cdecl startup_frame_increment_00572670() { ++startup_frame_counter_006a644c; }
void __cdecl startup_frame_decrement_00572680() { --startup_frame_counter_006a644c; }
// 00572690..005726e1, complete RET; original caller00536e69 discards EAX.
void __cdecl startup_frame_init_00572690() {
    const auto width=render_display_texture_width_005deac8;
    const auto height=render_display_texture_height_005deacc;
    render_driver_bounds_c_006a6430=width;
    render_driver_bounds_a_006a643c=0;
    render_driver_bounds_b_006a6438=0;
    startup_frame_counter_006a644c=0;
    render_driver_bounds_d_006a6434=height;
    render_event_dispatch_gate_005deaac=1;
    startup_frame_callback_005debe0=reinterpret_cast<std::uintptr_t>(&startup_frame_decrement_00572680);
    startup_frame_callback_005debe4=reinterpret_cast<std::uintptr_t>(&startup_frame_increment_00572670);
    startup_frame_callback_005debe8=reinterpret_cast<std::uintptr_t>(&startup_frame_copy_00572640);
}
}
