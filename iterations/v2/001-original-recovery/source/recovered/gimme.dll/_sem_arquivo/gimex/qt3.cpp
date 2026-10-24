// "QuickTime3 Movie" module 1.00 (Kaz Okuda): GIMEX module 50.
// gimme.dll 3a43b0f6…, entry points about 100310b0, is 100312c5, open 100313b2, info 10031742, read 1003186b, close 100319f8,
// wopen 10031090, write 10031099, wclose 100310a2.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100310b0.
GABOUT *QT3_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('M', 'O', 'O', 'V');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x8545;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('M', 'o', 'o', 'V');
        strcpy(about->extension[0], ".mov");
        strcpy(about->extension[1], ".qt");
        strcpy(about->author, "Kaz Okuda");
        strcpy(about->moduleversion, "1.00");
        strcpy(about->shortname, "QT3");
        strcpy(about->longname, "QuickTime3");
        strcpy(about->name, "QuickTime3 Movie");
    }
    return about;
}

// 100312c5.
int GCALL QT3_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char atom[8];
    gseek(stream, 0);
    if (gread(stream, atom, 8))
    {
        if (ggetm(atom + 4, 4) == GTAG('w', 'i', 'd', 'e') && ggetm(atom, 4) == 8)
            gseek(stream, 8);
        else
            gseek(stream, 0);
    }
    if (gread(stream, atom, 8))
    {
        if (ggetm(atom + 4, 4) != GTAG('m', 'd', 'a', 't') && ggetm(atom + 4, 4) != GTAG('m', 'o', 'o', 'v'))
            return 0;
        score = 80;
    }
    return score;
}

GIMEX_BOUNDARY_READ(QT3)
GIMEX_BOUNDARY_WRITE(QT3)
