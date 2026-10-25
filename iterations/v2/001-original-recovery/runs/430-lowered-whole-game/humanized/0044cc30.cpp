/* 0044cc30: copies two dwords from the argument; returns the object. */
struct Pair_0044cc30 {
    unsigned long first;
    unsigned long second;
    Pair_0044cc30 *copy(Pair_0044cc30 *src);
};

Pair_0044cc30 *Pair_0044cc30::copy(Pair_0044cc30 *src)
{
    unsigned long a = src->first;
    first = a;
    second = src->second;
    return this;
}
