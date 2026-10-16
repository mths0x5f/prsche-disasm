extern float _DAT_005b242c;
extern float _DAT_005b24a8;
extern "C" __declspec(dllimport) __declspec(noreturn) void __stdcall ExitProcess(unsigned int);

extern "C" void __cdecl entry() {
    const unsigned char *a = reinterpret_cast<const unsigned char *>(&_DAT_005b242c);
    const unsigned char *b = reinterpret_cast<const unsigned char *>(&_DAT_005b24a8);
    const unsigned char expected_a[4] = {0, 0, 0xc8, 0x42};
    const unsigned char expected_b[4] = {0, 0, 0x80, 0x3f};
    if ((reinterpret_cast<unsigned int>(a) & 3) ||
        (reinterpret_cast<unsigned int>(b) & 3) || a == b) ExitProcess(1);
    for (unsigned int i = 0; i != 4; ++i) {
        if (a[i] != expected_a[i] || b[i] != expected_b[i]) ExitProcess(2);
    }
    ExitProcess(0);
}
