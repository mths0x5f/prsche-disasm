/* 005360e0: Drops a reference on a shared count; at zero frees the object's block (via 00554cc0) and the count. */
#define release_00554cc0 ((void (__cdecl *)(void *))0x00554cc0)
#define free_0059f050 ((void (__cdecl *)(void *))0x0059f050)

struct Shared_005360e0 {
    void *vtable_00;
    unsigned long unknown_04;
    void *block_08;
    unsigned char unknown_0c[0x14];
    long *refcount_20;
    void release_005360e0();
};

void Shared_005360e0::release_005360e0()
{
    long *count;

    vtable_00 = (void *)0x005bb6d4;
    count = refcount_20;
    *count = *count - 1;
    if (*refcount_20 == 0) {
        if (block_08 != 0)
            release_00554cc0(block_08);
        free_0059f050(refcount_20);
    }
}
