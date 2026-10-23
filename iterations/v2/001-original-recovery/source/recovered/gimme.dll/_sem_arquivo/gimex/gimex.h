// GIMEX image import/export library: structures and entry points as used by gimme.dll.
//
// Recovered from gimme.dll SHA-256 3a43b0f6…; the original header is not available.  The
// library name comes from the module names in the binary ("Nil Gimex", "Gimex Images",
// "ClipBoard Gimex").  Field names describe the observed use; offsets are checked below.
// Function names without an EA diagnostic string are role names, see functions.json.

#ifndef GIMEX_H
#define GIMEX_H

#include <stddef.h>

#define GCALL __stdcall

// Four-character tags are MSVC multi-character constants ('SHPI' == 0x53485049).
#define GTAG(a, b, c, d) (((unsigned)(a) << 24) | ((unsigned)(b) << 16) | ((unsigned)(c) << 8) | (unsigned)(d))

// ---------------------------------------------------------------------------------------------
// Image descriptor.  Every module's info() allocates one and writes its tag and own size; the
// size doubles as the structure version.  Two generations are linked into gimme.dll:
//   GINFO_SIZE_LEGACY  0x2890  FaceInRace and 63 modules
//   GINFO_SIZE_SHAPE   0x2aa4  the six shape modules (FSH, PSH, VSH, NSH, DSH, SSH, version 2.07)
// The shape writer touches the extension only when size == GINFO_SIZE_SHAPE.

#define GINFO_SIZE_LEGACY 0x2890
#define GINFO_SIZE_SHAPE 0x2aa4
#define GINFO_VERSION 300

struct GCOLOUR
{
    unsigned char b, g, r, a;
};

struct GSHAPERECORD
{
    int a;
    int b;
    unsigned c;
    unsigned d;
};

struct GINFO
{
    unsigned tag;                // +0x000 format tag ('SHPI', '.BMP', …)
    int size;                    // +0x004 sizeof this descriptor (version test)
    int version;                 // +0x008 GINFO_VERSION
    int frames;                  // +0x00c
    int width;                   // +0x010
    int height;                  // +0x014
    int bpp;                     // +0x018 storage bits per pixel (8 or 32 in FaceInRace)
    int depth;                   // +0x01c significant bits per pixel
    int unknown_020;             // +0x020
    int numcolours;              // +0x024 palette entries in use
    GCOLOUR colour[256];         // +0x028
    unsigned attributes;         // +0x428 per-format section flags (FSH writer gates on bits)
    int unknown_42c[3];          // +0x42c
    int alphabits;               // +0x438
    int redbits;                 // +0x43c
    int greenbits;               // +0x440
    int bluebits;                // +0x444
    int centrex;                 // +0x448 cleared by ConvertFile
    int centrey;                 // +0x44c
    int positionx;               // +0x450
    int positiony;               // +0x454
    unsigned char unknown_458[GINFO_SIZE_LEGACY - 0x458];
    // Shape extension, valid only when size == GINFO_SIZE_SHAPE.
    int shapeflagsx;             // +0x2890
    int shapeflagsy;             // +0x2894
    int shaperecordcount;        // +0x2898 at most 32 (reader cap at 1010a6fa)
    GSHAPERECORD shaperecord[32]; // +0x289c
    int unknown_2a9c[2];         // +0x2a9c
};

static_assert(offsetof(GINFO, colour) == 0x28, "GINFO layout");
static_assert(offsetof(GINFO, attributes) == 0x428, "GINFO layout");
static_assert(offsetof(GINFO, alphabits) == 0x438, "GINFO layout");
static_assert(offsetof(GINFO, positiony) == 0x454, "GINFO layout");
static_assert(offsetof(GINFO, shapeflagsx) == GINFO_SIZE_LEGACY, "GINFO layout");
static_assert(offsetof(GINFO, shaperecord) == 0x289c, "GINFO layout");
static_assert(sizeof(GINFO) == GINFO_SIZE_SHAPE, "GINFO layout");

// An image as FaceInRace passes it around: descriptor, pixels and row stride (12 bytes).
struct GIMAGE
{
    GINFO *info;
    unsigned char *pixels;
    int rowbytes;
};

// ---------------------------------------------------------------------------------------------
// Module description returned by about() (0xdc bytes).

#define GABOUT_FLAG_DETECT_BY_CONTENT 0x8000  // bit 15: is() is meaningful, else match names

