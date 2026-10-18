// Original Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39
//
// Bodies recovered in this run. Run 290's consumer 00487e20 is the proven
// caller of all three, and this file supplies the member definitions that
// frame_service_290.hpp declared as external frontier:
//   00423840..00423882 (67 bytes)
//   00482e50..00482e94 (69 bytes)
//   00476170..00476218 (169 bytes)
#include "frame_service_callees_310.hpp"
#include "../290-frame-service-cluster/frame_service_290.hpp"

namespace porsche {

// Storage cell 00628960, declared extern by Run 290. The original is a single
// 32-bit pointer cell in writable data. A HIGHLOW operand scan of .text finds
// exactly three stores into it, in two owners: the initialiser 00471b70
// (00471bae writes the constructed object, 00471bb5 writes 0 when the
// allocation fails) and the teardown 00471c40 (00471c6d writes 0 after
// destructing and freeing the object). Neither owner is recovered in this run.
std::uint32_t frame_service_root_00628960 = 0;

// ---------------------------------------------------------------------------
// 00423840 (67 bytes): in-order tree successor.
// __thiscall; ECX points at the iterator's single node-pointer slot.
// ---------------------------------------------------------------------------
void CALL_THISCALL FrameIterator_290::advance_00423840() {
    TreeNode_310** const slot = reinterpret_cast<TreeNode_310**>(this);
    TreeNode_310* const node = *slot;          // 00423840: mov edx,[ecx]
    TreeNode_310* const right = node->right;   // 00423842: mov eax,[edx+0xc]

    if (right != nullptr) {                    // 00423845/47
        *slot = right;                         // 00423849: mov [ecx],eax
        if (right->left != nullptr) {          // 0042384b/4e/50
            TreeNode_310* next;
            do {
                next = (*slot)->left;          // 00423852/54: reloads [ecx]
                *slot = next;                  // 00423857
            } while (next->left != nullptr);   // 00423859/5c/5e
        }
        return;                                // 00423860 / 00423882
    }

    TreeNode_310* parent = node->parent;       // 00423861: mov eax,[edx+4]
    if (node == parent->right) {               // 00423865/68
        do {
            *slot = parent;                    // 0042386a
            parent = parent->parent;           // 0042386c
        } while (*slot == parent->right);      // 0042386f/71/74
    }
    if ((*slot)->right != parent) {            // 00423876/78/7b/7e
        *slot = parent;                        // 00423880
    }
}

// ---------------------------------------------------------------------------
// 00482e50 (69 bytes): advance the timer of every active element whose timer
// is not above the 8000.0f limit.
// ---------------------------------------------------------------------------
void CALL_THISCALL FrameTail_290::invoke_00482e50() {
    FrameTailContext_310* const self = reinterpret_cast<FrameTailContext_310*>(this);

    if (self->count == 0) {            // 00482e50/56/58 (unsigned jbe)
        return;
    }

    std::uint32_t index = 0;           // edi
    std::uint32_t offset = 0;          // esi, byte offset
    do {
        // 00482e5d reloads the base pointer inside the loop.
        std::uint8_t* const base = reinterpret_cast<std::uint8_t*>(self->items);
        FrameTailItem_310* const item =
            reinterpret_cast<FrameTailItem_310*>(base + offset);

        if (item->active != 0) {       // 00482e63/67/69
            // 00482e6b: fld [edx+4]; fcomp [0x5b47d8]; fnstsw ax;
            // 00482e76: test ah,0x41; je skip  ->  tests C0|C3, i.e. "not
            // greater". The unordered result sets C0 and C3, so a NaN timer
            // also takes the adjustment; !(x > limit) reproduces that exactly.
            if (!(item->timer > g_frame_tail_limit_005b47d8)) {
                // 00482e7b: fld [edx+4]; fadd [0x5b2764]; fstp [edx+4]
                item->timer = item->timer + g_frame_tail_delta_005b2764;
            }
        }

        ++index;                       // 00482e8a
        offset += 0x38;                // 00482e8b
    } while (index < self->count);     // 00482e87/8e/90 (count reloaded)
}

// ---------------------------------------------------------------------------
// 00476170 (169 bytes): per-element lifecycle transition and dispatch.
// ---------------------------------------------------------------------------
void CALL_THISCALL FrameAction_290::invoke_00476170() {
    FrameActionContext_310* const self =
        reinterpret_cast<FrameActionContext_310*>(this);

    if (self->owner->count == 0) {     // 00476177/7e/81/83 (unsigned jbe)
        return;
    }

    std::uint32_t index = 0;           // edi, spilled across the dword copy
    std::uint32_t offset = 0;          // ebx, byte offset
    do {
        // 0047618d reloads the element base inside the loop.
        std::uint8_t* base = reinterpret_cast<std::uint8_t*>(self->elements);
        FrameNodeElement_310* element =
            reinterpret_cast<FrameNodeElement_310*>(base + offset);

        if (element->object != nullptr) {          // 00476190/94/96
            self->prepare_00476710(index);         // 00476198/99/9b

            // 004761a0 reloads the base after the call.
            base = reinterpret_cast<std::uint8_t*>(self->elements);
            element = reinterpret_cast<FrameNodeElement_310*>(base + offset);
            FrameNodeObject_310* const object = element->object;

            // 004761aa loads the flag byte before the null check at 004761b8:
            // the original dereferences the reloaded pointer unconditionally.
            const std::uint8_t flag = object->flag;

            if (flag == 0 && element->field_2c == 0) {   // 004761ad..b6
                if (object != nullptr) {                 // 004761b8/ba
                    object->vtable->destroy(object, 1);  // 004761bc/be/c0
                }
                // 004761c2 reloads the base again before the store.
                base = reinterpret_cast<std::uint8_t*>(self->elements);
                element = reinterpret_cast<FrameNodeElement_310*>(base + offset);
                element->object = nullptr;               // 004761c5

                // 004761cd..df: rep movsd of 6 dwords from element+0x1c into
                // *(element+0x34). The first dword is the slot just cleared.
                base = reinterpret_cast<std::uint8_t*>(self->elements);
                element = reinterpret_cast<FrameNodeElement_310*>(base + offset);
                std::uint32_t* const dst = element->carry_target;
                const std::uint32_t* const src =
                    reinterpret_cast<const std::uint32_t*>(
                        reinterpret_cast<std::uint8_t*>(element) + 0x1c);
                for (std::uint32_t i = 0; i < 6; ++i) {
                    dst[i] = src[i];
                }
            } else if (object != nullptr && flag == 0) { // 004761e7..ed
                object->vtable->tick(object);            // 004761ef/f1
            }
        }

        // 004761f4..fc: base reloaded, index advanced, element+8 cleared.
        base = reinterpret_cast<std::uint8_t*>(self->elements);
        element = reinterpret_cast<FrameNodeElement_310*>(base + offset);
        ++index;
        element->field_08 = 0;

        offset += 0x38;                       // 00476207
    } while (index < self->owner->count);     // 00476204/0a/0d (count reloaded)
}

} // namespace porsche
