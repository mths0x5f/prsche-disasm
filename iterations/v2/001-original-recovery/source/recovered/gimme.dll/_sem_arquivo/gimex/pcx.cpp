// "ZSoft PCX" module 1.05 (FrANK G. Barchard): GIMEX module 16.
// gimme.dll 3a43b0f6…, entry points about 100d7060, is 100d727b, open 100d72fd, info 100d743e, read 100d78fa, close 100d7fb1,
// wopen 100d68f0, write 100d69e9, wclose 100d6fb6.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100d7060.
GABOUT *PCX_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'P', 'C', 'X');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x97d7;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('P', 'C', 'X', ' ');
        about->mactype[1] = GTAG('B', 'I', 'N', 'A');
        strcpy(about->extension[0], ".pcx");
        strcpy(about->extension[1], ".dcx");
        strcpy(about->extension[2], ".pcc");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.05");
        strcpy(about->shortname, "PCX");
        strcpy(about->longname, "PCX");
        strcpy(about->name, "ZSoft PCX");
    }
    return about;
}

// 100d727b.
int GCALL PCX_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[8];
    gseek(stream, 0);
    if (gread(stream, header, 8))
    {
        if (header[0] == 10 && header[1] < 6 && header[2] < 2)
            score = 95;
        else if (ggeti(header, 4) == 0x3ade68b1)   // DCX page table
            score = 100;
    }
    return score;
}

GIMEX_BOUNDARY_READ(PCX)
GIMEX_BOUNDARY_WRITE(PCX)
