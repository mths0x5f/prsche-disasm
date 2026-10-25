/* 0055ed20: Sets or clears bit 0 of one diagnostic device's flags (12-byte entries). */
struct DiagnosticDevice {
    unsigned long flags;
    unsigned long unknown_04[2];
};

#define diagnostic_devices_005e1c90 ((DiagnosticDevice *)0x005e1c90)

void __cdecl diagnostic_device_enable_0055ed20(unsigned long device, long enable)
{
    unsigned long flags = diagnostic_devices_005e1c90[device].flags;

    diagnostic_devices_005e1c90[device].flags = (flags & ~1u) | (enable != 0);
}
