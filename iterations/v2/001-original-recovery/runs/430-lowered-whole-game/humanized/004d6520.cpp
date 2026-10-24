/* 004d6520: address of element `index` (no bounds check).
 * Original (thiscall): mov eax,[ecx] / mov ecx,[esp+4] / lea eax,[eax+ecx*4] / ret 4 */
#include "humanized/pointer_vector.h"

void **PointerVector::at(unsigned long index) const
{
    return first + index;
}
