#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include "porsche/formatter_bootstrap.hpp"
#include "porsche/formatter_strings.hpp"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <initializer_list>

// Private terminal boundary: this fixture never calls a fatal path.
namespace porsche {
[[noreturn]] void __cdecl formatter_fatal_005a2e22(int) { std::abort(); }
}
int main() {
    using namespace porsche;
    char native_name[32768]{}, reference[32768]{};
    const auto length=formatter_error_module_name(nullptr,native_name,sizeof native_name);
    if(!length || length!=GetModuleFileNameA(nullptr,reference,sizeof reference) ||
       std::strcmp(native_name,reference)) return 1;
    char shortened[8]{};
    if(formatter_error_module_name(nullptr,shortened,sizeof shortened)!=sizeof shortened ||
       std::memcmp(shortened,native_name,7)) return 2;
    for(const int selector : {-10,-11,-12})
        if(formatter_error_std_handle(selector)!=GetStdHandle(static_cast<DWORD>(selector))) return 3;
    void* library=formatter_dialog_load_library("user32.dll");
    if(!library) return 4;
    for(const char* name : {"MessageBoxA","GetActiveWindow","GetLastActivePopup"})
        if(formatter_dialog_get_proc_address(library,name)!=
           reinterpret_cast<void*>(GetProcAddress(static_cast<HMODULE>(library),name))) return 5;
    if(formatter_dialog_get_proc_address(library,"Porsche153MissingSymbol")!=nullptr) return 6;
    if(!FreeLibrary(static_cast<HMODULE>(library))) return 7;
    // The OS deletes this uniquely-created file when its handle is closed.
    char temporary[MAX_PATH]{},file[MAX_PATH]{};
    if(!GetTempPathA(MAX_PATH,temporary) || !GetTempFileNameA(temporary,"p53",0,file)) return 8;
    HANDLE handle=CreateFileA(file,GENERIC_READ|GENERIC_WRITE,0,nullptr,OPEN_EXISTING,
        FILE_ATTRIBUTE_TEMPORARY|FILE_FLAG_DELETE_ON_CLOSE,nullptr);
    if(handle==INVALID_HANDLE_VALUE){DeleteFileA(file);return 9;}
    const unsigned char data[]={0,0x80,0xff,'P','5','3','\n'};
    std::uint32_t written=0;
    bool ok=formatter_error_write_file(handle,data,sizeof data,&written,nullptr)!=0 && written==sizeof data;
    ok=ok && SetFilePointer(handle,0,nullptr,FILE_BEGIN)!=INVALID_SET_FILE_POINTER;
    unsigned char readback[sizeof data]{};DWORD read=0;
    ok=ok && ReadFile(handle,readback,sizeof readback,&read,nullptr)!=0 && read==sizeof data &&
        std::memcmp(readback,data,sizeof data)==0;
    CloseHandle(handle);
    if(!ok)return 10;
    written=0xccccccccu;
    if(formatter_error_write_file(INVALID_HANDLE_VALUE,data,sizeof data,&written,nullptr)!=0 ||
       written!=0 || GetLastError()!=ERROR_INVALID_HANDLE)return 11;
    std::puts("{\"fixture_passed\":true,\"module_name\":true,\"truncation\":true,\"standard_handles\":3,\"resolved_user32_symbols\":3,\"file_bytes\":7,\"invalid_handle\":true,\"dialog_invoked\":false}");
    return 0;
}
