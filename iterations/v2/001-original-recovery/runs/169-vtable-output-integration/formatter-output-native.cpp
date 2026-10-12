#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cstdio>
#include "porsche/formatter_output.hpp"
int main() {
    using namespace porsche;
    char directory[MAX_PATH],path[MAX_PATH];
    if (!::GetTempPathA(MAX_PATH,directory) || !::GetTempFileNameA(directory,"nfs",0,path)) return 1;
    HANDLE file=::CreateFileA(path,GENERIC_READ|GENERIC_WRITE,0,nullptr,OPEN_EXISTING,FILE_ATTRIBUTE_TEMPORARY|FILE_FLAG_DELETE_ON_CLOSE,nullptr);
    if (file==INVALID_HANDLE_VALUE) { ::DeleteFileA(path);return 2; }
    const auto handle=reinterpret_cast<std::uint32_t>(file);DWORD written=0,read=0;char byte=0;
    bool passed=::WriteFile(file,"0123456789",10,&written,nullptr)!=0 && written==10;
    passed=passed && formatter_output_set_file_pointer(handle,3,nullptr,FILE_BEGIN)==3;
    passed=passed && ::ReadFile(file,&byte,1,&read,nullptr)!=0 && read==1 && byte=='3';
    passed=passed && formatter_output_set_file_pointer(handle,-2,nullptr,FILE_END)==8;
    std::int32_t high=0;::SetLastError(0);
    const auto low=formatter_output_set_file_pointer(handle,-1,&high,FILE_BEGIN);
    passed=passed && low==0xffffffffu && high==0 && ::GetLastError()==0;
    ::SetLastError(0);
    passed=passed && formatter_output_set_file_pointer(0xffffffffu,0,nullptr,FILE_BEGIN)==0xffffffffu && ::GetLastError()==ERROR_INVALID_HANDLE;
    if (!::CloseHandle(file)) passed=false;
    if (!passed) return 3;
    std::puts("{\"fixture_passed\":true,\"seek_read\":true,\"negative_distance\":true,\"sentinel_success_and_failure\":true,\"game_launch_verified\":false}");
}
