// "Ninja 3 CharMap" module 1.04 (FrANK G. Barchard): GIMEX module 37.
// gimme.dll 3a43b0f6…, entry points about 10070d90, is 10070fb2, open 1007104f, info 100710c1, read 100715e8, close 10071b0d,
// wopen 1010b840, write 1010b849, wclose 1010b852.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 10070d90.
GABOUT *CMP_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'C', 'M', 'P');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x9841;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'C', 'M', 'P');
        strcpy(about->extension[0], ".cmp");
        strcpy(about->extension[1], ".chr");
        strcpy(about->extension[2], ".pal");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.04");
        strcpy(about->shortname, "CMP");
        strcpy(about->longname, "Ninja");
        strcpy(about->name, "Ninja 3 CharMap");
    }
    return about;
}

// 10070fb2.
// Width and height words followed by 16-bit cells must account for the whole file.
int GCALL CMP_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[6];
    gseek(stream, 0);
    if (gread(stream, header, 6))
    {
        int width = ggeti(header, 2);
        int height = ggeti(header + 2, 2);
        int expected = width * height * 2 + 6;
        if (expected == glen(stream) && width > 0 && width <= 0x2000 && height > 0 && height <= 0x2000)
            score = 95;
    }
    return score;
}

GIMEX_BOUNDARY_READ(CMP)
