/* 0055ec30: clears the global at 0x6a57cc when it is not zero; returns the old value. */
#define g_006a57cc_0055ec30 (*(unsigned long *)0x006a57cc)

unsigned long clear_0055ec30()
{
    unsigned long old = g_006a57cc_0055ec30;
    if (old != 0)
        g_006a57cc_0055ec30 = 0;
    return old;
}
