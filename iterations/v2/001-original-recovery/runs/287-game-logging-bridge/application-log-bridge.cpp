#include "porsche/application_main.hpp"
#include "porsche/formatter_stdio.hpp"

namespace porsche {
// Original 004b6b13 calls 005a177b with one string and ignores EAX.
void __cdecl application_main_log(const char* text) {
    formatter_stdio_printf_005a177b(text);
}
}
