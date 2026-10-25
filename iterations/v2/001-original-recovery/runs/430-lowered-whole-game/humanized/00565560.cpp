/* 00565560: Nonzero when the window is active and an input device is set (two globals). */
#define window_active_006b7c14 (*(long *)0x006b7c14)
#define input_device_006b7bf8 (*(long *)0x006b7bf8)

long __cdecl window_input_ready_00565560(void)
{
    if (!window_active_006b7c14)
        return 0;
    if (!input_device_006b7bf8)
        return 0;
    return 1;
}
