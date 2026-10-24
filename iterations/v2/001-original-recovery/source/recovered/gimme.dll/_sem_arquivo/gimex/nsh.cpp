// "NSH Nintendo 64 Shape File" module 2.07 (F Barchard): GIMEX module 45.
// gimme.dll 3a43b0f6…, entry points about 10064740, is 10064956, open 100649a7, info 100669b7, read 10068178, close 10068f37,
// wopen 10057320, write 100573e4, wclose 1006311d.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 10064740.
GABOUT *NSH_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('S', 'H', 'P', 'N');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xb7eb;
        about->unknown_14 = 4;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'n', 's', 'h');
        strcpy(about->extension[0], ".nsh");
        strcpy(about->author, "F Barchard");
        strcpy(about->moduleversion, "2.07");
        strcpy(about->shortname, "NSH");
        strcpy(about->longname, "NSH");
        strcpy(about->name, "NSH Nintendo 64 Shape File");
    }
    return about;
}

// 10064956.
int GCALL NSH_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char header[16];
    gseek(stream, 0);
    if (gread(stream, header, 16) == 16 && ggetm(header, 4) == GTAG('S', 'H', 'P', 'N'))
        score = 100;
    return score;
}

GIMEX_BOUNDARY_READ(NSH)
GIMEX_BOUNDARY_WRITE(NSH)
