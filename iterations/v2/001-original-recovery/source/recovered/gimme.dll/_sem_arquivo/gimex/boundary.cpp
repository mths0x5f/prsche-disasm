// Recovery boundary reporting (not part of the original; see boundary.h).

#include "boundary.h"

int gimexboundaryhit;

int gimexboundary(const char *entry)
{
    gimexboundaryhit = 1;
    gerror("gimme recovery boundary: %s is not recovered\n", entry);
    return 0;
}
