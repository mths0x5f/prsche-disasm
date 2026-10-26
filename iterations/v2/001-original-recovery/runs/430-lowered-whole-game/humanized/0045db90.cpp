/* 0045db90: marks the object once and runs the init routine of the global at 00627e1c. */
struct Target_0045db90 {
    unsigned long unknown_00;
    void start_00459a20();
};
#define target_00627e1c (*(Target_0045db90 **)0x00627e1c)

struct Object_0045db90 {
    unsigned char unknown_00[0x60];
    unsigned char started;
    void start_once();
};

__declspec(naked) void Target_0045db90::start_00459a20()
{
    __asm mov eax, 0x00459a20
    __asm jmp eax
}

void Object_0045db90::start_once()
{
    if (started == 0) {
        started = 1;
        target_00627e1c->start_00459a20();
    }
}
