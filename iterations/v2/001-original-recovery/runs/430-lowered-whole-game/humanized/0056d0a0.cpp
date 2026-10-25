/* 0056d0a0: Reads a packed entry from the 64-slot table at 0x006b61a0 chosen by the top 6 bits of 0x006b4f60, notifies 0056d040 with its low byte and returns its signed value >> 22. */
#define selector_006b4f60 (*(unsigned long *)0x006b4f60)
#define entries_006b61a0 ((long *)0x006b61a0)
#define notify_0056d040 ((void (__cdecl *)(unsigned long))0x0056d040)

long __cdecl read_entry_0056d0a0(void)
{
    long entry = entries_006b61a0[selector_006b4f60 >> 26];

    notify_0056d040(entry & 0xff);
    return entry >> 22;
}
