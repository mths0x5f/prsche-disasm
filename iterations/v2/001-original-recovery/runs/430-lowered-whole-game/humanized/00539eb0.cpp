/* 00539eb0: If the pointer in its first dword is set, passes it to 0x0059f050. */
#define callee_0059f050 ((unsigned long (__cdecl *)(void *))0x0059f050)

struct Object_00539eb0 {
    void * block;
    unsigned long release_00539eb0();
};

unsigned long Object_00539eb0::release_00539eb0()
{
    if (block != 0)
        return callee_0059f050(block);
    return 0;
}