struct GABOUT
{
    unsigned tag;                // +0x00
    int size;                    // +0x04 sizeof(GABOUT)
    int version;                 // +0x08 GINFO_VERSION
    unsigned flags;              // +0x0c
    int unknown_10;              // +0x10
    int unknown_14;              // +0x14
    int unknown_18;              // +0x18
    unsigned unknown_1c[2];      // +0x1c
    unsigned char unknown_24[0x3c - 0x24];
    char extension[8][8];        // +0x3c ".fsh", …
    char author[32];             // +0x7c
    char moduleversion[8];       // +0x9c "2.07"
    char shortname[8];           // +0xa4 "FSH"
    char longname[16];           // +0xac "FSH"
    char name[32];               // +0xbc "FSH Shape File"
};

static_assert(offsetof(GABOUT, extension) == 0x3c, "GABOUT layout");
static_assert(offsetof(GABOUT, shortname) == 0xa4, "GABOUT layout");
static_assert(sizeof(GABOUT) == 0xdc, "GABOUT layout");

// ---------------------------------------------------------------------------------------------
// Buffered file handle created by gopen/gwopen (0x2424 bytes).

#define GSTREAM_BUFFER_SIZE 0x2000

struct GSTREAM
{
    void *file;                  // +0x000 FILE*
    int position;                // +0x004 logical position
    int length;                  // +0x008 file length
    int bufferstart;             // +0x00c file offset of buffer[0]
    unsigned char *cursor;       // +0x010
    unsigned char *end;          // +0x014 end of valid buffer data
    int writable;                // +0x018
    int dirty;                   // +0x01c
    int mode;                    // +0x020 gopen: 1 for a real file, 0 for "con:"; gwopen: backup mode
    char name[0x200];            // +0x024
    char writename[0x200];       // +0x224
    unsigned char buffer[GSTREAM_BUFFER_SIZE]; // +0x424
};

static_assert(offsetof(GSTREAM, name) == 0x24, "GSTREAM layout");
static_assert(offsetof(GSTREAM, buffer) == 0x424, "GSTREAM layout");
static_assert(sizeof(GSTREAM) == 0x2424, "GSTREAM layout");

// ---------------------------------------------------------------------------------------------
// Application callbacks.  FaceInRace implements them (dev/FaceInRace); the names in quotes
// are attested by their own diagnostic prefixes.

void *GCALL galloc(int size);                               // "galloc"
int GCALL gfree(void *memory);                              // "gfree"
GSTREAM *GCALL gopen(const char *name);                     // "gopen"
GSTREAM *GCALL gwopen(const char *name);                    // "gwopen"
int GCALL gclose(GSTREAM *stream);
int GCALL gread(GSTREAM *stream, void *buffer, int count);  // "gread"
int GCALL gwrite(GSTREAM *stream, const void *buffer, int count); // "gwrite"
int GCALL gseek(GSTREAM *stream, int position);
int GCALL glen(GSTREAM *stream);
int GCALL gtell(GSTREAM *stream);

extern int gwopenbackupmode;                                // 0x10431a40, initialised to 3
extern int(__cdecl *gerror)(const char *format, ...);       // 0x10431a44, printf

// Byte order helpers (cdecl).
int ggetm(const void *source, int count);                   // big-endian read
int ggeti(const void *source, int count);                   // little-endian read
void gputm(void *destination, int value, int count);        // big-endian write
void gputi(void *destination, unsigned value, int count);   // little-endian write

// ---------------------------------------------------------------------------------------------
// Format modules: nine entry points per module, table at 0x10431a50 (0x24 bytes per module).

typedef GABOUT *(__cdecl *GABOUTFN)(void);
typedef int(GCALL *GISFN)(GSTREAM *stream);
typedef int(GCALL *GOPENFN)(void **handle, GSTREAM *stream, const char *name, int frame);
typedef GINFO *(GCALL *GINFOFN)(void *handle, int frame);
typedef int(GCALL *GREADFN)(void *handle, GINFO *info, void *pixels, int rowbytes);
typedef int(GCALL *GCLOSEFN)(void *handle);
typedef int(GCALL *GWOPENFN)(void **handle, GSTREAM *stream, const char *name, int frames);
typedef int(GCALL *GWRITEFN)(void *handle, const GINFO *info, const void *pixels, int rowbytes);
typedef int(GCALL *GWCLOSEFN)(void *handle);

struct GMODULE
{
    GABOUTFN about;
    GISFN is;
    GOPENFN open;
    GINFOFN info;
    GREADFN read;
    GCLOSEFN close;
    GWOPENFN wopen;
    GWRITEFN write;
    GWCLOSEFN wclose;
};

extern GMODULE gimexmodules[];                              // 0x10431a50, null-terminated

