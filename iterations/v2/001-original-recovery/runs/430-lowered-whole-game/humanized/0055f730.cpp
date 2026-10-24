/* 0055f730: Win32 handle of a game thread.
 * Original (cdecl): mov eax,[esp+4] / mov eax,[eax] / ret */
#include "humanized/threads.h"

void * __cdecl thread_handle_0055f730(const ThreadRecord *record)
{
    return record->handle;
}
