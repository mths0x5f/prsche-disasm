/* 0055d730: nonzero when a provider resolves the worker's addresses (mode above 3).
 * Original (cdecl): mov ecx,[esp+4] / mov eax,3 / cmp eax,[ecx+0BCh] / sbb eax,eax / neg eax / ret */
#include "humanized/network_worker.h"

long __cdecl network_address_provider_mode_0055d730(const NetworkWorker *worker)
{
    return worker->address_mode > 3;
}
