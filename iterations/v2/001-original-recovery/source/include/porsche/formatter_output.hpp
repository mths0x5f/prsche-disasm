#pragma once
#include "porsche/formatter_cleanup.hpp"
#include "porsche/formatter_locale.hpp"

namespace porsche {
extern std::uint32_t formatter_output_allocations_006afcf8;
std::int32_t* __cdecl formatter_output_map_error_005a662b(std::uint32_t);
std::int32_t __cdecl formatter_output_seek_inner_005a9b1d(std::uint32_t,std::uint32_t,std::uint32_t);
std::int32_t __cdecl formatter_output_write_inner_005a9eae(std::uint32_t,const void*,std::int32_t);
int __cdecl formatter_output_wide_inner_005abfb7(char*,std::uint32_t);
// Exact SetFilePointer import boundary; the high-distance pointer is null here.
std::uint32_t __stdcall formatter_output_set_file_pointer(std::uint32_t,std::int32_t,std::int32_t*,std::uint32_t);
}
