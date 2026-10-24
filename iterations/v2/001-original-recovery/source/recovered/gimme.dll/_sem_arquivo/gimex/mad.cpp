// "Madcow Movie" module 1.09 (Kaz Okuda): GIMEX module 64.
// gimme.dll 3a43b0f6…, entry points about 100125d0, is 100127bf, open 100128b1, info 10012b2f, read 10012daf, close 100133b2,
// wopen 100121a0, write 10012224, wclose 10012581.  about() and is() are recovered; the other entry points
// are recovery boundaries (boundary.h) until the module is recovered.

#include <stdlib.h>
#include <string.h>

#include "boundary.h"

// 100125d0.
GABOUT *MAD_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('M', 'A', 'D', 'C');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x9612;
        about->unknown_14 = 0;
        about->unknown_18 = 70;
        about->mactype[0] = GTAG('M', 'A', 'D', 'C');
        strcpy(about->extension[0], ".mad");
        strcpy(about->author, "Kaz Okuda");
        strcpy(about->moduleversion, "1.09");
        strcpy(about->shortname, "Mad");
        strcpy(about->longname, "Madcow");
        strcpy(about->name, "Madcow Movie");
    }
    return about;
}

// 100127bf.
// Walks up to three chunks of an EA movie: "MADe/k/m" is Madcow (100), "SCCl/SCDl/SCHl" only
// a candidate (10).  Chunk sizes are little-endian and include the 8-byte header.
int GCALL MAD_is(GSTREAM *stream)
{
    int score = 0;
    int chunks = 3;
    unsigned char header[8];
    gseek(stream, 0);
    gread(stream, header, 8);
    while (chunks)
    {
        unsigned tag = ggetm(header, 4);
        if (tag == GTAG('M', 'A', 'D', 'e') || tag == GTAG('M', 'A', 'D', 'k') || tag == GTAG('M', 'A', 'D', 'm'))
        {
            score = 100;
            chunks = 0;
            continue;
        }
        if (tag == GTAG('S', 'C', 'C', 'l') || tag == GTAG('S', 'C', 'D', 'l') || tag == GTAG('S', 'C', 'H', 'l'))
            score = 10;
        --chunks;
        int position = gtell(stream);
        gseek(stream, position - 8 + ggeti(header + 4, 4));
        gread(stream, header, 8);
    }
    return score;
}

GIMEX_BOUNDARY_READ(MAD)
GIMEX_BOUNDARY_WRITE(MAD)
