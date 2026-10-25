/* 0052df10: If the pointer in its first dword is set, passes it to 0x0052f7d0. */
#define callee_0052f7d0 ((unsigned long (__cdecl *)(void *))0x0052f7d0)

struct Object_0052df10 {
    void * block;
    unsigned long release_0052df10();
};

unsigned long Object_0052df10::release_0052df10()
{
    if (block != 0)
        return callee_0052f7d0(block);
    return 0;
}
