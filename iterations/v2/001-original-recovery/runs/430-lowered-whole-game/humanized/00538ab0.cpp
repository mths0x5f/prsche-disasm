/* 00538ab0: Deleting destructor: sets the vtable, frees a global block and the object's block at +18, and the object when bit 0 of the flag is set. */
#define free_0059f050 ((void (__cdecl *)(void *))0x0059f050)
#define block_0069e0d4 (*(void **)0x0069e0d4)

struct Owner_00538ab0 {
    void *vtable_00;
    unsigned char unknown_04[0x14];
    void *block_18;
    Owner_00538ab0 *destroy_00538ab0(unsigned long flags);
};

Owner_00538ab0 *Owner_00538ab0::destroy_00538ab0(unsigned long flags)
{
    vtable_00 = (void *)0x005bb860;
    free_0059f050(block_0069e0d4);
    free_0059f050(block_18);
    if (flags & 1)
        free_0059f050(this);
    return this;
}
