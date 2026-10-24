/* 0056c540: STREAM_get: takes the next chunk waiting at a tap, or 0 when none is.
 *
 * The byte count and the head are read without the stream lock (the classifier may be adding
 * a chunk at that moment); the lock only covers the count update. Afterwards the head moves to
 * the next chunk carrying this tap's mark, following the ring buffer's wrap chunks.
 */
#include "humanized/stream.h"

StreamChunk * __cdecl STREAM_get(StreamTap *handle)
{
    Stream *stream;
    StreamTap *tap;
    StreamChunk *chunk, *next;
    unsigned long size, mark;
    long remaining;

    if (stream_handle_0056b380(handle, &stream, &tap)) {
        real_error_file = STREAM_C_FILE;
        real_error_line = 0x7e5;
        real_error_handler(STREAM_MSG_BAD_HANDLE);
        return 0;
    }
    if (!tap->bytes)
        return 0;
    chunk = tap->head;
    size = chunk->size_tap & 0x00ffffff;
    chunk->size_tap = size;                              /* no longer waiting */

    heap_enter_005322b0(stream->lock);
    remaining = tap->bytes - (long)size;
    tap->bytes = remaining;
    heap_leave_005322c0(stream->lock);

    if (remaining > 0) {
        next = (StreamChunk *)((char *)chunk + size);
        mark = tap->id << 24;
        while ((next->size_tap & 0xff000000) != mark) {
            if (next->id == STREAM_CHUNK_WRAP)
                next = (StreamChunk *)stream->buffer;
            else
                next = (StreamChunk *)((char *)next + (next->size_tap & 0x00ffffff));
        }
        tap->head = next;
    }
    return chunk;
}
