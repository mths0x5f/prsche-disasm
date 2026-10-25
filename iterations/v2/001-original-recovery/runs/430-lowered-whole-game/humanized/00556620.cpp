/* 00556620: The suffix size of one of the 16 EA heaps (selected by the low bits of flags). */
struct EaHeap {
    unsigned char unknown_00[0x30];
    long suffix;
};

#define ea_heaps_006b4f20 ((EaHeap **)0x006b4f20)

long __cdecl heap_suffix_00556620(unsigned long flags)
{
    return ea_heaps_006b4f20[flags & 15]->suffix;
}
