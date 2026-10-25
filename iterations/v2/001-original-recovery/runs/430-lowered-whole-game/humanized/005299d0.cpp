/* 005299d0: Copies a 16-byte deque iterator; returns this. */
struct DequeIterator16 {
    unsigned long field[4];
    DequeIterator16 *assign(const DequeIterator16 *other);
};

DequeIterator16 *DequeIterator16::assign(const DequeIterator16 *other)
{
    field[0] = other->field[0];
    field[1] = other->field[1];
    field[2] = other->field[2];
    field[3] = other->field[3];
    return this;
}
