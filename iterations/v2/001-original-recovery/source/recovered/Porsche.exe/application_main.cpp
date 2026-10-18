#include "porsche/application_main.hpp"
#include "porsche/application_heap.hpp"
#include "porsche/application_fe.hpp"
#include "porsche/render_activate.hpp"
#include "porsche/render_startup.hpp"
#include "porsche/render_display.hpp"
#include "porsche/resource_paths.hpp"
#include "porsche/startup_services.hpp"
#include "porsche/fe_stream.hpp"
#include <cstdint>
#include <cstring>

namespace porsche {
namespace {
constexpr std::uint32_t kFeArena=0x006573e8;
std::uint8_t net_byte(const void* p,std::uint32_t offset) {
    return static_cast<const std::uint8_t*>(p)[offset];
}
std::uint32_t net_word(const void* p,std::uint32_t offset) {
    std::uint32_t value; std::memcpy(&value,static_cast<const std::uint8_t*>(p)+offset,4); return value;
}
void net_set_byte(void* p,std::uint32_t offset,std::uint8_t value) {
    static_cast<std::uint8_t*>(p)[offset]=value;
}
bool network_ready_for_start(void* p) {
    if(!p) return false;
    return net_byte(p,0xbf)!=0 ||
        (net_byte(p,0xbe)!=0 && static_cast<std::int32_t>(net_word(p,0xdc))>=0);
}
bool network_ready_for_mode(void* p) {
    if(!p || net_word(p,8)==0) return false;
    return net_byte(p,0xbf)==0 && net_byte(p,0xc5)==0 &&
        net_byte(p,0xbe)!=0 && static_cast<std::int32_t>(net_word(p,0xdc))>=0;
}
void copy_fe_string_to_network(void* network) {
    if(!global_00657a84[0] || !network) return;
    net_set_byte(network,0x58,99);
    const auto n=std::strlen(global_00657a84)+1;
    std::memcpy(static_cast<std::uint8_t*>(network)+0x59,global_00657a84,n);
}
void apply_fe_records(const std::uint32_t* p) {
    while(*p) {
        fe_apply_004b4b80(p);
        p+=fe_record_words_004b4cd0(p);
    }
}
}

// 004b6a50..004b6fe5. Control flow and direct state accesses follow the
// original body; opaque subsystem effects are exposed as typed boundaries.
std::int32_t __cdecl app_main_004b6a50(std::int32_t argc,char** argv) {
    std::uint32_t swap_bytes=0x08000000;
    void* swap_probe=application_page_alloc_0059ed40(&swap_bytes);
    application_page_release_0059ed90(swap_probe);
    if(!swap_probe) {
        application_main_memory_dialog("Insufficient space in the swap file.  Please make additional space available and try again.","Memory full");
        startup_exit_005a246e(1);
    }

    startup_cd_relaunch_004a5c30();
    startup_services_004a5410();
    application_main_create_directory(0x0065b360);
    resource_paths_0059d650();
    // The original 0053c290 clears 0x3e24 bytes beginning at 006573e8.
    // The original helper is adapted over the shared, bounded FE arena span.
    application_main_fill_fe_arena_0053c290(kFeArena,0,0x3e24);

    auto* initial=fe_build_004b6660(argc,argv);
    application_fe_apply_release_004b6ad8(initial);
    application_main_setup_heaps(0x40000,0x8000);
    application_main_log("Initializing rendering\n");
    render_startup_00467470();

    copy_fe_string_to_network(startup_network_00628c70);
    if(global_00657a60) {
        if(startup_network_00628c70) application_main_network_poll(0,0);
        while(!startup_network_00628c70) {}
        while(!network_ready_for_start(startup_network_00628c70)) {}
    } else if(global_00657a64) {
        if(startup_network_00628c70) application_main_network_wait(1,0,&global_00657a64);
        while(!startup_network_00628c70) {}
        while(!network_ready_for_start(startup_network_00628c70)) {}
    }

    global_006577d8=0;
    global_006577dc=0;
    global_006573e8=0;
    std::uint8_t setup_started=0;
    bool frame_active=false;
    std::int32_t game_setup_result=0;
    bool run=true;
    while(run) {
        auto* stream=fe_build_004b6660(argc,argv);
        if(fe_enabled_0065b298) {
            if(!setup_started && !global_0065743c) {
                setup_started=1;
                application_main_function_004dd600();
            }
            ApplicationSetupContext setup_context;
            application_setup_context_construct_004d1a90(&setup_context,nullptr);
            game_setup_result=application_main_game_setup(&setup_context,nullptr,
                "gamesetup",stream,0);
            global_00657e34=1;
            application_setup_context_destroy_004d1ba0(&setup_context,nullptr);
        }
        if(game_setup_result!=1) {
            apply_fe_records(stream);
            render_display_reconfigure_00467fc0(render_display_00628130,
                render_width_00657a48,render_height_00657a4c,
                render_display_requested_mode_00657a50,2);
            frame_active=1;
            application_main_front_end_display(stream);
            application_main_function_004a4a70(0);

            if(global_006573e8==3 && startup_network_00628c70) {
                auto* n=startup_network_00628c70;
                const auto connected=net_word(n,8)!=0;
                const auto pending=connected && net_byte(n,0xbf)==0 &&
                    net_byte(n,0xc5)==0 && net_byte(n,0xbe)!=0 &&
                    static_cast<std::int32_t>(net_word(n,0xdc))<0;
                const auto continuing=connected && net_byte(n,0xbf)==0 &&
                    net_byte(n,0xc5)==0 && net_byte(n,0xbe)!=0 &&
                    static_cast<std::int32_t>(net_word(n,0xdc))>=0;
                if(!continuing) frame_active=0;
                if(pending) {
                    net_set_byte(n,0xc5,1);
                    net_set_byte(n,0xbc,1);
                    net_set_byte(n,0xc4,0);
                    application_main_network_action(-2,-1);
                }
            }
            free_00531f90(stream);
            if(frame_active) application_main_function_004b67b0();
        }
        if(game_setup_result!=1 && frame_active && global_00606a88) {
            for(;;) {
                global_00606a88=0;
                application_main_function_004acb80();
                application_main_function_004a88a0();
                application_main_function_00471b60();
                application_main_function_00414eb0();
                application_main_function_004640b0();
                application_main_function_00413ea0();
                application_main_function_004a6e30();
                auto* n=startup_network_00628c70;
                if(n && net_word(n,8)!=0 && net_byte(n,0xbf)==0)
                    application_main_function_0048cdf0();
                n=startup_network_00628c70;
                if(n && net_word(n,8)!=0 && net_byte(n,0xbf)==0)
                    application_main_function_0048cdf0();
                application_main_function_00425780();
                application_main_function_005366e0(0);
                if(global_006573e8==3 && network_ready_for_mode(startup_network_00628c70)) {
                    application_main_function_004152e0();
                } else if(global_006573e8==3 && startup_network_00628c70) {
                    auto* n2=startup_network_00628c70;
                    if(net_word(n2,8)!=0 && net_byte(n2,0xbf)==0 &&
                       net_byte(n2,0xc5)==0 && net_byte(n2,0xbe)!=0 &&
                       static_cast<std::int32_t>(net_word(n2,0xdc))<0) {
                        net_set_byte(n2,0xc5,1);
                        net_set_byte(n2,0xbc,1);
                        net_set_byte(n2,0xc4,0);
                        application_main_network_action(-2,-1);
                    }
                } else if(global_006573e8!=3) {
                    application_main_function_004152e0();
                }
                bool transition=false;
                if(global_006573e8!=3) {
                    const auto mode_a=global_00657424;
                    const auto mode_b=global_00657428;
                    transition=mode_a<=1 || mode_b!=0;
                    if(transition) {
                        global_00657424=2;
                        global_00606874=(mode_b==0)?1u:0u;
                        application_main_function_00412030();
                        global_005e99f4=2;
                        global_00657428=0;
                    }
                }
                if(transition) continue; // 004b6f18 -> 004b6d9f
                if(global_00606a88) continue; // 004b6f23 -> 004b6d9f
                break;
            }
        }
        if(game_setup_result!=1 && frame_active) {
            application_main_function_004b68f0();
            auto* net=startup_network_00628c70;
            if(net && net_word(net,8)!=0 && net_byte(net,0xbf)==0 &&
               net_byte(net,0xbe)!=0 && static_cast<std::int32_t>(net_word(net,0xdc))>=0)
                application_main_function_0048dad0();
        }
        auto* net=startup_network_00628c70;
        if(global_006573e8==3 && net && net_word(net,8)!=0 &&
           net_byte(net,0xbf)==0 &&
           (net_byte(net,0xbe)==0 || static_cast<std::int32_t>(net_word(net,0xdc))<0)) {
            application_main_function_0048e6f0();
        }
        if(fe_enabled_0065b298 && game_setup_result!=1) continue;
        run=false;
    }

    application_main_function_004a6960();
    application_main_function_00563d30();
    application_main_function_004a54b0();
    application_main_function_00467740();
    application_main_function_004a54e0();
    return 0;
}
}
