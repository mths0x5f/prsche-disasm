// "MVI Movie" module 1.14 (F Barchard & A Brownsword): GIMEX module 35.
// gimme.dll 3a43b0f6…, entry points about 10075e29, is 1007600a, open 10076099, info 100761ec, read 100763be, close 1007645c,
// wopen 100721d0, write 10072242, wclose 100723df.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 10075e29.
GABOUT *MVI_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'M', 'V', 'I');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xb4d7;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'M', 'V', 'I');
        strcpy(about->extension[0], ".mvi");
        strcpy(about->extension[1], ".cmv");
        strcpy(about->author, "F Barchard & A Brownsword");
        strcpy(about->moduleversion, "1.14");
        strcpy(about->shortname, "MVI");
        strcpy(about->longname, "MVI");
        strcpy(about->name, "MVI Movie");
    }
    return about;
}

// 1007600a.
int GCALL MVI_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char magic[4];
    gseek(stream, 0);
    if (gread(stream, magic, 4))
    {
        if (ggetm(magic, 4) != GTAG('M', 'V', 'I', 's') && ggetm(magic, 4) != GTAG('M', 'V', 'I', 'h') &&
            ggetm(magic, 4) != GTAG('M', 'V', 'I', 'f') && ggetm(magic, 2) != 0xc6fb)
            return 0;
        score = 100;
    }
    return score;
}

GIMEX_BOUNDARY_READ(MVI)
GIMEX_BOUNDARY_WRITE(MVI)
