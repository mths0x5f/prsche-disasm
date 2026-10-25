/* 004c3150: Copies the value the object's first pointer points at into *out; returns out. */
struct NetworkHolder {
    unsigned long *value;
    unsigned long *copy_to(unsigned long *out) const;
};

unsigned long *NetworkHolder::copy_to(unsigned long *out) const
{
    *out = *value;
    return out;
}
