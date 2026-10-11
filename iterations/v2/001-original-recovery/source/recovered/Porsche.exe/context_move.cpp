#include "porsche/context_move.hpp"

namespace porsche {
namespace {
using U=std::uint32_t;
void byte(U destination,U source){
    const auto value=*reinterpret_cast<volatile const std::uint8_t*>(source);
    *reinterpret_cast<volatile std::uint8_t*>(destination)=value;
}
void word(U destination,U source){
    const auto value=*reinterpret_cast<volatile const U*>(source);
    *reinterpret_cast<volatile U*>(destination)=value;
}
}

// Porsche.exe 005a1a40..005a1d74. The DWORD loops preserve the exact
// access ordering of both the short jump-table and REP MOVSD paths.
// Volatile accesses retain self-copy reads/writes and source access widths.
void* __cdecl context_move_005a1a40(void* destination,const void* source,U bytes){
    U out=reinterpret_cast<U>(destination),in=reinterpret_cast<U>(source);
    const U source_end=in+bytes;
    if(out>in && out<source_end){
        out+=bytes;in+=bytes;
        if(bytes>=4u){
            const U prefix=out&3u;
            for(U i=0;i<prefix;++i){--out;--in;byte(out,in);}
            bytes-=prefix;
            const U words=bytes>>2u;
            for(U i=0;i<words;++i){out-=4u;in-=4u;word(out,in);}
            bytes&=3u;
        }
        while(bytes){--out;--in;byte(out,in);--bytes;}
    }else{
        if(bytes>=4u){
            const U alignment=out&3u;
            const U prefix=alignment?4u-alignment:0u;
            for(U i=0;i<prefix;++i){byte(out,in);++out;++in;}
            bytes-=prefix;
            const U words=bytes>>2u;
            for(U i=0;i<words;++i){word(out,in);out+=4u;in+=4u;}
            bytes&=3u;
        }
        while(bytes){byte(out,in);++out;++in;--bytes;}
    }
    return destination;
}
}
