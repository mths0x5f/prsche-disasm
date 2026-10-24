// "SSH Sony Shape File" module 2.07 (F Barchard): GIMEX module 49.
// gimme.dll 3a43b0f6…, entry points about 1003eed0, is 1003f0e3, open 1003f134, info 10041144, read 10042905, close 100436c4,
// wopen 10031ab0, write 10031b74, wclose 1003d8ad.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 1003eed0.
GABOUT *SSH_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('S', 'H', 'P', 'S');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xb7eb;
        about->unknown_14 = 4;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 's', 's', 'h');
        strcpy(about->extension[0], ".ssh");
        strcpy(about->author, "F Barchard");
        strcpy(about->moduleversion, "2.07");
        strcpy(about->shortname, "SSH");
        strcpy(about->longname, "SSH");
        strcpy(about->name, "SSH Sony Shape File");
    }
    return about;
}

// 1003f0e3.
int GCALL SSH_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[16];
    gseek(stream, 0);
    if (gread(stream, header, 16) == 16 && ggetm(header, 4) == GTAG('S', 'H', 'P', 'S'))
        score = 100;
    return score;
}

GIMEX_BOUNDARY_READ(SSH)
GIMEX_BOUNDARY_WRITE(SSH)
