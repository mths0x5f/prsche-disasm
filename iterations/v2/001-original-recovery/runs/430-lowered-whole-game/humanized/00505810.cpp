/* 00505810: Makes an empty range (three null pointers); returns this. The argument is unused. */
struct ContextRange {
    void *first, *last, *end;
    ContextRange *make_empty(unsigned long unused);
};

ContextRange *ContextRange::make_empty(unsigned long)
{
    first = 0;
    last = 0;
    end = 0;
    return this;
}
