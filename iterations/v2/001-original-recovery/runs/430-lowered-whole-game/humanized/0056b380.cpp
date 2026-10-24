/* 0056b380: checks a tap handle; on success gives its stream and tap. Returns 0 when valid. */
#include "humanized/stream.h"

long __cdecl stream_handle_0056b380(StreamTap *handle, Stream **stream, StreamTap **tap)
{
    Stream *owner;

    if (!handle)
        return 1;
    owner = handle->stream;
    if (owner->magic != STREAM_MAGIC)
        return 1;
    *tap = handle;
    *stream = owner;
    return 0;
}
