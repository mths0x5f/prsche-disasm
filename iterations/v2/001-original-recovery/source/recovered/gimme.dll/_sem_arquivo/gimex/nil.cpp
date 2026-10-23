// "Nil Gimex" module 1.02 (FrANK G. Barchard): module 0, the fallback when nothing matches.
// gimme.dll 3a43b0f6…, VA 1010b840–1010ba55.  Its three write entry points are shared by the
// read-only modules 37 and 58.

#include <string.h>

#include "gimex.h"

// 1010b860.  Every flag bit is cleared except bit 12.
GABOUT *NIL_about(void)
{
    GABOUT *about = (GABOUT *)galloc(sizeof(GABOUT));
    if (about)
    {
        memset(about, 0, sizeof(GABOUT));
        about->tag = GTAG('.', 'N', 'I', 'L');
        about->size = sizeof(GABOUT);
        about->version = GINFO_VERSION;
        about->flags = 0x1000;
        about->unknown_14 = 0;
        about->unknown_18 = 100;
        about->unknown_1c[0] = 0;
        strcpy(about->author, "FrANK G. Barchard");
        strcpy(about->moduleversion, "1.02");
        strcpy(about->shortname, "Nil");
        strcpy(about->longname, "Nil");
        strcpy(about->name, "Nil Gimex");
    }
    return about;
}

// 1010ba2b … 1010ba4f.
int GCALL NIL_is(GSTREAM *)
{
    return 0;
}

int GCALL NIL_open(void **, GSTREAM *, const char *, int)
{
    return 0;
}

GINFO *GCALL NIL_info(void *, int)
{
    return 0;
}

int GCALL NIL_read(void *, GINFO *, void *, int)
{
    return 0;
}

int GCALL NIL_close(void *)
{
    return 0;
}

// 1010b840 … 1010b852.
int GCALL NIL_wopen(void **, GSTREAM *, const char *, int)
{
    return 0;
}

int GCALL NIL_write(void *, const GINFO *, const void *, int)
{
    return 0;
}

int GCALL NIL_wclose(void *)
{
    return 0;
}
