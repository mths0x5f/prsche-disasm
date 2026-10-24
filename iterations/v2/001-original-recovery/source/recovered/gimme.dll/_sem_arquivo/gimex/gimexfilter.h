// GIMEX filter and colour-quantizer descriptions (the records returned by about()).
//
// Recovered from gimme.dll SHA-256 3a43b0f6…; the original header is not available.  Layouts
// come from the 37 filter and 10 quantizer about() functions (tables 0x10432428, 0x10432720);
// field names describe the observed use.  Names marked "inferred" rest on the values only.

#ifndef GIMEXFILTER_H
#define GIMEXFILTER_H

#include "gimex.h"

// A filter parameter slot is 8 bytes.  Parameters of type 2 and 3 hold a double, the other
// types an int in the first word; FaceInRace passes only ints (GFILTERVALUE, gimex.h).
union GFILTERNUMBER
{
    int integer;
    double real;
};

// One parameter description (0x140 bytes).  Observed types: 0x1 int, 0x2 and 0x3 real,
// 0x201 list (help holds the comma-separated choices), 0x403, 0x801 and 0x1801 (colours).
struct GFILTERPARAMETER
{
    int type;                    // +0x00
    int unknown_04;              // +0x04 never written
    GFILTERNUMBER minimum;       // +0x08
    GFILTERNUMBER maximum;       // +0x10
    GFILTERNUMBER initial;       // +0x18 default value
    char name[32];               // +0x20
    char help[256];              // +0x40
};

#define GFILTER_MAX_VALUES 16

struct GFILTERABOUT
{
    unsigned tag;                // +0x00 (Size, Chroma, Smooth and Rotate leave it 0)
    int size;                    // +0x04 sizeof(GFILTERABOUT)
    int version;                 // +0x08 100, 104 or 105
    unsigned flags;              // +0x0c
    int minimages;               // +0x10 inferred: 1, Texture 0
    int maximages;               // +0x14 inferred: 1, Blend 2
    int unknown_18;              // +0x18 1 for Rect, Fill and Line
    int unknown_1c;              // +0x1c 0, 1 or 2
    char author[32];             // +0x20
    char filterversion[8];       // +0x40 "1.02"
    char name[16];               // +0x48 matched by GFILTER_find
    char description[32];        // +0x58
    int values;                  // +0x78 parameters in use
    int unknown_7c;              // +0x7c never written
    GFILTERPARAMETER value[GFILTER_MAX_VALUES]; // +0x80
};

static_assert(sizeof(GFILTERPARAMETER) == 0x140, "GFILTERPARAMETER layout");
static_assert(offsetof(GFILTERABOUT, name) == 0x48, "GFILTERABOUT layout");
static_assert(offsetof(GFILTERABOUT, value) == 0x80, "GFILTERABOUT layout");
static_assert(sizeof(GFILTERABOUT) == 0x1480, "GFILTERABOUT layout");

struct GQUANTABOUT
{
    unsigned tag;                // +0x00
    int size;                    // +0x04 sizeof(GQUANTABOUT)
    int version;                 // +0x08 150
    unsigned flags;              // +0x0c
    char author[32];             // +0x10
    char quantversion[8];        // +0x30 "1.04"
    char name[16];               // +0x38 matched by GQUANT_find
    char description[32];        // +0x48
};

static_assert(offsetof(GQUANTABOUT, name) == 0x38, "GQUANTABOUT layout");
static_assert(sizeof(GQUANTABOUT) == 0x68, "GQUANTABOUT layout");

// Filter handle created by open() (0x18 bytes).  Crop, Remap and Size each have their own,
// identical open(); the handle keeps the caller's image and parameter array by reference.
struct GFILTERHANDLE
{
    int unknown_00;              // +0x00 1
    int unknown_04;              // +0x04 0
    int images;                  // +0x08
    GIMAGE *image;               // +0x0c first input image
    int values;                  // +0x10
    GFILTERNUMBER *value;        // +0x14
};

static_assert(sizeof(GFILTERHANDLE) == 0x18, "GFILTERHANDLE layout");

// The Remap filter's single parameter points to this block (FaceInRace ReduceImage builds it).
struct GREMAP
{
    int first;                   // +0x00 palette index of palette[0]
    int colours;                 // +0x04 entries in palette
    GCOLOUR *palette;            // +0x08
    unsigned char *inverse;      // +0x0c optional 64^3 index table, (r >> 2 << 12) + (g >> 2 << 6) + (b >> 2)
};

// GINFO +0x458 counts (x, y) pairs from +0x87c, inside GINFO::unknown_458 (the field names
// belong to the shape-format recovery).  Crop and Size move them with the image.
inline int &GINFO_pointcount(GINFO *info)
{
    return *(int *)((unsigned char *)info + 0x458);
}

inline int *GINFO_point(GINFO *info, int point)
{
    return (int *)((unsigned char *)info + 0x87c) + 2 * point;
}

// Recovered filters and quantizers (entry points of the tables in gimextables.cpp).
GFILTERABOUT *CROP_about(void);
int CROP_open(void **handle, int images, GIMAGE *image, int values, void *value);
GINFO *CROP_info(void *handle, int frame);
int CROP_read(void *handle, GINFO *info, void *pixels, int rowbytes);
int CROP_close(void *handle);

GFILTERABOUT *REMAP_about(void);
int REMAP_open(void **handle, int images, GIMAGE *image, int values, void *value);
GINFO *REMAP_info(void *handle, int frame);
int REMAP_read(void *handle, GINFO *info, void *pixels, int rowbytes);
int REMAP_close(void *handle);

GFILTERABOUT *SIZE_about(void);
int SIZE_open(void **handle, int images, GIMAGE *image, int values, void *value);
GINFO *SIZE_info(void *handle, int frame);
int SIZE_read(void *handle, GINFO *info, void *pixels, int rowbytes);
int SIZE_close(void *handle);

GQUANTABOUT *WU_about(void);
void *WU_open(void);
int GCALL WU_add(void *handle, const GINFO *info, const void *pixels, int rowbytes);
GCOLOUR *GCALL WU_make(void *handle, int colours, int *exact);

#endif
