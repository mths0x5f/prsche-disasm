// "Amiga ILBM" module 1.20 (Frank Barchard): GIMEX module 6.
// gimme.dll 3a43b0f6…, entry points about 100e8480, is 100e86c1, open 100e8776, info 100e88df, read 100e967f, close 100e96a9,
// wopen 100e76c0, write 100e7716, wclose 100e8451.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100e8480.
GABOUT *LBM_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('I', 'L', 'B', 'M');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xb3d7;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('I', 'L', 'B', 'M');
        strcpy(about->extension[0], ".lbm");
        strcpy(about->extension[1], ".ilbm");
        strcpy(about->extension[2], ".bbm");
        strcpy(about->extension[3], ".iff");
        strcpy(about->author, "Frank Barchard");
        strcpy(about->moduleversion, "1.20");
        strcpy(about->shortname, "LBM");
        strcpy(about->longname, "ILBM");
        strcpy(about->name, "Amiga ILBM");
    }
    return about;
}

// 100e86c1.
int GCALL LBM_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[12];
    int length = glen(stream);
    gseek(stream, 0);
    if (gread(stream, header, 12))
    {
        int size = ggetm(header + 4, 4);
        if (ggetm(header, 4) == GTAG('F', 'O', 'R', 'M') && size > 0 && size <= length)
        {
            score = 75;
            int type = ggetm(header + 8, 4);
            if (type == GTAG('A', 'N', 'I', 'M') || type == GTAG('I', 'L', 'B', 'M') || type == GTAG('P', 'B', 'M', ' '))
                score = 100;
        }
    }
    return score;
}

GIMEX_BOUNDARY_READ(LBM)
GIMEX_BOUNDARY_WRITE(LBM)
