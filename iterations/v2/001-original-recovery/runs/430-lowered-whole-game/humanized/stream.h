/* \real\cmn\stream.c: EA's chunk streaming (video and audio files read in the background).
 *
 * A stream reads a file into its ring buffer; the chunks it receives are classified by their id
 * into taps, and each consumer takes the chunks of its tap with STREAM_get. A chunk keeps its
 * tap in the top byte of its size word while it waits.
 */
#ifndef HUMANIZED_STREAM_H
#define HUMANIZED_STREAM_H

#include <windows.h>

#define STREAM_MAGIC        0x4d525453       /* 'STRM' */
#define STREAM_ABORT_TAP    (-2)             /* filter result for chunks of an aborted request */
#define STREAM_CHUNK_WRAP   0xffffffffu      /* id: continue at the start of the buffer */
#define STREAM_CHUNK_SKIP   0xfffffffeu      /* id: chunk discarded by the classifier */
#define STREAM_REQUEST_DONE 4                /* request state: finished or aborted */

struct StreamChunk {
    unsigned long id;
    unsigned long size_tap;                 /* size in the low 24 bits, waiting tap in the top 8 */
};

struct StreamFilter {                        /* 12 bytes */
    unsigned long mask;
    unsigned long value;                     /* (id & mask) == value selects the filter */
    long tap;                                /* 1-based tap, or a negative code */
};

struct Stream;

struct StreamTap {                           /* 16 bytes; a STREAM_get handle points at one */
    Stream *stream;
    unsigned long id;                        /* the mark chunks of this tap carry */
    long bytes;                              /* bytes of chunks waiting */
    StreamChunk *head;                       /* first waiting chunk */
};

struct StreamRequest {
    unsigned char unknown_000[4];
    long state;                              /* STREAM_REQUEST_DONE when finished */
    unsigned char unknown_008[0x118];
    unsigned long last_id;                   /* id of the request's final chunk */
};

struct Stream {
    unsigned long magic;                     /* STREAM_MAGIC */
    CRITICAL_SECTION *lock;
    unsigned char unknown_08[8];
    StreamFilter *filters;
    long filter_count;
    StreamTap *taps;
    unsigned char unknown_1c[4];
    char *buffer;                            /* ring buffer start (STREAM_CHUNK_WRAP goes here) */
    unsigned char unknown_24[0x10];
    long greedy_level;
    long greedy_wait;
    long received;
    unsigned char unknown_40[4];
    char *parse;                             /* next chunk to classify */
    char *fill;                              /* end of the data read so far */
    unsigned char unknown_4c[4];
    StreamRequest *request;
};

/* Humanized functions of stream.c. */
long __cdecl stream_handle_0056b380(StreamTap *handle, Stream **stream, StreamTap **tap);
long __cdecl stream_filter_0056c000(Stream *stream, const StreamChunk *chunk);
long __cdecl stream_classify_0056be40(Stream *stream);
StreamChunk * __cdecl STREAM_get(StreamTap *handle);

/* Game functions and data used here, at their original addresses (still lowered code). */
#define heap_enter_005322b0     ((void (__cdecl *)(CRITICAL_SECTION *))0x005322b0)
#define heap_leave_005322c0     ((void (__cdecl *)(CRITICAL_SECTION *))0x005322c0)
/* The real library's error report: source file and line in two globals, then the handler. */
#define real_error_file         (*(const char **)0x005deb74)
#define real_error_line         (*(long *)0x005deb78)
#define real_error_handler      (*(void (__cdecl **)(const char *, ...))0x005debf0)
/* Strings of the original .rdata: the handler keeps these pointers. */
#define STREAM_C_FILE           ((const char *)0x005bd978)   /* "\real\cmn\stream.c" */
#define STREAM_MSG_ABORT_TAP    ((const char *)0x005bdcdc)   /* "STREAM - chunk received at abort tap\n" */
#define STREAM_MSG_BAD_CHUNK    ((const char *)0x005bdc98)   /* "STREAM - invalid chunk (%02x ...)\n" */
#define STREAM_MSG_BAD_HANDLE   ((const char *)0x005bdd88)   /* "STREAM_get - invalid stream handle\n" */

#endif
