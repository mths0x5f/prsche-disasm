#include "porsche/startup_sequence.hpp"
#include "porsche/application_heap_state.hpp"
#include "../374-render-descriptor/render_descriptor.hpp"

namespace porsche {
// Porsche.exe 00569a90..00569aca is the global-flags form of the accepted
// 00569ad0 scan. Reuse its signed comparison and size-before-sentinel order.
std::uint32_t __cdecl startup_sequence_value_00569a90(){
    return application_heap_measure_00569ad0(render_descriptor_flags_005deb60);
}
}
