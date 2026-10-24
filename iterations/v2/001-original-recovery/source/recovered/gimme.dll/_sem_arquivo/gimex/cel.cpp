// "3DO Cel" module 1.11 (L Ancessi & F Barchard): GIMEX module 58.
// gimme.dll 3a43b0f6…, entry points about 10019c3d, is 10019b87, open 10019e73, info 1001a843, read 1001b2d5, close 1001bf2c,
// wopen 1010b840, write 1010b849, wclose 1010b852.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 10019c3d.
GABOUT *CEL_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG(0, 'C', 'E', 'L');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xb545;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('3', 'D', 'O', 'c');
        about->mactype[1] = GTAG('3', 'D', 'O', 'a');
        about->mactype[2] = GTAG('3', 'D', 'O', 's');
        strcpy(about->extension[0], ".cel");
        strcpy(about->extension[1], ".anim");
        strcpy(about->extension[2], ".sanim");
        strcpy(about->extension[3], ".ani");
        strcpy(about->extension[4], ".san");
        strcpy(about->author, "L Ancessi & F Barchard");
        strcpy(about->moduleversion, "1.11");
        strcpy(about->shortname, "CEL");
        strcpy(about->longname, "Cel");
        strcpy(about->name, "3DO Cel");
    }
    return about;
}

// 10019b87.
int GCALL CEL_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[8];
    int length = glen(stream);
    gseek(stream, 0);
    if (gread(stream, header, 8))
    {
        int chunk = ggetm(header, 4);
        int size = ggetm(header + 4, 4);
        if ((chunk == GTAG('C', 'C', 'B', ' ') || chunk == GTAG('P', 'L', 'U', 'T') || chunk == GTAG('S', 'A', 'N', 'M') ||
             chunk == GTAG('A', 'N', 'I', 'M') || chunk == GTAG('X', 'T', 'R', 'A') || chunk == GTAG('O', 'F', 'S', 'T') ||
             chunk == GTAG('H', 'S', 'P', 'T')) &&
            size > 0 && size <= length)
            score = 100;
    }
    return score;
}

GIMEX_BOUNDARY_READ(CEL)
