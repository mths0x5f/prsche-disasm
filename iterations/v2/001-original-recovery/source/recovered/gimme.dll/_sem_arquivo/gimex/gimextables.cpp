// The module, filter and quantizer tables linked into gimme.dll (0x10431a50, 0x10432428,
// 0x10432720).  The original order and indices are listed in runs/432-gimme-dll/components.md;
// only recovered entries are present here, so indices after the first missing module differ
// from the original until the missing modules are recovered.  See README.md (boundaries).

#include "gimex.h"

#define GIMEX_MODULE(prefix) \
    GABOUT *prefix##_about(void); \
    int GCALL prefix##_is(GSTREAM *); \
    int GCALL prefix##_open(void **, GSTREAM *, const char *, int); \
    GINFO *GCALL prefix##_info(void *, int); \
    int GCALL prefix##_read(void *, GINFO *, void *, int); \
    int GCALL prefix##_close(void *); \
    int GCALL prefix##_wopen(void **, GSTREAM *, const char *, int); \
    int GCALL prefix##_write(void *, const GINFO *, const void *, int); \
    int GCALL prefix##_wclose(void *);

#define GIMEX_ENTRY(prefix) \
    { prefix##_about, prefix##_is, prefix##_open, prefix##_info, prefix##_read, prefix##_close, \
      prefix##_wopen, prefix##_write, prefix##_wclose }

GIMEX_MODULE(NIL)

GMODULE gimexmodules[] = {
    GIMEX_ENTRY(NIL),   // 0  Nil Gimex 1.02
    { 0 } };

GFILTER gimexfilters[] = {
    { 0 } };

GQUANT gimexquantizers[] = {
    { 0 } };
