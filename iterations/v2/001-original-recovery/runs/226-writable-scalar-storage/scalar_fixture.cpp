extern int DAT_005e25d0;
extern unsigned int DAT_005e25d4;
extern "C" __declspec(dllimport) __declspec(noreturn) void __stdcall ExitProcess(unsigned int);

static unsigned int raw_word(const void *p) {
    const unsigned char *b = static_cast<const unsigned char *>(p);
    return b[0] | (static_cast<unsigned int>(b[1]) << 8) |
        (static_cast<unsigned int>(b[2]) << 16) | (static_cast<unsigned int>(b[3]) << 24);
}
static void store_word(void *p, unsigned int value) {
    unsigned char *b = static_cast<unsigned char *>(p);
    for (unsigned int i = 0; i != 4; ++i) b[i] = static_cast<unsigned char>(value >> (i * 8));
}
extern "C" void __cdecl entry() {
    if (raw_word(&DAT_005e25d0) || raw_word(&DAT_005e25d4)) ExitProcess(1);
    if (reinterpret_cast<unsigned int>(&DAT_005e25d4) -
        reinterpret_cast<unsigned int>(&DAT_005e25d0) != 4) ExitProcess(2);
    const unsigned int patterns[5] = {0, 1, 0x7fffffffu, 0x80000000u, 0xffffffffu};
    for (unsigned int i = 0; i != 5; ++i) {
        store_word(&DAT_005e25d0, patterns[i]);
        store_word(&DAT_005e25d4, patterns[4 - i]);
        if (raw_word(&DAT_005e25d0) != patterns[i] ||
            raw_word(&DAT_005e25d4) != patterns[4 - i]) ExitProcess(3);
    }
    DAT_005e25d0 = 0;
    DAT_005e25d4 = 0;
    ExitProcess(0);
}
