/* 00474420: refreshes the object (00474320) and returns its member at +0x0c. */
struct Refreshable_00474420 {
    unsigned char unknown_00[0x0c];
    unsigned char member_0c[1];
    void refresh_00474320();
    void *refreshed_member();
};

/* the original 00474320 (thiscall) */
__declspec(naked) void Refreshable_00474420::refresh_00474320()
{
    __asm mov eax, 0x00474320
    __asm jmp eax
}

void *Refreshable_00474420::refreshed_member()
{
    refresh_00474320();
    return member_0c;
}
