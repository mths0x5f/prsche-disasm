// Platform setting, not original code.  The original links the VC6 static CRT, whose
// transcendental functions (sin, cos, …) run on x87 instructions.  The current static CRT picks
// SSE2 versions that differ in the last bit for some arguments, which changes Size filter output
// (9 of 471 oracle cases, ±1 in one channel).  Disabling the SSE2 path makes them match.

#include <math.h>

static int UseX87Math()
{
    return _set_SSE2_enable(0);
}

static int x87math = UseX87Math();
