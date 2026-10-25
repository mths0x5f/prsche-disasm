/* 00529050: Copies the handle a network member holds into *out; returns out. */
struct NetworkMember {
    unsigned long handle;
    unsigned long *copy_to(unsigned long *out) const;
};

unsigned long *NetworkMember::copy_to(unsigned long *out) const
{
    *out = handle;
    return out;
}
