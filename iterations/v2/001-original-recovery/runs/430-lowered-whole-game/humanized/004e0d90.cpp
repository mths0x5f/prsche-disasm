/* 004e0d90: the larger of the object's limit and (when the flag is set) the global manager's value. */
#define manager_004e0d90 (*(void **)0x0065b928)

struct Manager_004e0d90 {
    long value_004d6300();
};
__declspec(naked) long Manager_004e0d90::value_004d6300()
{
    __asm mov eax, 0x004d6300
    __asm jmp eax
}

struct Limited_004e0d90 {
    unsigned char unknown_000[0x130];
    long limit;
    long max_004e0d90(unsigned char use_manager);
};

long Limited_004e0d90::max_004e0d90(unsigned char use_manager)
{
    if (use_manager) {
        long v;
        if (manager_004e0d90 == 0)
            v = 0;
        else
            v = ((Manager_004e0d90 *)manager_004e0d90)->value_004d6300();
        if (v > limit)
            return v;
    }
    return limit;
}
