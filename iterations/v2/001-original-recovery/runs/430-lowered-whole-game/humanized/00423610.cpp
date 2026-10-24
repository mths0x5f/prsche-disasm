/* 00423610: returns the object itself (a member accessor shared, after the linker folded
 * identical bodies, by several classes).
 * Original (thiscall): mov eax,ecx / ret */
struct ContextObject {
    ContextObject *self();
};

ContextObject *ContextObject::self()
{
    return this;
}
