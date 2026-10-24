// libtiff platform layer over GSTREAM (gimme.dll 3a43b0f6…, 10139510–101397be, data 1043f2d8).
//
// libtiff 3.4 leaves the file I/O, memory and message hooks to a per-platform file (tif_unix.c,
// tif_win32.c, …).  EA wrote its own one in the shape of tif_unix.c: the client handle is a
// GSTREAM (thandle_t is HFILE, an int, under _WINDOWS), memory comes from galloc with the block
// size stored in front of it, there is no file mapping, and both message handlers are empty, so
// libtiff never prints.  The open entry point takes the already opened stream.  The file name
// and the open function's name are not attested ("TIFFOpen" is its message prefix);
// TIFFOpenGStream is a role name.

#include <stdio.h>
#include <string.h>

#include "gimex.h"
#include "tifgstream.h"

extern "C"
{
#include "tiff/tiffiop.h"
}

static_assert(sizeof(TIFF) == 0x1e0, "libtiff 3.4 TIFF layout (TIFFClientOpen allocates 0x1e0 + name)");

// 10139564.
static tsize_t TifReadProc(thandle_t fd, tdata_t buffer, tsize_t size)
{
    return gread((GSTREAM *)fd, buffer, size);
}

// 1013957a.
static tsize_t TifWriteProc(thandle_t fd, tdata_t buffer, tsize_t size)
{
    return gwrite((GSTREAM *)fd, buffer, size);
}

// 10139590.  The SEEK_CUR case falls through into SEEK_END and adds the length as well; libtiff's
// reader only seeks with SEEK_SET.  Returns the new position, or -1 when gseek fails.
static toff_t TifSeekProc(thandle_t fd, toff_t offset, int whence)
{
    GSTREAM *stream = (GSTREAM *)fd;
    switch (whence)
    {
    case SEEK_CUR:
        offset += gtell(stream);
        // falls through
    case SEEK_END:
        offset += glen(stream);
    }
    int ok = gseek(stream, offset);
    offset = gtell(stream);
    if (!ok)
        offset = (toff_t)-1;
    return offset;
}

// 101395fc.  The stream belongs to the GIMEX caller.
static int TifCloseProc(thandle_t)
{
    return 0;
}

// 10139603.
static toff_t TifSizeProc(thandle_t fd)
{
    return glen((GSTREAM *)fd);
}

// 10139611.  No mapping: libtiff falls back to reading.
static int TifMapProc(thandle_t, tdata_t *, toff_t *)
{
    return 0;
}

// 10139618.
static void TifUnmapProc(thandle_t, tdata_t, toff_t)
{
}

// 10139510.
extern "C" TIFF *TIFFFdOpen(int fd, const char *name, const char *mode)
{
    TIFF *tif = TIFFClientOpen(name, mode, (thandle_t)fd, TifReadProc, TifWriteProc, TifSeekProc, TifCloseProc,
                               TifSizeProc, TifMapProc, TifUnmapProc);
    if (tif)
        tif->tif_fd = fd;
    return tif;
}

// 1013961d.
TIFF *TIFFOpenGStream(const char *name, GSTREAM *stream, const char *mode)
{
    static const char module[] = "TIFFOpen";
    int m = _TIFFgetMode(mode, module);
    if (m == -1)
        return 0;
    if (stream == 0)
    {
        TIFFError(module, "%s: Cannot open", name);
        return 0;
    }
    return TIFFFdOpen((int)stream, name, mode);
}

// 10139677.  The size goes big-endian into 4 bytes in front of the block; no null check.
extern "C" tdata_t _TIFFmalloc(tsize_t size)
{
    unsigned char *block = (unsigned char *)galloc(size + 4);
    gputm(block, size, 4);
    return block + 4;
}

// 101396a6.
extern "C" void _TIFFfree(tdata_t p)
{
    gfree((unsigned char *)p - 4);
}

// 101396b7.  Always a new block: copies min(old size, new size) and frees the old one.
extern "C" tdata_t _TIFFrealloc(tdata_t p, tsize_t size)
{
    int oldsize = ggetm((unsigned char *)p - 4, 4);
    unsigned char *block = (unsigned char *)galloc(size + 4);
    gputm(block, size, 4);
    memcpy(block + 4, p, oldsize < size ? oldsize : size);
    gfree((unsigned char *)p - 4);
    return block + 4;
}

// 1013973c.
extern "C" void _TIFFmemset(tdata_t p, int v, tsize_t c)
{
    memset(p, v, c);
}

// 10139768.
extern "C" void _TIFFmemcpy(tdata_t d, const tdata_t s, tsize_t c)
{
    memcpy(d, s, c);
}

// 10139788.
extern "C" int _TIFFmemcmp(const tdata_t p1, const tdata_t p2, tsize_t c)
{
    return memcmp(p1, p2, c);
}

// 101397b9.
static void TifWarningHandler(const char *, const char *, va_list)
{
}

// 101397be.
static void TifErrorHandler(const char *, const char *, va_list)
{
}

// 1043f2d8, 1043f2dc.
extern "C" TIFFErrorHandler _TIFFwarningHandler = TifWarningHandler;
extern "C" TIFFErrorHandler _TIFFerrorHandler = TifErrorHandler;
