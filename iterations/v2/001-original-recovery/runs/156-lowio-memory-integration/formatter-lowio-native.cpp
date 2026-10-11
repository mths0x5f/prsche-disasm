#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include "porsche/formatter_lowio.hpp"
#include <cstdio>
#include <cstring>
#include <initializer_list>

struct Worker { CRITICAL_SECTION* lock; HANDLE started; HANDLE acquired; };
DWORD WINAPI enter_from_worker(void* opaque) {
    auto* worker=static_cast<Worker*>(opaque);
    SetEvent(worker->started);
    porsche::formatter_lowio_critical_enter(worker->lock);
    SetEvent(worker->acquired);
    porsche::formatter_lowio_critical_leave(worker->lock);
    return 0;
}
int main() {
    using namespace porsche;
    FormatterLowioStartupInfo32 info{};STARTUPINFOA direct{};
    formatter_lowio_startup_info(&info);GetStartupInfoA(&direct);
    if(info.reserved_bytes!=direct.cbReserved2 || info.reserved!=direct.lpReserved2 ||
       info.standard_handles[0]!=reinterpret_cast<std::uint32_t>(direct.hStdInput) ||
       info.standard_handles[1]!=reinterpret_cast<std::uint32_t>(direct.hStdOutput) ||
       info.standard_handles[2]!=reinterpret_cast<std::uint32_t>(direct.hStdError)) return 1;
    for(const int selector:{-10,-11,-12}) {
        const auto handle=formatter_lowio_get_standard(selector);
        if(handle!=reinterpret_cast<std::uint32_t>(GetStdHandle(static_cast<DWORD>(selector)))) return 2;
        if(formatter_lowio_set_standard(selector,handle)==0) return 3;
        if(formatter_lowio_get_standard(selector)!=handle) return 4;
    }
    if(formatter_lowio_set_count(64)!=SetHandleCount(64))return 5;
    HANDLE read=nullptr,write=nullptr;
    if(!CreatePipe(&read,&write,nullptr,0))return 6;
    const auto type=formatter_lowio_file_type(reinterpret_cast<std::uint32_t>(read));
    CloseHandle(read);CloseHandle(write);
    if(type!=FILE_TYPE_PIPE)return 7;
    SetLastError(0);
    if(formatter_lowio_file_type(0xffffffffu)!=FILE_TYPE_UNKNOWN || GetLastError()!=ERROR_INVALID_HANDLE) return 8;
    CRITICAL_SECTION lock;
    formatter_lowio_critical_initialize(&lock);
    formatter_lowio_critical_enter(&lock);formatter_lowio_critical_enter(&lock);
    Worker worker{&lock,CreateEventA(nullptr,TRUE,FALSE,nullptr),CreateEventA(nullptr,TRUE,FALSE,nullptr)};
    if(!worker.started || !worker.acquired)return 9;
    HANDLE thread=CreateThread(nullptr,0,enter_from_worker,&worker,0,nullptr);
    if(!thread || WaitForSingleObject(worker.started,5000)!=WAIT_OBJECT_0)return 10;
    if(WaitForSingleObject(worker.acquired,0)!=WAIT_TIMEOUT)return 11;
    formatter_lowio_critical_leave(&lock);
    if(WaitForSingleObject(worker.acquired,0)!=WAIT_TIMEOUT)return 12;
    formatter_lowio_critical_leave(&lock);
    if(WaitForSingleObject(worker.acquired,5000)!=WAIT_OBJECT_0 || WaitForSingleObject(thread,5000)!=WAIT_OBJECT_0)return 13;
    CloseHandle(thread);CloseHandle(worker.started);CloseHandle(worker.acquired);DeleteCriticalSection(&lock);
    std::puts("{\"fixture_passed\":true,\"startup_info_layout\":true,\"standard_handles\":3,\"pipe_type\":true,\"invalid_handle\":true,\"recursive_lock\":true,\"thread_contention\":true}");
    return 0;
}
