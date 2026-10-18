#include "action_297.hpp"
namespace porsche {
namespace {
using U=std::uint32_t;
U read(U p) { return *reinterpret_cast<volatile U*>(p); }
void write(U p,U v) { *reinterpret_cast<volatile U*>(p)=v; }
using Destroy=void(__thiscall*)(void*,U);
using Update=void(__thiscall*)(void*);
}
void __thiscall FrameAction_290::invoke_00476170() {
    const U self=reinterpret_cast<U>(this);
    U index=0,offset=0;
    if(!read(read(self+4)+0x18)) return;
    do {
        if(read(read(self+0xc)+offset+0x1c)) {
            reinterpret_cast<FrameActionBoundary_297*>(this)->update_00476710(index);
            const U table=read(self+0xc);
            const U item=read(table+offset+0x1c);
            const auto flag=*reinterpret_cast<volatile std::uint8_t*>(item+4);
            if(!flag && !read(table+offset+0x2c)) {
                if(item) reinterpret_cast<Destroy>(read(read(item)))(reinterpret_cast<void*>(item),1);
                write(read(self+0xc)+offset+0x1c,0);
                const U base=read(self+0xc)+offset;
                const U destination=read(base+0x34);
                // Original REP MOVSD copies six DWORDs forward, including overlap.
                for(U i=0;i<6;++i) write(destination+i*4,read(base+0x1c+i*4));
            } else if(item && !flag) {
                reinterpret_cast<Update>(read(read(item)+0x1c))(reinterpret_cast<void*>(item));
            }
        }
        ++index;
        write(read(self+0xc)+offset+8,0);
        offset+=0x38;
    } while(index<read(read(self+4)+0x18));
}
}
