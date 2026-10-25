/* 0050e140: Assigns the first field from another record; returns this. */
struct NetworkValue {
    unsigned long value;
    NetworkValue *assign(const NetworkValue *other);
};

NetworkValue *NetworkValue::assign(const NetworkValue *other)
{
    value = other->value;
    return this;
}
