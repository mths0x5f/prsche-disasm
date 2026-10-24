/* 0055d750: nonzero when the worker's addresses are plain text (mode 1).
 * Original (cdecl): mov ecx,[esp+4] / xor eax,eax / cmp dword ptr [ecx+0BCh],1 / sete al / ret */
#include "humanized/network_worker.h"

long __cdecl network_address_text_mode_0055d750(const NetworkWorker *worker)
{
    return worker->address_mode == 1;
}
