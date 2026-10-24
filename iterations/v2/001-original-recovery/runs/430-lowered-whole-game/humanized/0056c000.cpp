/* 0056c000: the tap a chunk goes to: the first filter whose masked id matches; otherwise the
 * abort tap. */
#include "humanized/stream.h"

long __cdecl stream_filter_0056c000(Stream *stream, const StreamChunk *chunk)
{
    unsigned long id = chunk->id;
    StreamFilter *filter = stream->filters;
    long i;

    for (i = 0; i < stream->filter_count; ++i, ++filter)
        if ((id & filter->mask) == filter->value)
            return filter->tap;
    return STREAM_ABORT_TAP;
}
