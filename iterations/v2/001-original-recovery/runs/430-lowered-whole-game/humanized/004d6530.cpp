/* 004d6530: drop the last element (no empty check).
 * Original (thiscall): add dword ptr [ecx+4],-4 / ret */
#include "humanized/pointer_vector.h"

void PointerVector::pop_back()
{
    --last;
}
