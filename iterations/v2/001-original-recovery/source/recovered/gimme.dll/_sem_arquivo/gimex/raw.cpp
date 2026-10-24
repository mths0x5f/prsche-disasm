// "Erik Kiss RAW" module 1.04 (FrANK G. Barchard): GIMEX module 39.
// gimme.dll 3a43b0f6…, entry points about 1006fdb0, is 1006ff9b, open 10070032, info 1007009b, read 10070207, close 10070302,
// wopen 1006fc20, write 1006fc6c, wclose 1006fd8a.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 1006fdb0.
GABOUT *RAW_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'R', 'A', 'W');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x9303;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'R', 'A', 'W');
        strcpy(about->extension[0], ".raw");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.04");
        strcpy(about->shortname, "Raw");
        strcpy(about->longname, "Raw");
        strcpy(about->name, "Erik Kiss RAW");
    }
    return about;
}

// 1006ff9b.
int GCALL RAW_is(GSTREAM *stream)
{
    unsigned char header[4];
    gseek(stream, 0);
    if (gread(stream, header, 4))
    {
        int width = ggeti(header, 2);
        int height = ggeti(header + 2, 2);
        int pixels = width * height;
        if (pixels * 3 + 4 == glen(stream) && width > 0 && width <= 0x2000 && height > 0 && height <= 0x2000)
            return 95;
    }
    return 0;
}

GIMEX_BOUNDARY_READ(RAW)
GIMEX_BOUNDARY_WRITE(RAW)
