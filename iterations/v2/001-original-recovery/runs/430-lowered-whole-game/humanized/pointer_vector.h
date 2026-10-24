/* A vector of pointers kept as [first, last): the layout of the STL vector<T*> of the time. */
#ifndef HUMANIZED_POINTER_VECTOR_H
#define HUMANIZED_POINTER_VECTOR_H

struct PointerVector {
    void **first;
    void **last;

    long count() const;                      /* 004d6510 */
    void **at(unsigned long index) const;    /* 004d6520 */
    void pop_back();                         /* 004d6530 */
};

#endif
