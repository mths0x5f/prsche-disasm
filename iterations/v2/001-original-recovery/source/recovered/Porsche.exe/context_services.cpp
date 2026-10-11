#include "porsche/context_services.hpp"
#include <cstring>

namespace porsche {
namespace {
using U=std::uint32_t;
U raw(const void* p){return reinterpret_cast<U>(p);}
void* ptr(U x){return reinterpret_cast<void*>(x);}
U load(U p){U x;std::memcpy(&x,ptr(p),4);return x;}
void store(U p,U x){std::memcpy(ptr(p),&x,4);}
void zero(U object){store(object,0);store(object+4u,0);store(object+8u,0);}
void initialize(U object,U bytes){
    if(bytes<=0xfffffffeu){
        U block=0;
        if(bytes)block=raw(application_context_member_storage_004211d0(bytes,0));
        store(object,block);store(object+4u,block);store(object+8u,block+bytes);
    }
}
}
void* __fastcall context_identity_00423610(void* object,void*){return object;}
void* __fastcall context_empty_range_00505810(void* object,void*,U){zero(raw(object));return object;}
U __cdecl context_strlen_004d55c0(const char* text){
    U address=raw(text),remaining=0xffffffffu;
    while(remaining){
        const auto byte=*reinterpret_cast<const unsigned char*>(address);
        ++address;--remaining;if(byte==0)break;
    }
    return (~remaining)-1u;
}
void* __fastcall context_string_construct_004d64a0(void* object,void*,const char* text,U){
    const U dest=raw(object),source=raw(text);
    zero(dest);
    const U length=context_strlen_004d55c0(text),end=source+length;
    initialize(dest,length+1u);
    const U block=load(dest);
    (void)context_move_005a1a40(ptr(block),text,length);
    const U finish=(block-source)+end;
    store(dest+4u,finish);*reinterpret_cast<unsigned char*>(finish)=0;
    return object;
}
void* __fastcall context_string_assign_range_004298a0(void* object,void*,const void* first,const void* last){
    const U dest=raw(object),begin=raw(first),end=raw(last),length=end-begin;
    initialize(dest,length+1u);
    const U block=load(dest);
    (void)context_move_005a1a40(ptr(block),first,length);
    const U finish=end+(block-begin);
    store(dest+4u,finish);*reinterpret_cast<unsigned char*>(finish)=0;
    return ptr(finish);
}
void* __fastcall context_string_copy_00429bf0(void* object,void*,const void* source){
    const U dest=raw(object),from=raw(source);
    zero(dest);
    const U end=load(from+4u),begin=load(from),length=end-begin;
    initialize(dest,length+1u);
    const U block=load(dest);
    (void)context_move_005a1a40(ptr(block),ptr(begin),length);
    const U finish=end+(block-begin);
    store(dest+4u,finish);*reinterpret_cast<unsigned char*>(finish)=0;
    return object;
}
void __fastcall context_string_destroy_00429840(void* object,void*){
    const U from=raw(object),block=load(from),bytes=load(from+8u)-block;
    if(block&&bytes){
        const U state=raw(application_context_heap_state_005e4fe8())+0x28u;
        if(bytes>0x100u){context_table_release_0059ecd0(ptr(block));return;}
        heap_enter_005322b0(ptr(load(state)));
        const U slot=state+0xcu+((bytes-1u)>>3u)*4u;
        store(block+4u,load(slot));store(slot,block);
        heap_leave_005322c0(ptr(load(state)));
    }
}
std::int32_t __fastcall context_vector_count_004d6510(const void* object,void*){
    const U from=raw(object);
    const U end=load(from+4u),begin=load(from);
    return static_cast<std::int32_t>(end-begin)>>2u;
}
void* __fastcall context_vector_at_004d6520(const void* object,void*,U index){return ptr(load(raw(object))+index*4u);}
void __fastcall context_vector_pop_004d6530(void* object,void*){const U field=raw(object)+4u;store(field,load(field)-4u);}
U __cdecl context_word_not_equal_004d67b0(const void* first,const void* second){
    const U a=load(raw(first)),b=load(raw(second));return a!=b?1u:0u;
}
}
