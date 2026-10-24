// "TQI Texture Quantized Image" module 1.01 (Martin Griffiths): GIMEX module 51.
// gimme.dll 3a43b0f6…, entry points about 10030a20, is 10030c97, open 10030d81, info 10030dea, read 10030fb3, close 1003106a,
// wopen 100308e0, write 1003092c, wclose 100309f0.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 10030a20.
GABOUT *TQI_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'T', 'Q', 'I');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xb317;
        about->unknown_14 = 0;
        about->unknown_18 = 90;
        about->mactype[0] = GTAG('.', 'T', 'Q', 'I');
        strcpy(about->extension[0], ".tqi");
        strcpy(about->extension[1], ".444");
        strcpy(about->author, "Martin Griffiths");
        strcpy(about->moduleversion, "1.01");
        strcpy(about->shortname, "TQI");
        strcpy(about->longname, "TQI");
        strcpy(about->name, "TQI Texture Quantized Image");
    }
    return about;
}

// 10030c97.
int GCALL TQI_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[8];
    gseek(stream, 0);
    if (!gread(stream, header, 8))
        return 0;
    unsigned flags = ggetm(header + 4, 1);
    if ((flags & 0x6e) != 100)
        return 0;
    if (!(flags & 1) || ggetm(header + 5, 3) != 0)
    {
        if (flags & 1)
            return 0;
        if (ggetm(header + 5, 3) != 0xff00ff)
            return 0;
    }
    if ((unsigned)ggeti(header, 2) > 7 && (unsigned)ggeti(header, 2) < 0x2001 &&
        (unsigned)ggeti(header + 2, 2) > 7 && (unsigned)ggeti(header + 2, 2) < 0x2001)
        score = 90;
    return score;
}

GIMEX_BOUNDARY_READ(TQI)
GIMEX_BOUNDARY_WRITE(TQI)
