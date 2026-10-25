/* 005aa9aa: The CRT small-heap region (20-byte entries) holding an address, or 0. */
struct SmallHeapRegion {             /* 20 bytes */
    unsigned long unknown_00[3];
    char *base;
    unsigned long unknown_10;
};

#define small_heap_count_006c01d0 (*(const long *)0x006c01d0)
#define small_heap_regions_006c01d4 (*(SmallHeapRegion **)0x006c01d4)

SmallHeapRegion * __cdecl small_heap_find_005aa9aa(char *address)
{
    SmallHeapRegion *region = small_heap_regions_006c01d4;
    SmallHeapRegion *end = region + small_heap_count_006c01d0;

    for (; region < end; ++region)
        if ((unsigned long)(address - region->base) < 0x100000)
            return region;
    return 0;
}
