#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#include "porsche/formatter_output.hpp"
namespace porsche {
// Porsche.exe ddd748fdbe6d Kernel32 SetFilePointer IAT005b223c.
static_assert(sizeof(LONG)==sizeof(std::int32_t));
std::uint32_t __stdcall formatter_output_set_file_pointer(std::uint32_t handle,std::int32_t distance,std::int32_t* high,std::uint32_t origin) {
    return ::SetFilePointer(reinterpret_cast<HANDLE>(handle),distance,reinterpret_cast<LONG*>(high),origin);
}
}
