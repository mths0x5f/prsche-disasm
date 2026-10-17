#include "porsche/files.hpp"
namespace porsche {
static void error(std::uint32_t line,const char* message) {
    diagnostic_file_005deb74_set("\\real\\pc\\nfile.c");diagnostic_line_005deb78=line;
    diagnostic_handler_005debf0(message);
}

std::uint32_t __cdecl operation_queue_00568200(FileOperation* op) {
    auto* device=devices_006a5c7c+(op->id&31);
    if(!device) error(0xf9,"FILE_queueop - ATTEMPT TO QUEUE FILEOP ON NON-EXISTANT DEVICE.\n");
    io_sorted_00580850(&device->queued,reinterpret_cast<IoNode*>(op));
    file_event_signal_0055fb30(device->queued_event);return op->id;
}

}
