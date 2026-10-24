// GSTREAM data source for the IJG library (gimme.dll 3a43b0f6…, 10156980–10156b4e).
//
// The code is IJG 6a jdatasrc.c with the stdio file replaced by a GSTREAM: JFREAD(infile, buffer,
// INPUT_BUF_SIZE) became gread(stream, buffer, 0x1000), everything else (error codes
// JERR_INPUT_EMPTY 0x29 and JWRN_JPEG_EOF 0x74, the fake EOI, the skip loop, the 0x28-byte
// manager, jpeg_resync_to_restart) is unchanged.  It sits in the binary between jdapimin.c and
// jdapistd.c, with the setup function first, so it was a separate object.  Its file and function
// names are not attested; jpeg_gstream_src is a role name.

#include <stdio.h>
#include <string.h>

#include "jpgsource.h"

// The manager: the public part, then jdatasrc.c's own fields (0x28 bytes).
struct GSTREAMSOURCE
{
    jpeg_source_mgr pub;         // +0x00
    GSTREAM *stream;             // +0x1c jdatasrc.c: infile
    JOCTET *buffer;              // +0x20
    boolean startoffile;         // +0x24
};

static_assert(sizeof(GSTREAMSOURCE) == 0x28, "GSTREAMSOURCE layout");

#define GSTREAM_INPUT_SIZE 4096  // jdatasrc.c INPUT_BUF_SIZE

// 10156a26.
static void JpgInitSource(j_decompress_ptr cinfo)
{
    GSTREAMSOURCE *source = (GSTREAMSOURCE *)cinfo->src;
    source->startoffile = TRUE;
}

// 10156a41.  An empty file is fatal; a truncated one gets a warning and a fake EOI marker.
static boolean JpgFillInputBuffer(j_decompress_ptr cinfo)
{
    GSTREAMSOURCE *source = (GSTREAMSOURCE *)cinfo->src;
    size_t count = gread(source->stream, source->buffer, GSTREAM_INPUT_SIZE);
    if (count <= 0)
    {
        if (source->startoffile)
            ERREXIT(cinfo, JERR_INPUT_EMPTY);
        WARNMS(cinfo, JWRN_JPEG_EOF);
        source->buffer[0] = (JOCTET)0xff;
        source->buffer[1] = (JOCTET)JPEG_EOI;
        count = 2;
    }
    source->pub.next_input_byte = source->buffer;
    source->pub.bytes_in_buffer = count;
    source->startoffile = FALSE;
    return TRUE;
}

// 10156af2.
static void JpgSkipInputData(j_decompress_ptr cinfo, long count)
{
    GSTREAMSOURCE *source = (GSTREAMSOURCE *)cinfo->src;
    if (count > 0)
    {
        while (count > (long)source->pub.bytes_in_buffer)
        {
            count -= (long)source->pub.bytes_in_buffer;
            JpgFillInputBuffer(cinfo);
        }
        source->pub.next_input_byte += (size_t)count;
        source->pub.bytes_in_buffer -= (size_t)count;
    }
}

// 10156b4a.
static void JpgTermSource(j_decompress_ptr)
{
}

// 10156980.  Allocates the manager and its buffer once per decompressor (permanent pool).
void jpeg_gstream_src(j_decompress_ptr cinfo, GSTREAM *stream)
{
    GSTREAMSOURCE *source;
    if (cinfo->src == NULL)
    {
        cinfo->src = (jpeg_source_mgr *)(*cinfo->mem->alloc_small)((j_common_ptr)cinfo, JPOOL_PERMANENT,
                                                                   sizeof(GSTREAMSOURCE));
        source = (GSTREAMSOURCE *)cinfo->src;
        source->buffer = (JOCTET *)(*cinfo->mem->alloc_small)((j_common_ptr)cinfo, JPOOL_PERMANENT,
                                                              GSTREAM_INPUT_SIZE * sizeof(JOCTET));
    }
    source = (GSTREAMSOURCE *)cinfo->src;
    source->pub.init_source = JpgInitSource;
    source->pub.fill_input_buffer = JpgFillInputBuffer;
    source->pub.skip_input_data = JpgSkipInputData;
    source->pub.resync_to_restart = jpeg_resync_to_restart;
    source->pub.term_source = JpgTermSource;
    source->stream = stream;
    source->pub.bytes_in_buffer = 0;
    source->pub.next_input_byte = NULL;
}
