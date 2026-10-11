#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cstdio>
#include <thread>
#include "porsche/formatter_crt_runtime.hpp"
#include "porsche/formatter_text.hpp"

int main() {
    using namespace porsche;
    const auto heap = reinterpret_cast<std::uint32_t>(::HeapCreate(0,0,0));
    if (!heap) return 1;
    auto* bytes = static_cast<unsigned char*>(formatter_crt_heap_allocate(heap, HEAP_ZERO_MEMORY, 128));
    if (!bytes) return 2;
    for (unsigned i=0; i<128; ++i) if (bytes[i]) return 3;
    bytes[127] = 0x5a;
    if (!formatter_crt_heap_free(heap,0,bytes) || !::HeapDestroy(reinterpret_cast<HANDLE>(heap))) return 4;
    const auto slot = formatter_crt_tls_allocate();
    if (slot == TLS_OUT_OF_INDEXES) return 5;
    int main_value=31, child_value=47;
    if (!formatter_crt_tls_set(slot,&main_value) || formatter_crt_tls_get(slot)!=&main_value) return 6;
    const auto main_id=formatter_crt_thread_id();
    if (main_id!=::GetCurrentThreadId()) return 7;
    int child_result=0;
    std::thread child([&] {
        if (formatter_crt_tls_get(slot)!=nullptr) { child_result=1; return; }
        if (!formatter_crt_tls_set(slot,&child_value) || formatter_crt_tls_get(slot)!=&child_value) { child_result=2; return; }
        if (formatter_crt_thread_id()==main_id || formatter_crt_thread_id()!=::GetCurrentThreadId()) { child_result=3; return; }
        formatter_crt_set_last_error(0x12345678);
        if (formatter_crt_get_last_error()!=0x12345678) child_result=4;
    });
    child.join();
    if (child_result || formatter_crt_tls_get(slot)!=&main_value) return 8;
    if (!formatter_crt_tls_set(slot,nullptr) || formatter_crt_tls_get(slot)!=nullptr || !::TlsFree(slot)) return 9;
    formatter_crt_set_last_error(0xfedcba98);
    if (formatter_crt_get_last_error()!=0xfedcba98) return 10;
    alignas(4) std::int32_t counter=0x7fffffff;
    if (formatter_text_platform_increment(&counter)!=(-2147483647-1) || counter!=(-2147483647-1)) return 11;
    if (formatter_text_platform_decrement(&counter)!=2147483647 || counter!=2147483647) return 12;
    counter=0;
    auto increment=[&] { for (unsigned i=0; i<10000; ++i) formatter_text_platform_increment(&counter); };
    std::thread first(increment), second(increment);
    first.join(); second.join();
    if (counter!=20000) return 13;
    std::puts("{\"fixture_passed\":true,\"heap_zero_fill\":true,\"tls_thread_isolation\":true,\"last_error\":true,\"atomic_wrap_and_concurrency\":true,\"game_launch_verified\":false}");
}
