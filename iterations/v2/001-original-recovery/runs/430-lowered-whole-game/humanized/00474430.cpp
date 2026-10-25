/* 00474430: Calls the member at 0x00474320 and returns this + 0x18. */
struct Object_00474430 {
    unsigned char unknown_00[0x18];
    unsigned long field_18;
    void call_00474320();
    void *run_00474430();
};

__declspec(naked) void Object_00474430::call_00474320()
{
    __asm mov eax, 0x00474320
    __asm jmp eax
}

void *Object_00474430::run_00474430()
{
    call_00474320();
    return &field_18;
}
