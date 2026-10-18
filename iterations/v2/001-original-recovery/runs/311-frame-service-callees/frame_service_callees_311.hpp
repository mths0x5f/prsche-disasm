// Original Porsche.exe SHA-256 ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39
#ifndef PORSCHE_FRAME_SERVICE_CALLEES_311_HPP
#define PORSCHE_FRAME_SERVICE_CALLEES_311_HPP

#include <cstdint>
#include <cstddef>

#if defined(_MSC_VER)
#define CALL_THISCALL __thiscall
#define CALL_CDECL __cdecl
#define CALL_FASTCALL __fastcall
#else
#define CALL_THISCALL
#define CALL_CDECL
#define CALL_FASTCALL
#endif

namespace porsche {

// ---------------------------------------------------------------------------
// 00423840: in-order tree successor. The field offsets below are the ones the
// original body actually dereferences: +0x04 parent, +0x08 left, +0x0c right.
// Offset +0x00 is never touched by this body and stays opaque here.
// ---------------------------------------------------------------------------
struct TreeNode_311 {
    std::uint32_t opaque_00;   // +0x00 not referenced by 00423840
    TreeNode_311* parent;      // +0x04 [edx+4]
    TreeNode_311* left;        // +0x08 [eax+8]
    TreeNode_311* right;       // +0x0c [edx+0xc]
};
static_assert(sizeof(TreeNode_311) == 0x10, "original node prefix");

// ---------------------------------------------------------------------------
// 00482e50: strided element array at this+0x40, element count at this+0x18.
// The original reloads both the count and the base pointer on every iteration.
// ---------------------------------------------------------------------------
struct FrameTailItem_311 {
    std::uint32_t opaque_00;      // +0x00
    float timer;                  // +0x04 [edx+4]
    std::uint8_t opaque_08[0x2c]; // +0x08..+0x33
    std::uint8_t active;          // +0x34 [eax+esi+0x34]
    std::uint8_t opaque_35[3];    // +0x35..+0x37
};
static_assert(sizeof(FrameTailItem_311) == 0x38, "original element stride");

struct FrameTailContext_311 {
    std::uint8_t opaque_00[0x18];
    std::uint32_t count;             // +0x18 [ecx+0x18]
    std::uint8_t opaque_1c[0x24];
    FrameTailItem_311* items;        // +0x40 [ecx+0x40]
};
static_assert(offsetof(FrameTailContext_311, count) == 0x18, "count offset");
static_assert(offsetof(FrameTailContext_311, items) == 0x40, "items offset");

// Read-only scalars the original body loads from .rdata.
extern "C" const float g_frame_tail_limit_005b47d8;  // 8000.0f
extern "C" const float g_frame_tail_delta_005b2764;  // 10000.0f

// ---------------------------------------------------------------------------
// 00476170: node transition & lifecycle dispatch.
// ---------------------------------------------------------------------------
struct FrameNodeObject_311;

struct FrameNodeVtable_311 {
    // slot 0 (+0x00): destructor, __thiscall with the flag pushed on the stack.
    void (CALL_THISCALL* destroy)(FrameNodeObject_311* self, std::int32_t flag);
    void* opaque_04[6];
    // slot 7 (+0x1c): lifecycle tick, __thiscall, no arguments.
    void (CALL_THISCALL* tick)(FrameNodeObject_311* self);
};
static_assert(offsetof(FrameNodeVtable_311, tick) == 0x1c, "tick slot");

struct FrameNodeObject_311 {
    FrameNodeVtable_311* vtable;  // +0x00 [ecx]
    std::uint8_t flag;            // +0x04 [ecx+4]
    std::uint8_t opaque_05[3];
};

struct FrameNodeElement_311 {
    std::uint8_t opaque_00[8];
    std::uint32_t field_08;            // +0x08 cleared on every iteration
    std::uint8_t opaque_0c[0x10];
    FrameNodeObject_311* object;       // +0x1c
    std::uint32_t opaque_20[3];        // +0x20..+0x2b
    std::uint32_t field_2c;            // +0x2c
    std::uint32_t opaque_30;           // +0x30
    std::uint32_t* carry_target;       // +0x34 destination of the 6-dword copy
};
static_assert(sizeof(FrameNodeElement_311) == 0x38, "original element stride");
static_assert(offsetof(FrameNodeElement_311, object) == 0x1c, "object offset");
static_assert(offsetof(FrameNodeElement_311, field_2c) == 0x2c, "field_2c offset");
static_assert(offsetof(FrameNodeElement_311, carry_target) == 0x34, "carry offset");

struct FrameNodeOwner_311 {
    std::uint8_t opaque_00[0x18];
    std::uint32_t count;   // +0x18 [[ebp+4]+0x18]
};

struct FrameActionContext_311 {
    std::uint32_t opaque_00;
    FrameNodeOwner_311* owner;      // +0x04
    std::uint32_t opaque_08;
    FrameNodeElement_311* elements; // +0x0c

    // External original callee 00476710 (136 bytes, not recovered in Run 311):
    // __thiscall on this same context, element index pushed on the stack.
    void CALL_THISCALL prepare_00476710(std::uint32_t index);
};
static_assert(offsetof(FrameActionContext_311, owner) == 0x04, "owner offset");
static_assert(offsetof(FrameActionContext_311, elements) == 0x0c, "elements offset");

} // namespace porsche

#endif // PORSCHE_FRAME_SERVICE_CALLEES_311_HPP
