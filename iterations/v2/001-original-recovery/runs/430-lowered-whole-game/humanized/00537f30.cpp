/* 00537f30: returns a field of the structure its argument points to. */
struct Record_00537f30 {
    char pad_00[8];
    unsigned long value;
};

unsigned long __cdecl fn_00537f30(const Record_00537f30 *record)
{
    return record->value;
}
