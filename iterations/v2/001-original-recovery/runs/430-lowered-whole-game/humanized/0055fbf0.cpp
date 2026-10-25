/* 0055fbf0: calls 0055fb60(a, b, -1). */
#define callee_0055fb60_0055fbf0 ((unsigned long (__cdecl *)(unsigned long, unsigned long, unsigned long))0x0055fb60)

unsigned long forward_0055fbf0(unsigned long a, unsigned long b)
{
    return callee_0055fb60_0055fbf0(a, b, (unsigned long)-1);
}
