// "VAN DOS/PC" module 1.00 (Sam Deasy): GIMEX module 62.
// gimme.dll 3a43b0f6…, entry points about 10015310, is 10015506, open 10015577, info 1001592c, read 10015d27, close 10016597,
// wopen 10015048, write 10013a30, wclose 1001524a.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 10015310.
GABOUT *VAN_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'V', 'A', 'N');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x194ff;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->mactype[0] = GTAG('.', 'V', 'A', 'N');
        strcpy(about->extension[0], ".van");
        strcpy(about->author, "Sam Deasy");
        strcpy(about->moduleversion, "1.00");
        strcpy(about->shortname, "VAN");
        strcpy(about->longname, "VAN");
        strcpy(about->name, "VAN DOS/PC");
    }
    return about;
}

// 10015506.
int GCALL VAN_is(GSTREAM *stream)
{
    int score = 0;
    char magic[4];
    gseek(stream, 0);
    if (gread(stream, magic, 4) && magic[0] == 'V' && magic[1] == 'A' && magic[2] == 'N' && magic[3] == 'M')
        score = 100;
    return score;
}

GIMEX_BOUNDARY_READ(VAN)
GIMEX_BOUNDARY_WRITE(VAN)
