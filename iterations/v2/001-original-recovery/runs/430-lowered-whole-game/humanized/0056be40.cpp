/* 0056be40: classifies the chunks read so far into their taps. Returns 1 when the request's
 * final chunk has been classified, 0 otherwise (more data needed, request done, or an error).
 *
 * The tap's byte count is published before its head, under the stream lock, while STREAM_get
 * reads both without it: the order is kept from the original.
 */
#include "humanized/stream.h"

long __cdecl stream_classify_0056be40(Stream *stream)
{
    StreamRequest *request = stream->request;
    StreamChunk *chunk;
    CRITICAL_SECTION *lock;
    StreamTap *tap_entry;
    long size, tap, done, bytes, received;

    while ((long)(stream->fill - stream->parse) >= 8) {
        chunk = (StreamChunk *)stream->parse;
        size = (long)chunk->size_tap;
        if (size & 0xff000000) {
            const unsigned char *b = (const unsigned char *)chunk;
            real_error_file = STREAM_C_FILE;
            real_error_line = 0x192;
            real_error_handler(STREAM_MSG_BAD_CHUNK, b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7]);
            return 0;
        }
        if ((char *)chunk + size > stream->fill)
            return 0;                                    /* the chunk is not complete yet */

        tap = stream_filter_0056c000(stream, chunk);
        if (tap < 0) {
            if (tap == STREAM_ABORT_TAP) {
                real_error_file = STREAM_C_FILE;
                real_error_line = 0x19e;
                real_error_handler(STREAM_MSG_ABORT_TAP);
            }
            lock = stream->lock;
            heap_enter_005322b0(lock);
            done = request->state == STREAM_REQUEST_DONE;
            if (!done) {
                chunk->id = STREAM_CHUNK_SKIP;
                stream->parse += size;
            }
            heap_leave_005322c0(lock);
        } else {
            chunk->size_tap |= (unsigned long)tap << 24;
            heap_enter_005322b0(stream->lock);
            done = request->state == STREAM_REQUEST_DONE;
            if (!done) {
                tap_entry = &stream->taps[tap - 1];
                bytes = tap_entry->bytes + size;
                tap_entry->bytes = bytes;
                if (bytes == size)
                    tap_entry->head = chunk;             /* the tap was empty */
                stream->parse += size;
                received = stream->received;
                stream->received = received + size;
                if (received < stream->greedy_level && received + size >= stream->greedy_level)
                    stream->greedy_wait = 0;
            }
            heap_leave_005322c0(stream->lock);
        }
        if (done)
            return 0;
        if (chunk->id == request->last_id)
            return 1;
    }
    return 0;
}
