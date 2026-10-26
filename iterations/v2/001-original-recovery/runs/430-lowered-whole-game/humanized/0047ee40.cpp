/* 0047ee40: allocates an 8-byte zeroed record and publishes it in a global (0 when the allocation fails). */
struct Record_0047ee40 {
    unsigned long unknown_00;
    unsigned long unknown_04;
};

#define alloc_0059ef90 ((void *(__cdecl *)(unsigned long))0x0059ef90)
#define record_0628ba0 (*(Record_0047ee40 **)0x00628ba0)

void make_record_0047ee40(void)
{
    Record_0047ee40 *p = (Record_0047ee40 *)alloc_0059ef90(8);
    if (p != 0) {
        p->unknown_00 = 0;
        p->unknown_04 = 0;
        record_0628ba0 = p;
    } else {
        record_0628ba0 = 0;
    }
}
