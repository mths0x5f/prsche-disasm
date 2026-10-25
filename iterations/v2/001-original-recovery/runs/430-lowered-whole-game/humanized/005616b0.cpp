/* 005616b0: sum of the dwords at +0x24 and +0x20 of entry `index` of the pointer table at 0x6b7cc0. */
struct Entry_005616b0 {
    unsigned char unknown_00[0x20];
    unsigned long first;
    unsigned long second;
};

#define t_006b7cc0_005616b0 ((Entry_005616b0 **)0x006b7cc0)

unsigned long sum_005616b0(unsigned long index)
{
    Entry_005616b0 *e = t_006b7cc0_005616b0[index];
    return e->second + e->first;
}
