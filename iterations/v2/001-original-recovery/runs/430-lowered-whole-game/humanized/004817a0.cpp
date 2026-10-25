/* 004817a0: Looks up the 56-byte record for a slot through a signed-byte index table; NULL when the entry is negative. */
struct RecordTable_004817a0 {
    unsigned char unknown_00[0x14];
    signed char *indices;
    unsigned char unknown_18[4];
    unsigned char **records;
    unsigned char *record_004817a0(long slot);
};

unsigned char *RecordTable_004817a0::record_004817a0(long slot)
{
    long index = indices[slot];

    if (index < 0)
        return 0;
    return *records + index * 56;
}
