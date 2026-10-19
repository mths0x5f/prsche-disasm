#include "porsche/application_pool.hpp"
#include "porsche/disk_open.hpp"
#include "porsche/heap_locks.hpp"
namespace porsche {
namespace {
using U=std::uint32_t;
template<class T>T* pointer307(T* const* p){return *reinterpret_cast<T* const volatile*>(p);}
std::int32_t count307(){return *reinterpret_cast<volatile std::int32_t*>(&physical_count_006af080);}
}
void __cdecl application_pool_disk_slots_release_005918c0(){
    if(!pointer307(&physical_files_006af084))return;
    heap_enter_005322b0(pointer307(&disk_slot_mutex_006af07c));
    std::int32_t count=count307();
    U index=0,offset=0;
    if(count>0){
        do{
            auto* const base=reinterpret_cast<std::uint8_t*>(pointer307(&physical_files_006af084));
            if(*reinterpret_cast<volatile std::uint8_t*>(base+offset))
                (void)file_physical_close_00592290(reinterpret_cast<void*>(~index));
            count=count307();
            ++index;offset+=0x20;
        }while(static_cast<std::int32_t>(index)<count);
    }
    (void)file_object_free_0056e640(pointer307(&physical_files_006af084));
    physical_files_006af084=nullptr;
    auto* mutexes=reinterpret_cast<void* volatile*>(disk_mutexes_006aeffc);
    for(U i=0;i<32;++i){
        void* const mutex=mutexes[i];
        if(mutex){heap_lock_destroy_005322d0(mutex);mutexes[i]=nullptr;}
    }
    heap_leave_005322c0(pointer307(&disk_slot_mutex_006af07c));
    heap_lock_destroy_005322d0(pointer307(&disk_slot_mutex_006af07c));
    disk_slot_mutex_006af07c=nullptr;
}
}
