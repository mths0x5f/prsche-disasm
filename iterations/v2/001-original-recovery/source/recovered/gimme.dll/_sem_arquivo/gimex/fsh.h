// FSH Shape File module (GIMEX module 1, version 2.07, "F Barchard"): private structures.
//
// gimme.dll 3a43b0f6…, VA 100f9a60–1010b839.  The module is built from shape-library code that
// serves six shape formats; the FSH entry points pass shape type 2 (SHAPE_FSH).  The other type
// numbers are kept as numbers: which module each belongs to is not established here.
// The code splits in two translation units with their own static copies of the same helpers:
// the writer (100f9a60–10106e75, fshwrite.cpp + fshdxt.cpp) and the reader (10106e80–1010b839,
// fshread.cpp).

#ifndef FSH_H
#define FSH_H

#include "gimex.h"

#define SHAPE_FSH 2

// One directory entry with its blocks (0x44 bytes).  Each block starts with a type byte and a
// 3-byte little-endian offset to the next block of the same entry (0 for the last).
struct FSHSHAPE
{
    char name[4];                // +0x00 directory name
    unsigned char *bitmap;       // +0x04 bitmap block: 16-byte header and pixels
    int bitmapsize;              // +0x08
    char palettename[4];         // +0x0c writer: directory name of a separate palette entry
    unsigned char *palette;      // +0x10 palette block
    int palettesize;             // +0x14
    unsigned char *points;       // +0x18 0x7c block: count, then (x, y) pairs
    int pointssize;              // +0x1c
    unsigned char *comment;      // +0x20 0x6f block: text at +8
    int commentsize;             // +0x24
    unsigned char *records;      // +0x28 0x6e block: count, then 4-byte records
    int recordssize;             // +0x2c
    unsigned char *tpage;        // +0x30 0x6b block (12 bytes)
    int tpagesize;               // +0x34
    unsigned attributes;         // +0x38 becomes GINFO.attributes
    int compression;             // +0x3c becomes GINFO.compression
    int size;                    // +0x40 bytes of all blocks of the entry
};

static_assert(sizeof(FSHSHAPE) == 0x44, "FSHSHAPE layout");

// A count followed by the entries.
struct FSHTABLE
{
    int count;
    FSHSHAPE shape[1];
};

// Handle returned by open() and wopen() (0x18 bytes).
struct FSHHANDLE
{
    unsigned tag;                // +0x00 'SHPI'
    int size;                    // +0x04 sizeof(FSHHANDLE)
    int count;                   // +0x08 entries
    int current;                 // +0x0c writer: next entry index
    GSTREAM *stream;             // +0x10
    FSHTABLE *table;             // +0x14
};

static_assert(sizeof(FSHHANDLE) == 0x18, "FSHHANDLE layout");

// Block compressor used by the writer for GINFO.compression 3 (fshdxt.cpp, 100fc155).
int FSH_CompressBlocks(const GINFO *info, int rowbytes, const void *pixels, unsigned char *destination);

#endif
