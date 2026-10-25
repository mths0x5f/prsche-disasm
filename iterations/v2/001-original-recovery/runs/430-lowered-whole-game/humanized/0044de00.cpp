/* 0044de00: scalar deleting destructor shell: frees this when bit 0 of the flag is set; returns this. */
#define game_free_0059f050 ((void (__cdecl *)(void *))0x0059f050)

struct Object_0044de00 {
    unsigned long unknown_00;
    Object_0044de00 *destroy(unsigned long flags);
};

Object_0044de00 *Object_0044de00::destroy(unsigned long flags)
{
    if (flags & 1)
        game_free_0059f050(this);
    return this;
}
