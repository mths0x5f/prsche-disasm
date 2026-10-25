/* 0053d780: calls 005740a0(0, 0, global 005de624, global 005de628). */
#define size_a_005de624 (*(unsigned long *)0x005de624)
#define size_b_005de628 (*(unsigned long *)0x005de628)
#define call_005740a0_from_0053d780 ((unsigned long (__cdecl *)(unsigned long, unsigned long, unsigned long, unsigned long))0x005740a0)

unsigned long __cdecl call_with_sizes_0053d780(void)
{
    return call_005740a0_from_0053d780(0, 0, size_a_005de624, size_b_005de628);
}
