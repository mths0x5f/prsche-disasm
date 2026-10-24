// "Material" module 1.02 (Kaz Okuda): GIMEX module 65.
// gimme.dll 3a43b0f6…, entry points about 1001165c, is 1001184f, open 100118fc, info 10011bfc, read 10011f15, close 1001215c,
// wopen 10010bf0, write 10010cd7, wclose 10011117.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 1001165c.
GABOUT *MAT_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'M', 'A', 'T');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x97c3;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'M', 'A', 'T');
        strcpy(about->extension[0], ".mat");
        strcpy(about->author, "Kaz Okuda");
        strcpy(about->moduleversion, "1.02");
        strcpy(about->shortname, "MAT");
        strcpy(about->longname, "Material");
        strcpy(about->name, "Material");
    }
    return about;
}

// 1001184f.
int GCALL MAT_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[12];
    gseek(stream, 0);
    if (gread(stream, header, 12) && ggetm(header, 4) == GTAG('F', 'O', 'R', 'M') && ggetm(header + 4, 4) != 0 &&
        (unsigned)ggetm(header + 4, 4) <= (unsigned)glen(stream))
    {
        score = 75;
        int type = ggetm(header + 8, 4);
        if (type == GTAG('A', 'M', 'A', 'T') || type == GTAG('S', 'M', 'A', 'T'))
            score = 100;
    }
    return score;
}

GIMEX_BOUNDARY_READ(MAT)
GIMEX_BOUNDARY_WRITE(MAT)
