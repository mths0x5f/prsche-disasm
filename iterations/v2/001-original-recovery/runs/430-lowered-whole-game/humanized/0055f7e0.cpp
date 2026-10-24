/* 0055f7e0: Win32 thread id of a game thread (file_current_thread_0055f780 compares it with
 * GetCurrentThreadId).
 * Original (cdecl): mov eax,[esp+4] / mov eax,[eax+10h] / ret */
#include "humanized/threads.h"

unsigned long __cdecl thread_id_0055f7e0(const ThreadRecord *record)
{
    return record->id;
}
