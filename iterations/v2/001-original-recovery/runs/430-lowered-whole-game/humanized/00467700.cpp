/* 00467700: Constructs a render core object: owner, parameter, empty name, its vtable. */
struct RenderCore {
    void *vtable;
    unsigned long owner;
    unsigned long unknown_08;
    unsigned long parameter;
    unsigned char unknown_10[0x100];
    char name[1];
    RenderCore *construct(unsigned long owner, unsigned long parameter);
};

#define render_core_vtable_005b3fbc ((void *)0x005b3fbc)

RenderCore *RenderCore::construct(unsigned long new_owner, unsigned long new_parameter)
{
    owner = new_owner;
    parameter = new_parameter;
    name[0] = 0;
    vtable = render_core_vtable_005b3fbc;
    return this;
}
