// "S3 Texture" module 1.03 (FrANK G. Barchard): GIMEX module 4.
// gimme.dll 3a43b0f6…, entry points about 100f46e0, is 100f48ea, open 100f493a, info 100f49a3, read 100f4b7c, close 100f525c,
// wopen 100ebb00, write 100ebb47, wclose 100f46ae.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100f46e0.
GABOUT *S3T_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('S', '3', 'T', 'C');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0xb317;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'S', '3', 'T');
        strcpy(about->extension[0], ".s3t");
        strcpy(about->extension[1], ".s3tc");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.03");
        strcpy(about->shortname, "S3T");
        strcpy(about->longname, "S3T");
        strcpy(about->name, "S3 Texture");
    }
    return about;
}

// 100f48ea.
int GCALL S3T_is(GSTREAM *stream)
{
    int score = 0;
    unsigned char magic[4];
    gseek(stream, 0);
    if (gread(stream, magic, 4) && ggetm(magic, 4) == (int)0x91910000)
        score = 100;
    return score;
}

GIMEX_BOUNDARY_READ(S3T)
GIMEX_BOUNDARY_WRITE(S3T)
