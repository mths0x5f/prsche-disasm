/* 0055ea00: calls 005846b0 with the dword at +0x3c of its argument. */
#define callee_005846b0_0055ea00 ((unsigned long (__cdecl *)(unsigned long))0x005846b0)
struct Holder_0055ea00 {
    unsigned char unknown_00[60];
    unsigned long value;
};

unsigned long call_0055ea00(Holder_0055ea00 *p)
{
    return callee_005846b0_0055ea00(p->value);
}