int GCALL GIMEX_ok(void);
void GCALL GIMEX_end(void);
GABOUT *GCALL GIMEX_about(void);
int GCALL GIMEX_is(GSTREAM *stream);
int GCALL GIMEX_open(void **handle, GSTREAM *stream, const char *name, int frame);
GINFO *GCALL GIMEX_info(void *handle, int frame);
int GCALL GIMEX_read(void *handle, GINFO *info, void *pixels, int rowbytes);
int GCALL GIMEX_close(void *handle);
int GCALL GIMEX_wopen(void **handle, GSTREAM *stream, const char *name, int frames);
int GCALL GIMEX_write(void *handle, const GINFO *info, const void *pixels, int rowbytes);
int GCALL GIMEX_wclose(void *handle);
void GCALL GIMEX_set(int module);
int GCALL GIMEX_get(void);
int GCALL GIMEX_count(void);
int GCALL GIMEX_find(const char *extension, int *extensionindex);
int GCALL GIMEX_detect(const char *name, GSTREAM *stream);
GSTREAM *GCALL GIMEX_openfile(const char *name, char *foundname);
int GCALL GIMEX_open1(void **handle, GSTREAM *stream, const char *name);
void GCALL GIMEX_freeimage(GIMAGE *image);
GIMAGE *GCALL GIMEX_load(const char *name, int frame);

// ---------------------------------------------------------------------------------------------
// Filters: five entry points per filter, table at 0x10432428 (0x14 bytes per filter).

struct GFILTERABOUT;   // 0x1480 bytes, name at +0x48

// Unlike modules and quantizers, filter entry points are cdecl: the dispatchers at
// 100053c8… pop the arguments themselves (add esp, n) and skip null entries.
typedef GFILTERABOUT *(__cdecl *GFILTERABOUTFN)(void);
typedef int(__cdecl *GFILTEROPENFN)(void **handle, int images, GIMAGE *image, int values, void *value);
typedef GINFO *(__cdecl *GFILTERINFOFN)(void *handle, int frame);
typedef int(__cdecl *GFILTERREADFN)(void *handle, GINFO *info, void *pixels, int rowbytes);
typedef int(__cdecl *GFILTERCLOSEFN)(void *handle);

struct GFILTER
{
    GFILTERABOUTFN about;
    GFILTEROPENFN open;
    GFILTERINFOFN info;
    GFILTERREADFN read;
    GFILTERCLOSEFN close;
};

extern GFILTER gimexfilters[];                              // 0x10432428, null-terminated

// A filter parameter is an 8-byte slot; FaceInRace fills only the first word.
struct GFILTERVALUE
{
    int value;
    int unused;
};

GFILTERABOUT *GCALL GFILTER_about(void);
int GCALL GFILTER_open(void **handle, int images, GIMAGE *image, int values, void *value);
GINFO *GCALL GFILTER_info(void *handle, int frame);
int GCALL GFILTER_read(void *handle, GINFO *info, void *pixels, int rowbytes);
int GCALL GFILTER_close(void *handle);
int GCALL GFILTER_find(const char *name);
void GCALL GFILTER_set(int filter);
int GCALL GFILTER_get(void);
int GCALL GFILTER_count(void);
int GCALL GFILTER_ok(void);
void GCALL GFILTER_end(void);
GIMAGE *GCALL GFILTER_apply(const char *name, GIMAGE *image, int values, void *value);
GIMAGE *GCALL GFILTER_run(int images, GIMAGE *image, int values, void *value);
void GCALL GFILTER_freeimage(GIMAGE *image);

// ---------------------------------------------------------------------------------------------
// Colour quantizers: four entry points, table at 0x10432720 (0x10 bytes per quantizer).

struct GQUANTABOUT;    // 0x68 bytes, name at +0x38

typedef GQUANTABOUT *(__cdecl *GQUANTABOUTFN)(void);
typedef void *(__cdecl *GQUANTOPENFN)(void);
typedef int(GCALL *GQUANTADDFN)(void *handle, const GINFO *info, const void *pixels, int rowbytes);
typedef GCOLOUR *(GCALL *GQUANTMAKEFN)(void *handle, int colours, int *exact);

struct GQUANT
{
    GQUANTABOUTFN about;
    GQUANTOPENFN open;
    GQUANTADDFN add;
    GQUANTMAKEFN make;
};

extern GQUANT gimexquantizers[];                            // 0x10432720, null-terminated

GQUANTABOUT *GCALL GQUANT_about(void);
void *GCALL GQUANT_open(void);
int GCALL GQUANT_add(void *handle, const GINFO *info, const void *pixels, int rowbytes);
GCOLOUR *GCALL GQUANT_make(void *handle, int colours, int *exact);
int GCALL GQUANT_find(const char *name);
void GCALL GQUANT_set(int quantizer);
int GCALL GQUANT_get(void);
int GCALL GQUANT_count(void);
int GCALL GQUANT_ok(void);
void GCALL GQUANT_end(void);

#endif
