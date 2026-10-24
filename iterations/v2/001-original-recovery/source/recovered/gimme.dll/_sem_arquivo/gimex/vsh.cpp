// "VSH Shape File" module 2.07 (F Barchard): GIMEX module 32.
// gimme.dll 3a43b0f6…, entry points about 1008a120, is 1008a351, open 1008a3ff, info 1008c40f, read 1008dbd0, close 1008e98f,
// wopen 1007cd00, write 1007cdc4, wclose 10088afd.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 1008a120.
GABOUT *VSH_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('S', 'H', 'P', 'V');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xb4eb;
        about->unknown_14 = 4;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'v', 's', 'h');
        strcpy(about->extension[0], ".vsh");
        strcpy(about->author, "F Barchard");
        strcpy(about->moduleversion, "2.07");
        strcpy(about->shortname, "VSH");
        strcpy(about->longname, "VSH");
        strcpy(about->name, "VSH Shape File");
    }
    return about;
}

// 1008a351.
// The header holds the file length and the entry count (24 bytes per directory entry).
int GCALL VSH_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[16];
    gseek(stream, 0);
    if (gread(stream, header, 16) == 16)
    {
        int length = glen(stream);
        int stored = ggeti(header, 4);
        int entries = ggeti(header + 4, 2);
        if (entries > 0 && entries * 0x18 + 6 <= length && (unsigned)(stored - length + 0x10) < 0x20 &&
            entries < 0x5dd)
        {
            score = 50;
            if (stored == length && entries < 0x41)
                score = 100;
        }
    }
    return score;
}

GIMEX_BOUNDARY_READ(VSH)
GIMEX_BOUNDARY_WRITE(VSH)
