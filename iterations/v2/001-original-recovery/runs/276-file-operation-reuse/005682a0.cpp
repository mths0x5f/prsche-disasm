#include "porsche/files.hpp"
namespace porsche {
static void error(std::uint32_t line,const char* message) {
    diagnostic_file_005deb74_set("\\real\\pc\\nfile.c");diagnostic_line_005deb78=line;
    diagnostic_handler_005debf0(message);
}

FileOperation* __cdecl operation_allocate_005682a0(std::uint32_t type,std::uint8_t group,void* context,std::uint32_t index) {
    auto* op=reinterpret_cast<FileOperation*>(io_pop_00580790(&free_operations_006a5c58));
    auto* device=devices_006a5c7c+index;
    if(!op) { error(0xd1,"FILE_allocateop - NO FREE OPS LEFT TO ALLOCATE.\n");return nullptr; }
    if(!device->initialized) file_start_device_00568390(index);
    op->group=group;op->type=type;op->status=0;op->flags &= 0xfffffff0;
    op->field14=0;op->handle=0;op->context=context;op->callback=nullptr;
    op->offset=0;op->count=0;op->buffer=nullptr;
    const auto lock=device->initialized ? io_lock_00580ea0(&device->queued) : 0;
    const auto next=(device->serial+1)&0xffffff;
    op->id=(device->serial<<5)|index;device->serial=next ? next : 1;
    if(device->initialized) io_unlock_00580ec0(&device->queued,lock);
    return op;
}

}
