/* 005a506c: scalar deleting destructor: runs 005a510f, frees this when bit 0 of the flag is set; returns this. */
#define game_free_0059f050 ((void (__cdecl *)(void *))0x0059f050)

struct Object_005a506c {
    unsigned long unknown_00;
    void destroy_005a510f();
    Object_005a506c *delete_this(unsigned long flags);
};

__declspec(naked) void Object_005a506c::destroy_005a510f()
{
    __asm mov eax, 0x005a510f
    __asm jmp eax
}

Object_005a506c *Object_005a506c::delete_this(unsigned long flags)
{
    destroy_005a510f();
    if (flags & 1)
        game_free_0059f050(this);
    return this;
}
