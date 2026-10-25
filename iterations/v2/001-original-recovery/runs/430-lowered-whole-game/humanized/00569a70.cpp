/* 00569a70: The first free slot among EA heaps 3..15, or 16 when all are used. */
#define ea_heaps_006b4f20 ((void **)0x006b4f20)

unsigned long __cdecl heap_first_free_00569a70(void)
{
    unsigned long index;

    for (index = 3; index < 16; ++index)
        if (!ea_heaps_006b4f20[index])
            break;
    return index;
}
