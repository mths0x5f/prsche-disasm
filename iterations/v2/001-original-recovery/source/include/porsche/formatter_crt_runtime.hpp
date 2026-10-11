#pragma once
#include "porsche/formatter_lowio.hpp"

namespace porsche {
// Proven prefix through lock25; no claim about unobserved adjacent data extent.
extern void* formatter_crt_locks_005e57a8[26];
extern std::uint8_t formatter_crt_lock1_006afd00[24];
extern std::uint8_t formatter_crt_lock17_006afd18[24];
extern std::uint8_t formatter_crt_lock9_006afd30[24];
extern std::uint8_t formatter_crt_lock13_006afd48[24];
extern std::uint32_t formatter_crt_small_limit_005e606c;
extern std::uint32_t formatter_crt_new_mode_006afec8;
extern int (__cdecl* formatter_crt_new_handler_006afecc)(std::uint32_t);
extern std::uint32_t formatter_crt_heap_006c01d8;
extern std::uint32_t formatter_crt_header_count_006c01d0;
extern std::uint8_t* formatter_crt_headers_006c01d4;
extern std::uint32_t formatter_crt_tls_index_005e58b4;
// Opaque original table identity; its consumers and contents are not recovered here.
extern const std::uint8_t formatter_crt_signal_table_005e5ec8[];

void* __cdecl formatter_crt_nh_malloc_005a3bf7(std::uint32_t,std::uint32_t);
void* __cdecl formatter_crt_allocate_005a3c23(std::uint32_t);
void __cdecl formatter_crt_free_005a3b9d(void*);
int __cdecl formatter_crt_call_new_005ab4ab(std::uint32_t);
void __cdecl formatter_crt_initialize_locks_005a4b7b();
int __cdecl formatter_crt_initialize_tls_005a53f5();
void __cdecl formatter_crt_initialize_thread_005a5449(void*);
void* __cdecl formatter_crt_thread_005a545c();
void __cdecl formatter_crt_release_thread_005a54c3(void*);
void* __cdecl formatter_crt_calloc_005a8ea9(std::uint32_t,std::uint32_t);
std::uint8_t* __cdecl formatter_crt_find_header_005aa9aa(const void*);
void* __cdecl formatter_crt_memset_005abe90(void*,int,std::uint32_t);
#if defined(PORSCHE_CRT_MEMORY_TRACE)
void __cdecl formatter_crt_memset_store(const void*,std::uint32_t,std::uint32_t);
#endif

// Bounded unrecovered small-block internals and native OS boundaries.
void* __cdecl formatter_crt_small_allocate_005aad00(std::uint32_t);
void __cdecl formatter_crt_small_free_005aa9d5(std::uint8_t*,void*);
void* __stdcall formatter_crt_heap_allocate(std::uint32_t,std::uint32_t,std::uint32_t);
int __stdcall formatter_crt_heap_free(std::uint32_t,std::uint32_t,void*);
std::uint32_t __stdcall formatter_crt_tls_allocate();
void* __stdcall formatter_crt_tls_get(std::uint32_t);
int __stdcall formatter_crt_tls_set(std::uint32_t,void*);
std::uint32_t __stdcall formatter_crt_get_last_error();
void __stdcall formatter_crt_set_last_error(std::uint32_t);
std::uint32_t __stdcall formatter_crt_thread_id();
}
