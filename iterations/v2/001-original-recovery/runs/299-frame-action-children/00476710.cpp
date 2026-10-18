#include "../297-frame-action/action_297.hpp"
namespace porsche {
namespace {
using U=std::uint32_t;
U read299(U p) { return *reinterpret_cast<volatile U*>(p); }
void write299(U p,U v) { *reinterpret_cast<volatile U*>(p)=v; }
using Destroy299=void(__thiscall*)(void*,U);
using Update299=void(__thiscall*)(void*);
}
void __thiscall FrameActionBoundary_297::update_00476710(U index) {
    // ESI caches this group across callbacks, even if self+0xc changes.
    const U group=read299(reinterpret_cast<U>(this)+0xc)+index*0x38;
    U count=read299(group+0x14),iteration=0,offset=0;
    if(count) {
        do {
            const U record=read299(group+0x34)+offset;
            const U item=read299(record);
            const auto flag=*reinterpret_cast<volatile std::uint8_t*>(item+4);
            if(!flag && !read299(record+0x10)) {
                if(item) reinterpret_cast<Destroy299>(read299(read299(item)))(reinterpret_cast<void*>(item),1);
                const U destination=read299(group+0x34)+offset;
                for(U i=0;i<6;++i) write299(destination+i*4,0);
            } else if(item && !flag) {
                reinterpret_cast<Update299>(read299(read299(item)+0x1c))(reinterpret_cast<void*>(item));
            }
            count=read299(group+0x14);
            ++iteration;
            offset+=0x18;
        } while(iteration<count);
    }
    write299(group+0x14,0);
}
}
