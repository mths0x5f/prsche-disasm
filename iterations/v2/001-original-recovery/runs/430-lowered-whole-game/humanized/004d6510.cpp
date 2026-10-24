/* 004d6510: number of elements of a PointerVector.
 * Original (thiscall): mov eax,[ecx+4] / mov edx,[ecx] / sub eax,edx / sar eax,2 / ret */
#include "humanized/pointer_vector.h"

long PointerVector::count() const
{
    return (long)((char *)last - (char *)first) >> 2;
}
