#include "cursor_snapshot.hpp"
#include "porsche/window_shutdown.hpp"
#include "porsche/render_display.hpp"
#include <cstring>
namespace porsche {
std::uint8_t cursor_snapshot_prefix_005de650[12]{};
std::uint8_t cursor_snapshot_suffix_005de65e[30]={
    0,0,1,0,0,0,0,0,0,0,0,0,0,0,128,2,0,0,224,1,0,0,0,0,0,0,0,0,0,0};
namespace {
// Explicit original-address view; never access past a host object's bounds.
std::uint8_t& second_byte(std::uint32_t offset){
    if(offset<12)return cursor_snapshot_prefix_005de650[offset];
    if(offset==12)return window_shutdown_source_005de65c;
    if(offset==13)return window_shutdown_source_005de65d;
    if(offset<44)return cursor_snapshot_suffix_005de65e[offset-14];
    return reinterpret_cast<std::uint8_t*>(&window_shutdown_state_005de67c)[offset-44];
}
std::uint32_t second_read(std::uint32_t offset){
    std::uint32_t word;auto* bytes=reinterpret_cast<std::uint8_t*>(&word);
    for(std::uint32_t i=0;i<4;++i)bytes[i]=second_byte(offset+i);
    return word;
}
void second_write(std::uint32_t offset,std::uint32_t word){
    const auto* bytes=reinterpret_cast<const std::uint8_t*>(&word);
    for(std::uint32_t i=0;i<4;++i)second_byte(offset+i)=bytes[i];
}
}
// Proved callers supply an independent 96-byte stack buffer. REP MOVSD is
// represented by ordered DWORD reads/writes, rather than one aggregate copy.
void __cdecl startup_cursor_state_save_00570ed0(void* snapshot){
    auto* out=static_cast<std::uint8_t*>(snapshot);
    for(std::uint32_t i=0;i<12;++i){
        const auto word=window_shutdown_config_005de620[i];
        std::memcpy(out+4*i,&word,4);
    }
    for(std::uint32_t i=0;i<12;++i){
        const auto word=second_read(4*i);
        std::memcpy(out+48+4*i,&word,4);
    }
}
void __cdecl startup_cursor_state_restore_00570f00(const void* snapshot){
    const auto* in=static_cast<const std::uint8_t*>(snapshot);
    // The original restores the second block before the first.
    for(std::uint32_t i=0;i<12;++i){
        std::uint32_t word;std::memcpy(&word,in+48+4*i,4);second_write(4*i,word);
    }
    for(std::uint32_t i=0;i<12;++i){
        std::uint32_t word;std::memcpy(&word,in+4*i,4);window_shutdown_config_005de620[i]=word;
    }
    const auto mode=window_shutdown_mode_005de630;
    if(mode!=0&&window_shutdown_state_005de64c==0)
        window_shutdown_display_callback_006bd9b0(mode);
    else
        render_display_texture_bind_00534480(const_cast<void*>(snapshot));
}
}
