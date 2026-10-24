// "Alias Pix" module 1.00 (FrANK G. Barchard): GIMEX module 21.
// gimme.dll 3a43b0f6…, entry points about 100d0af0, is 100d0cfb, open 100d0daa, info 100d0e13, read 100d1019, close 100d119c,
// wopen 100d0820, write 100d0876, wclose 100d0abb.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100d0af0.
GABOUT *PIX_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('A', 'L', 'I', 'S');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x93d7;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'P', 'I', 'X');
        strcpy(about->extension[0], ".pix");
        strcpy(about->extension[1], ".als");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.00");
        strcpy(about->shortname, "PIX");
        strcpy(about->longname, "Alias");
        strcpy(about->name, "Alias Pix");
    }
    return about;
}

// 100d0cfb.
int GCALL PIX_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[10];
    gseek(stream, 0);
    if (gread(stream, header, 10) && ggetm(header, 2) != 0 && (unsigned)ggetm(header, 2) < 0x4000 &&
        ggetm(header + 2, 2) != 0 && (unsigned)ggetm(header + 2, 2) < 0x4000)
    {
        if (ggetm(header + 8, 2) != 0x18 && ggetm(header + 8, 2) != 8)
            return 0;
        score = 95;
    }
    return score;
}

GIMEX_BOUNDARY_READ(PIX)
GIMEX_BOUNDARY_WRITE(PIX)
