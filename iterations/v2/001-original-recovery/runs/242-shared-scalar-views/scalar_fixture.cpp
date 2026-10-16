extern "C" __declspec(dllimport) __declspec(noreturn) void __stdcall ExitProcess(unsigned int);
int read_signed242();
void write_signed242(int);
const void* address_signed242();
unsigned int read_unsigned242();
void write_unsigned242(unsigned int);
const void* address_unsigned242();

extern "C" void __cdecl entry() {
    if (read_signed242() != 0 || read_unsigned242() != 0) ExitProcess(1);
    if (address_signed242() != address_unsigned242()) ExitProcess(2);
    const int signed_patterns[6] = {0, 1, 2147483647, (-2147483647 - 1), -2147483647, -1};
    const unsigned int unsigned_patterns[6] = {0, 1, 0x7fffffffu, 0x80000000u, 0x80000001u, 0xffffffffu};
    for (unsigned int i = 0; i != 6; ++i) {
        write_signed242(signed_patterns[i]);
        if (read_signed242() != signed_patterns[i] || read_unsigned242() != unsigned_patterns[i]) ExitProcess(3);
        write_unsigned242(unsigned_patterns[5 - i]);
        if (read_signed242() != signed_patterns[5 - i] || read_unsigned242() != unsigned_patterns[5 - i]) ExitProcess(4);
        if (address_signed242() != address_unsigned242()) ExitProcess(5);
    }
    write_signed242(0);
    if (read_signed242() != 0 || read_unsigned242() != 0) ExitProcess(6);
    ExitProcess(0);
}
