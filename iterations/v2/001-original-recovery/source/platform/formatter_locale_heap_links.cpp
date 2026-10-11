#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#include "porsche/formatter_locale.hpp"
#include "porsche/formatter_small_heap.hpp"

namespace porsche {
// Original Porsche.exe ddd748fdbe6d Kernel32 IAT identities, Run161/162.
static_assert(sizeof(wchar_t)==sizeof(std::uint16_t));
static_assert(sizeof(CPINFO)==sizeof(FormatterLocaleCPInfo));
static_assert(offsetof(CPINFO,LeadByte)==offsetof(FormatterLocaleCPInfo,lead_ranges));
static_assert(offsetof(CPINFO,DefaultChar)==offsetof(FormatterLocaleCPInfo,default_character));
void* __stdcall formatter_small_heap_reallocate(std::uint32_t heap,std::uint32_t flags,void* p,std::uint32_t bytes) {
    return ::HeapReAlloc(reinterpret_cast<HANDLE>(heap),flags,p,bytes); // 005b2104
}
std::uint32_t __stdcall formatter_small_heap_size(std::uint32_t heap,std::uint32_t flags,const void* p) {
    return static_cast<std::uint32_t>(::HeapSize(reinterpret_cast<HANDLE>(heap),flags,p)); // 005b2100
}
std::uint32_t __stdcall formatter_small_heap_create(std::uint32_t flags,std::uint32_t initial,std::uint32_t maximum) {
    return reinterpret_cast<std::uint32_t>(::HeapCreate(flags,initial,maximum)); // 005b20d8
}
int __stdcall formatter_small_heap_destroy(std::uint32_t heap) {
    return ::HeapDestroy(reinterpret_cast<HANDLE>(heap)); // 005b20dc
}
void* __stdcall formatter_small_virtual_allocate(void* p,std::uint32_t bytes,std::uint32_t kind,std::uint32_t protection) {
    return ::VirtualAlloc(p,bytes,kind,protection); // 005b2144
}
int __stdcall formatter_small_virtual_free(void* p,std::uint32_t bytes,std::uint32_t kind) {
    return ::VirtualFree(p,bytes,kind); // 005b2148
}
int __stdcall formatter_locale_map_w(std::uint32_t locale,std::uint32_t flags,const std::uint16_t* input,int count,void* output,int capacity) {
    return ::LCMapStringW(locale,flags,reinterpret_cast<LPCWSTR>(input),count,static_cast<LPWSTR>(output),capacity); // 005b2108
}
int __stdcall formatter_locale_map_a(std::uint32_t locale,std::uint32_t flags,const char* input,int count,char* output,int capacity) {
    return ::LCMapStringA(locale,flags,input,count,output,capacity); // 005b210c
}
int __stdcall formatter_locale_to_wide(std::uint32_t codepage,std::uint32_t flags,const char* input,int count,std::uint16_t* output,int capacity) {
    return ::MultiByteToWideChar(codepage,flags,input,count,reinterpret_cast<LPWSTR>(output),capacity); // 005b2178
}
int __stdcall formatter_locale_from_wide(std::uint32_t codepage,std::uint32_t flags,const std::uint16_t* input,int count,char* output,int capacity,const char* fallback,int* used) {
    return ::WideCharToMultiByte(codepage,flags,reinterpret_cast<LPCWSTR>(input),count,output,capacity,fallback,used); // 005b2110
}
int __stdcall formatter_locale_type_w(std::uint32_t kind,const std::uint16_t* input,int count,std::uint16_t* output) {
    return ::GetStringTypeW(kind,reinterpret_cast<LPCWSTR>(input),count,output); // 005b20d0
}
int __stdcall formatter_locale_type_a(std::uint32_t locale,std::uint32_t kind,const char* input,int count,std::uint16_t* output) {
    return ::GetStringTypeA(locale,kind,input,count,output); // 005b20d4
}
std::uint32_t __stdcall formatter_locale_oem_codepage() { return ::GetOEMCP(); } // 005b2114
std::uint32_t __stdcall formatter_locale_ansi_codepage() { return ::GetACP(); } // 005b2118
int __stdcall formatter_locale_codepage_info(std::uint32_t cp,FormatterLocaleCPInfo* info) {
    return ::GetCPInfo(cp,reinterpret_cast<CPINFO*>(info)); // 005b211c
}
}
