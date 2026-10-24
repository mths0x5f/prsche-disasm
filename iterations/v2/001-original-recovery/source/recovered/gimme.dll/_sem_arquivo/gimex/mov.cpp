// "QuickTime Movie" module 1.31 (FrANK Barchard & Kaz Okuda): GIMEX module 20.
// gimme.dll 3a43b0f6…, entry points about 100d2f37, is 100d313f, open 100d3205, info 100d3bf5, read 100d2dce, close 100d3e59,
// wopen 100d11d0, write 100d1297, wclose 100d15a4.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

int GCALL MOV_open(void **, GSTREAM *, const char *, int);
int GCALL MOV_close(void *);

// 100d2f37.
GABOUT *MOV_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('M', 'O', 'O', 'V');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x8747;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('M', 'o', 'o', 'V');
        strcpy(about->extension[0], ".mov");
        strcpy(about->extension[1], ".qt");
        strcpy(about->extension[2], ".moov");
        strcpy(about->author, "FrANK Barchard & Kaz Okuda");
        strcpy(about->moduleversion, "1.31");
        strcpy(about->shortname, "MOV");
        strcpy(about->longname, "QuickTime");
        strcpy(about->name, "QuickTime Movie");
    }
    return about;
}

// 100d313f.
// A QuickTime file (optionally behind an 8-byte "wide" atom) that MOV_open accepts.
int GCALL MOV_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char atom[8];
    void *handle;
    gseek(stream, 0);
    if (gread(stream, atom, 8))
    {
        if (ggetm(atom + 4, 4) == GTAG('w', 'i', 'd', 'e'))
            gseek(stream, 8);
        else
            gseek(stream, 0);
    }
    if (gread(stream, atom, 8))
    {
        if (ggetm(atom + 4, 4) != GTAG('m', 'd', 'a', 't') && ggetm(atom + 4, 4) != GTAG('m', 'o', 'o', 'v'))
            return score;
        if (MOV_open(&handle, stream, "name", 0))
        {
            score = 100;
            MOV_close(handle);
        }
    }
    return score;
}

GIMEX_BOUNDARY_READ(MOV)
GIMEX_BOUNDARY_WRITE(MOV)
