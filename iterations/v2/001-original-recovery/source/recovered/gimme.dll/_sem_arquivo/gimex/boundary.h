// Recovery boundaries: entry points of the original that are not recovered yet.
//
// They are not imitations.  Each one reports itself through gerror, sets gimexboundaryhit
// and fails the way a module fails on data it cannot handle (0 / null).  ConvertFile checks
// gimexboundaryhit after opening the source and stops there, so a file routed to an
// unrecovered module yields no portrait instead of a crash.  The list of boundaries is in
// README.md; each one disappears when its module is recovered.

#ifndef GIMEX_BOUNDARY_H
#define GIMEX_BOUNDARY_H

#include "gimex.h"

extern int gimexboundaryhit;
int gimexboundary(const char *entry);

#define GIMEX_BOUNDARY_READ(prefix)                                                              \
    int GCALL prefix##_open(void **handle, GSTREAM *, const char *, int)                          \
    {                                                                                            \
        *handle = 0;                                                                             \
        return gimexboundary(#prefix "_open");                                                   \
    }                                                                                            \
    GINFO *GCALL prefix##_info(void *, int)                                                      \
    {                                                                                            \
        gimexboundary(#prefix "_info");                                                          \
        return 0;                                                                                \
    }                                                                                            \
    int GCALL prefix##_read(void *, GINFO *, void *, int) { return gimexboundary(#prefix "_read"); } \
    int GCALL prefix##_close(void *) { return gimexboundary(#prefix "_close"); }

#define GIMEX_BOUNDARY_WRITE(prefix)                                                             \
    int GCALL prefix##_wopen(void **handle, GSTREAM *, const char *, int)                         \
    {                                                                                            \
        *handle = 0;                                                                             \
        return gimexboundary(#prefix "_wopen");                                                  \
    }                                                                                            \
    int GCALL prefix##_write(void *, const GINFO *, const void *, int) { return gimexboundary(#prefix "_write"); } \
    int GCALL prefix##_wclose(void *) { return gimexboundary(#prefix "_wclose"); }

#endif
