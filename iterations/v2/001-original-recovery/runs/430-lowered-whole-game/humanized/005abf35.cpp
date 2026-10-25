/* 005abf35: Whether a CRT file handle is open as a device (FDEV, 40h in its osfile byte). */
struct CrtHandleInfo {               /* 36 bytes */
    long os_handle;
    unsigned char osfile;
    unsigned char unknown_05[31];
};

#define crt_handle_count_006c02e0 (*(const unsigned long *)0x006c02e0)
#define crt_handle_blocks_006c01e0 ((CrtHandleInfo **)0x006c01e0)

long __cdecl crt_handle_is_device_005abf35(unsigned long handle)
{
    if (handle >= crt_handle_count_006c02e0)
        return 0;
    return crt_handle_blocks_006c01e0[(long)handle >> 5][handle & 31].osfile & 0x40;
}
