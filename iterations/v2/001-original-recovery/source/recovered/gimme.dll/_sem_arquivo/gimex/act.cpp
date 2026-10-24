// "ACT Photoshop Palette" module 1.02 (FrANK G. Barchard): GIMEX module 18.
// gimme.dll 3a43b0f6…, entry points about 100d55d0, is 100d57be, open 100d5918, info 100d5981, read 100d5b72, close 100d5bab,
// wopen 100d54b0, write 100d5506, wclose 100d559b.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100d55d0.
GABOUT *ACT_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'A', 'C', 'T');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x90c3;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('8', 'B', 'C', 'T');
        strcpy(about->extension[0], ".act");
        strcpy(about->extension[1], ".pal");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.02");
        strcpy(about->shortname, "ACT");
        strcpy(about->longname, "ACT");
        strcpy(about->name, "ACT Photoshop Palette");
    }
    return about;
}

// 100d57be.
// A 768-byte palette; black and white at the ends and no other pure black or white entry
// (except entry 15) double the score.
int GCALL ACT_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char palette[0x300];
    int length = glen(stream);
    gseek(stream, 0);
    if (gread(stream, palette, 0x300) && length == 0x300)
    {
        score = 10;
        int first = ggetm(palette, 3);
        int last = ggetm(palette + 0x2fd, 3);
        if ((first == 0 && last == 0xffffff) || (first == 0xffffff && last == 0))
            score = 20;
        int i = 1;
        while (i < 255)
        {
            if (i != 15)
            {
                int colour = ggetm(palette + i * 3, 3);
                if (colour == 0 || colour == 0xffffff)
                    break;
            }
            ++i;
        }
        if (i == 255)
            score <<= 1;
    }
    return score;
}

GIMEX_BOUNDARY_READ(ACT)
GIMEX_BOUNDARY_WRITE(ACT)
