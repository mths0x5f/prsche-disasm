#pragma once

#include <cstdint>
#include <cstddef>

namespace porsche {

// -----------------------------------------------------------------------------
// Function 1: 0048da60 (99 PE body bytes, 112 bytes allocated)
// Subsystem event dispatcher & lock synchronization.
// -----------------------------------------------------------------------------
struct SubsystemLockHandle {
    std::uint32_t handle;
};

struct SubsystemEventTarget {
    void __thiscall send_event_0048c870(
        std::uint32_t event_id,
        std::uint32_t arg1,
        std::uint32_t arg2,
        std::uint32_t unused1,
        std::uint32_t unused2
    );
};

struct SubsystemContext_00628c70 {
    std::uint8_t pad_00[0x08];
    void* active_handle_08;
    SubsystemEventTarget* event_target_0c;
    SubsystemLockHandle* lock_obj_10;
    std::uint8_t pad_14[0xa9];
    std::uint8_t dirty_flag_bd;
    std::uint8_t pad_be[1];
    std::uint8_t suppress_flag_bf;

    void __thiscall release_0048ff30();
};

extern SubsystemContext_00628c70* global_subsystem_00628c70;

void __cdecl lock_acquire_005322b0(std::uint32_t handle);
void __cdecl lock_release_005322c0(std::uint32_t handle);

void __cdecl application_main_function_0048da60(std::uint32_t arg1, std::uint32_t arg2);

// -----------------------------------------------------------------------------
// Function 2: 004acb80 (141 PE body bytes, 144 bytes allocated)
// Frame state and slot reset for global contexts 00656aa8..00656ab0.
// -----------------------------------------------------------------------------
struct ContextSlotState {
    std::int32_t slot_a;
    std::uint32_t pad[2];
};

struct FrameContext_00656aa8 {
    std::uint8_t pad_00[0x38];
    std::int32_t field_38;
    std::int32_t field_3c;
    std::uint8_t field_40;
    std::uint8_t pad_41[3];
    std::uint32_t slot_flags_44[32]; // 0x44 .. 0xc4
    std::uint8_t pad_c4[0x20e];
    std::uint8_t field_2d2;
    std::uint8_t field_2d3;
    std::uint8_t pad_2d4[0x188];
    ContextSlotState slots_45c[32]; // 0x45c .. 0x5dc (slot_a)
    ContextSlotState slots_5dc[32]; // 0x5dc .. 0x75c (slot_b)
};

extern FrameContext_00656aa8* global_contexts_00656aa8[2];

void __cdecl slot_release_00565d60(std::int32_t slot_id);
void __cdecl application_main_function_004acb80();

// -----------------------------------------------------------------------------
// Function 3: 00425780 (135 PE body bytes, 144 bytes allocated)
// Frame item updates and collection compaction.
// -----------------------------------------------------------------------------
struct FrameItem_00425780 {
    virtual void vtable_slot_0();
    virtual void vtable_slot_1();
    virtual void vtable_slot_2();
    virtual void vtable_slot_3();
    virtual void vtable_slot_4();
    virtual void __thiscall on_step_00425780(std::uint32_t param); // slot 5
    virtual std::uint32_t __thiscall is_active_00425780();          // slot 6
};

struct FrameItemEntry {
    FrameItem_00425780* item;
    std::uint32_t user_data;
};

struct FrameItemVector {
    FrameItemEntry* begin;
    FrameItemEntry* end;
    FrameItemEntry* capacity;
};

extern FrameItemVector* global_frame_items_vector_0060c9f4;
extern FrameItemVector* global_frame_items_vector_0060c9c4;

void __cdecl application_main_function_00425780();

// -----------------------------------------------------------------------------
// Function 4: 004b4cd0 (134 PE body bytes, 144 bytes allocated)
// Packet / command stream length decoder in DWORDs.
// -----------------------------------------------------------------------------
std::int32_t __cdecl application_main_function_004b4cd0(const std::uint32_t* packet);

} // namespace porsche
