/* 005a5449: Points a CRT stream record at the default buffer descriptor and sets its count to 1. */
struct CrtStreamRecord {
    unsigned char unknown_00[0x14];
    long count;
    unsigned char unknown_18[0x38];
    void *descriptor;
};

#define crt_default_descriptor_005e5ec8 ((void *)0x005e5ec8)

CrtStreamRecord * __cdecl crt_stream_default_005a5449(CrtStreamRecord *record)
{
    record->descriptor = crt_default_descriptor_005e5ec8;
    record->count = 1;
    return record;
}
