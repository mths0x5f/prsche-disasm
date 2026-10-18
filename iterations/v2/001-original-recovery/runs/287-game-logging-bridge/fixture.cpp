// Private cutpoints only. Never include this TU in the game library.
#include "porsche/application_main.hpp"
#include "porsche/formatter_stdio.hpp"
#include "porsche/formatter_entry.hpp"
#include <cstdio>
#include <cstring>

using U=std::uint32_t;
static_assert(sizeof(void*)==4,"native x86 fixture");
U failures287,cases287,extra287,mode287,result287,seed287;
U arguments287[8],events287[64],event_count287;
U saved_sp287,saved_bp287,saved_bx287,saved_si287,saved_di287;
U seen_sp287,entry_sp287,seen_eax287,seen_bp287,seen_bx287,seen_si287,seen_di287,seen_flags287;
U target287,format287;
unsigned char arena287[4096];
const char literal287[]="Initializing rendering\n";
void require287(bool value){if(!value)++failures287;}
void event287(U code,U a=0,U b=0){require287(event_count287+3<=64);if(event_count287+3<=64){events287[event_count287++]=code;events287[event_count287++]=a;events287[event_count287++]=b;}}
namespace porsche {
FormatterOriginalDescriptor32 formatter_iob_entries_005e54e8[20]{};
U formatter_output_allocations_006afcf8;
void __cdecl exit_registry_lock_api_005a4ba4(U id){event287(1,id);}
void __cdecl exit_registry_unlock_api_005a4c05(U id){event287(5,id);}
void* __cdecl exit_registry_malloc_005a3be5(U bytes){event287(3,bytes);return mode287==2?nullptr:arena287;}
U __cdecl cleanup_is_character_device_005abf35(U id){event287(2,id);return mode287!=0;}
int __cdecl formatter_cleanup_file_write_005a9e49(U id,const void*,int size){event287(6,id,static_cast<U>(size));return size;}
void __stdcall formatter_lowio_critical_enter(void*){require287(false);}
void __stdcall formatter_lowio_critical_leave(void*){require287(false);}
std::int32_t __cdecl formatter_core_005a4371(FormatterOriginalDescriptor32* d,const char* format,const U* args){
    require287(d==&formatter_iob_entries_005e54e8[1]);
    require287(format==literal287);
    require287(args!=nullptr && (reinterpret_cast<U>(args)&3u)==0);
    // A bridge call has only its format argument: never read extra slots.
    if(extra287){require287(reinterpret_cast<U>(args)==entry_sp287+8);for(U i=0;i<8;++i)require287(args[i]==arguments287[i]);}
    event287(4,result287,extra287);
    return static_cast<std::int32_t>(result287);
}
// Exact original 65B. Only CALL REL32 and stdout absolute pointer relocate.
__declspec(naked) int __cdecl reference_printf287(const char*,...){__asm{
 push ebx
 push esi
 mov esi,offset formatter_iob_entries_005e54e8+32
 push edi
 push esi
 push 1
 call formatter_stdio_lock_index_005a3719
 push esi
 call formatter_stdio_temporary_buffer_005a533e
 mov edi,eax
 lea eax,[esp+20h]
 push eax
 push dword ptr[esp+20h]
 push esi
 call formatter_core_005a4371
 push esi
 push edi
 mov ebx,eax
 call formatter_stdio_finish_buffer_005a53cb
 push esi
 push 1
 call formatter_stdio_unlock_index_005a376b
 add esp,28h
 mov eax,ebx
 pop edi
 pop esi
 pop ebx
 ret
}}
}
__declspec(naked) void invoke287(){__asm{
 mov saved_sp287,esp
 mov saved_bp287,ebp
 mov saved_bx287,ebx
 mov saved_si287,esi
 mov saved_di287,edi
 cmp extra287,0
 je format_only
 push arguments287[28]
 push arguments287[24]
 push arguments287[20]
 push arguments287[16]
 push arguments287[12]
 push arguments287[8]
 push arguments287[4]
 push arguments287[0]
 format_only:
 push format287
 mov ebp,13579bdfh
 mov ebx,2468ace0h
 mov esi,89abcdefh
 mov edi,0fedcba98h
 mov eax,esp
 sub eax,4
 mov entry_sp287,eax
 cld
 call dword ptr target287
 mov seen_eax287,eax
 mov seen_sp287,esp
 mov seen_bp287,ebp
 mov seen_bx287,ebx
 mov seen_si287,esi
 mov seen_di287,edi
 pushfd
 pop seen_flags287
 mov esp,saved_sp287
 mov ebp,saved_bp287
 mov ebx,saved_bx287
 mov esi,saved_si287
 mov edi,saved_di287
 ret
}}
struct Snapshot287{unsigned char files[640];U buffers[2],allocations,events[64],count,eax;};
void reset287(){
    std::memset(porsche::formatter_iob_entries_005e54e8,0xa5,640);
    auto& d=porsche::formatter_iob_entries_005e54e8[1];
    std::memset(&d,0,32);d.flags=mode287==3?0x100:0;
    reinterpret_cast<U*>(&d)[4]=0x80000000u|seed287;
    porsche::formatter_stdio_buffers_006afd60[0]=nullptr;
    porsche::formatter_stdio_buffers_006afd60[1]=nullptr;
    porsche::formatter_output_allocations_006afcf8=0xffffffffu;
    std::memset(arena287,0x5a,sizeof(arena287));std::memset(events287,0,sizeof(events287));event_count287=0;
}
Snapshot287 run287(U target){
    reset287();target287=target;format287=reinterpret_cast<U>(literal287);invoke287();
    require287(seen_sp287==entry_sp287+4 && seen_bp287==0x13579bdfu && seen_bx287==0x2468ace0u && seen_si287==0x89abcdefu && seen_di287==0xfedcba98u && !(seen_flags287&0x400));
    if(extra287)require287(seen_eax287==result287);
    require287(event_count287>=9 && events287[0]==1 && events287[1]==29 && events287[event_count287-3]==5 && events287[event_count287-2]==29);
    Snapshot287 s{};std::memcpy(s.files,porsche::formatter_iob_entries_005e54e8,640);
    s.buffers[0]=reinterpret_cast<U>(porsche::formatter_stdio_buffers_006afd60[0]);s.buffers[1]=reinterpret_cast<U>(porsche::formatter_stdio_buffers_006afd60[1]);
    s.allocations=porsche::formatter_output_allocations_006afcf8;std::memcpy(s.events,events287,sizeof(events287));s.count=event_count287;s.eax=extra287?seen_eax287:0;return s;
}
int main(){
    const U results[]={0,1,0x7fffffffu,0x80000000u,0xffffffffu,0xa5a5a5a5u};
    for(seed287=0;seed287<8;++seed287){for(U i=0;i<8;++i)arguments287[i]=(0x9e3779b9u*(i+1))^(seed287*0x1234567u);
        for(mode287=0;mode287<4;++mode287)for(U r=0;r<6;++r){extra287=1;result287=results[r];auto original=run287(reinterpret_cast<U>(&porsche::reference_printf287));auto native=run287(reinterpret_cast<U>(&porsche::formatter_stdio_printf_005a177b));require287(std::memcmp(&original,&native,sizeof(original))==0);++cases287;}
        for(mode287=0;mode287<4;++mode287){extra287=0;result287=results[seed287%6];auto original=run287(reinterpret_cast<U>(&porsche::reference_printf287));auto native=run287(reinterpret_cast<U>(&porsche::application_main_log));require287(std::memcmp(&original,&native,sizeof(original))==0);++cases287;}
    }
    std::printf("{\"cases\":%u,\"failures\":%u,\"direct_printf\":192,\"format_only_bridge\":32}\n",cases287,failures287);
    return failures287?1:0;
}
