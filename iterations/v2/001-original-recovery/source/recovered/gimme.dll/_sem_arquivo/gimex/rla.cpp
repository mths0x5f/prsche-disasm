// "WaveFront RLA" module 1.06 (FrANK G. Barchard): GIMEX module 19.
// gimme.dll 3a43b0f6…, entry points about 100d4860, is 100d4a7d, open 100d4bba, info 100d4c23, read 100d4e65, close 100d547b,
// wopen 100d3f10, write 100d3f66, wclose 100d482f.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100d4860.
GABOUT *RLA_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'R', 'L', 'A');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x9317;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'R', 'L', 'A');
        strcpy(about->extension[0], ".rla");
        strcpy(about->extension[1], ".rlb");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.06");
        strcpy(about->shortname, "RLA");
        strcpy(about->longname, "WaveFront");
        strcpy(about->name, "WaveFront RLA");
    }
    return about;
}

// 100d4a7d.
int GCALL RLA_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[0x2e4];
    gseek(stream, 0);
    if (gread(stream, header, 0x2e4) &&
        (unsigned)ggetm(header, 2) < (unsigned)ggetm(header + 2, 2) &&
        (unsigned)ggetm(header + 4, 2) < (unsigned)ggetm(header + 6, 2) &&
        (unsigned)ggetm(header + 8, 2) < (unsigned)ggetm(header + 10, 2) &&
        (unsigned)ggetm(header + 12, 2) < (unsigned)ggetm(header + 14, 2) &&
        ggetm(header + 0x14, 2) != 0 && (unsigned)ggetm(header + 0x14, 2) < 5 &&
        (unsigned)ggetm(header + 0x16, 2) < 2)
        score = 95;
    return score;
}

GIMEX_BOUNDARY_READ(RLA)
GIMEX_BOUNDARY_WRITE(RLA)
