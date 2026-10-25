/* 00560180: Removes a value from the 8-slot network callback table (the first slot holding it). */
#define network_callbacks_006b7c20 ((unsigned long *)0x006b7c20)

void __cdecl network_callback_remove_00560180(unsigned long value)
{
    long i;

    for (i = 0; i < 8; ++i)
        if (network_callbacks_006b7c20[i] == value) {
            network_callbacks_006b7c20[i] = 0;
            return;
        }
}
