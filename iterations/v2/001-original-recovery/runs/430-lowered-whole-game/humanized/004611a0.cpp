/* 004611a0: calls 00464f80 with the second word, the address of +8 and the first word of the record. */
struct Record_004611a0 {
    unsigned long first;
    unsigned long second;
    unsigned long data[1];
};
#define call_00464f80_from_004611a0 ((unsigned long (__cdecl *)(unsigned long, unsigned long *, unsigned long))0x00464f80)

unsigned long __cdecl call_with_record_004611a0(Record_004611a0 *record)
{
    return call_00464f80_from_004611a0(record->second, record->data, record->first);
}
