#include "frame_loop_clusters_295.hpp"

namespace porsche {
void __cdecl render_teardown_secondary_00465e20() {
    auto* object = render_secondary_object_0062810c;
    if (object != nullptr) {
        object->destroy_0059f1c0();
        application_release_0059f050(object);
    }
}
} // namespace porsche
