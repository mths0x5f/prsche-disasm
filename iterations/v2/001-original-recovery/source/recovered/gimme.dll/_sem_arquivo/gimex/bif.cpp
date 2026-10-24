// "Binary Info File" module 1.04 (FrANK G. Barchard): GIMEX module 13.
// gimme.dll 3a43b0f6…, entry points about 100ddf89, is 100de17b, open 100de210, info 100de282, read 100de8c6, close 100defe1,
// wopen 100dc9a0, write 100dc9ff, wclose 100dd08e.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100ddf89.
GABOUT *BIF_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'H', 'S', 'I');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x9303;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'B', 'I', 'F');
        strcpy(about->extension[0], ".bif");
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.04");
        strcpy(about->shortname, "BIF");
        strcpy(about->longname, "BIF");
        strcpy(about->name, "Binary Info File");
    }
    return about;
}

// 100de17b.
// The environment variable BIF, when set, names the file to test instead of the stream.
int GCALL BIF_is(GSTREAM *stream)
{
    int score = 0;
    char magic[4];
    const char *alternative = getenv("BIF");
    if (alternative)
        stream = gopen(alternative);
    gseek(stream, 0);
    if (gread(stream, magic, 4) && magic[0] == 'B' && magic[1] == 'I' && magic[2] == 'F')
        score = 100;
    if (alternative)
        gclose(stream);
    return score;
}

GIMEX_BOUNDARY_READ(BIF)
GIMEX_BOUNDARY_WRITE(BIF)
