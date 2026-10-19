#include "porsche/application_pool.hpp"
#include "porsche/file_worker.hpp"
#include "porsche/file_events.hpp"
#include "porsche/file_wait.hpp"
#include "porsche/network_workers_members.hpp"
#include "porsche/heap_locks.hpp"
namespace porsche {
namespace {
using U=std::uint32_t;
U read305(const void* p){return *reinterpret_cast<const volatile U*>(p);}
template<class T>T* pointer305(T* const* p){return *reinterpret_cast<T* const volatile*>(p);}
}
void __cdecl application_pool_shutdown_005678f0(){
    if(!pointer305(&devices_006a5c7c))return;
    IoNode* node=io_pop_00580790(&free_auxiliary_006a5c38);
    while(node){
        (void)file_physical_close_00592290(reinterpret_cast<void*>(read305(reinterpret_cast<std::uint8_t*>(node)+0xc)));
        (void)file_object_free_0056e640(node);
        node=io_pop_00580790(&free_auxiliary_006a5c38);
    }
    file_shutdown_006a5c80=1;
    for(U offset=0;offset<0xe00;offset+=0x70){
        auto* const device=reinterpret_cast<std::uint8_t*>(pointer305(&devices_006a5c7c))+offset;
        if(read305(device)){
            void* const queued=reinterpret_cast<void*>(read305(device+0x5c));
            (void)file_event_signal_0055fb30(queued);
            while(read305(device))(void)file_sleep_0055f740(0);
            (void)file_close_event_0055fc10(queued);
            (void)file_signal_close_0055fc80(reinterpret_cast<void*>(read305(device+0x64)));
            network_worker_queue_dispose_005806c0(reinterpret_cast<IoList*>(device+0x40));
            network_worker_queue_dispose_005806c0(reinterpret_cast<IoList*>(device+0x24));
        }
    }
    (void)file_object_free_0056e640(pointer305(&free_operation_arena_006a5c54));
    (void)file_object_free_0056e640(pointer305(&devices_006a5c7c));
    network_worker_queue_dispose_005806c0(&free_operations_006a5c58);
    network_worker_queue_dispose_005806c0(&free_auxiliary_006a5c38);
    heap_lock_destroy_005322d0(pointer305(&application_pool_lock_006a5c78));
    devices_006a5c7c=nullptr;
}
}
