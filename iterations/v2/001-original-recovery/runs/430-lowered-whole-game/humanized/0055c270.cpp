/* 0055c270: When bit 0 of the flag at +dc of the record 0055c260 finds for a1 is set, forwards (record + 68, a2, a3) to 00560420; otherwise 0. */
#define find_0055c260 ((char *(__cdecl *)(unsigned long))0x0055c260)
#define forward_00560420 ((unsigned long (__cdecl *)(char *, unsigned long, unsigned long))0x00560420)

unsigned long __cdecl forward_if_flagged_0055c270(unsigned long unused, unsigned long a1, unsigned long a2, unsigned long a3)
{
    char *record = find_0055c260(a1);

    if (*(unsigned char *)(record + 0xdc) & 1)
        return forward_00560420(record + 0x68, a2, a3);
    return 0;
}
