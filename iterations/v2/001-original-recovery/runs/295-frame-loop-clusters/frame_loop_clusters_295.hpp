#pragma once

#include "porsche/application_alloc.hpp"
#include "porsche/application_context_base.hpp"
#include "porsche/application_main.hpp"
#include "porsche/application_state.hpp"
#include "porsche/fe_stream.hpp"
#include "porsche/file_wait.hpp"
#include "porsche/game_setup.hpp"
#include "porsche/heap.hpp"
#include "porsche/heap_locks.hpp"
#include "porsche/render_startup.hpp"
#include "porsche/startup_sequence.hpp"
#include "porsche/startup_service_516950.hpp"
#include "porsche/window_runtime.hpp"
#include "porsche/window_scheduler.hpp"

#include <cstdint>

namespace porsche {

static_assert(sizeof(void*) == 4, "original x86 pointer ABI");

// Cluster 1: 00412030 + 005338d0 (frame control slot release)
struct FrameControlIndexTuple_295 {
    std::int16_t slot_00;
    std::int16_t slot_02;
    std::int16_t slot_04;
    std::int16_t slot_06;
};
static_assert(sizeof(FrameControlIndexTuple_295) == 8);

struct FrameControlSlotEntry_295 {
    std::uint32_t active_00;
    std::uint32_t reserved_04;
    void* device_08;
    std::uint32_t state_0c;
    std::uint8_t reserved_10[0x80];
};
static_assert(sizeof(FrameControlSlotEntry_295) == 0x90);

extern std::uint32_t frame_control_enabled_005e940c;
extern std::uint32_t frame_control_index_005e9410;
extern FrameControlIndexTuple_295 frame_control_table_005e9420[4];
extern FrameControlSlotEntry_295 frame_control_slots_0069cb90[32];

void __cdecl frame_control_slot_release_005338d0(std::int32_t slot);

// Cluster 2: 00425780 (frame callback poll and vector compaction)
struct FrameCallbackObject_295 {
    virtual void __thiscall slot_00() = 0;
    virtual void __thiscall slot_04() = 0;
    virtual void __thiscall slot_08() = 0;
    virtual void __thiscall slot_0c() = 0;
    virtual void __thiscall slot_10() = 0;
    virtual void __thiscall notify_14(std::uint32_t zero) = 0;
    virtual std::uint32_t __thiscall poll_18() = 0;
};

struct FrameVector_295 {
    std::uint32_t begin;
    std::uint32_t end;
};
static_assert(sizeof(FrameVector_295) == 8);

extern FrameVector_295* frame_callback_vector_0060c9f4;
extern FrameVector_295* frame_compact_vector_0060c9c4;

// Cluster 3: 004acb80 + 00565d60 (frame audio channel sweep)
extern void* audio_channel_banks_00656aa8[2];
extern std::uint8_t audio_system_active_006b499c;

void __cdecl audio_backend_lock_005896d0();
std::int32_t __cdecl audio_backend_find_channel_00589d20(std::uint32_t handle);
std::uint32_t __cdecl audio_backend_next_voice_00590340(std::int32_t channel, std::uint32_t* voice_slot);
void __cdecl audio_backend_stop_voice_0058a8b0(std::uint32_t voice_slot);
void __cdecl audio_backend_unlock_005896f0();
std::int32_t __cdecl audio_channel_stop_00565d60(std::uint32_t handle);

// Cluster 4: 00414eb0 (frame race/session state reset)
extern std::uint32_t frame_reset_word_00606ab8;
extern std::uint8_t frame_reset_byte_00656858;
extern std::uint32_t frame_reset_word_00606a8c;
extern std::uint32_t frame_reset_word_00606a90;
extern std::uint32_t frame_reset_word_00606a98;
extern std::uint32_t frame_reset_word_00606a9c;
extern std::uint32_t frame_reset_word_00606aa0;
extern std::uint32_t frame_reset_source_005e99b8;
extern std::uint32_t frame_reset_word_006280f0;
extern std::uint32_t frame_reset_word_00606ac8;
extern std::uint32_t frame_reset_word_006280ec;
extern std::uint32_t frame_reset_word_006280e8;
extern std::uint32_t frame_reset_word_00628100;
extern std::uint32_t frame_reset_word_006280fc;
extern std::uint32_t frame_reset_word_006280f8;

void __cdecl frame_reset_service_004a4780(std::uint32_t value);
void __cdecl frame_reset_service_0044fd00(std::uint32_t value);
void __cdecl frame_reset_service_004030b0();
void __cdecl frame_reset_service_004069d0();
void __cdecl frame_reset_service_004066d0();
void __cdecl frame_reset_service_004110a0();
void __cdecl frame_reset_service_00406710();
void __cdecl frame_reset_service_004069e0();
void __cdecl frame_reset_service_004690a0();
void __cdecl frame_reset_service_00412150();

// Cluster 5: 00467740 + 004b7140 + 00465e20 + 00538d80 + 00539eb0 + 00540420 + 0047f190 + 00514990
struct VirtualDeleteSlot0_295 {
    virtual void __thiscall delete_slot0(std::uint32_t flags) = 0;
};

struct VirtualDeleteSlot1_295 {
    virtual void __thiscall slot_00() = 0;
    virtual void __thiscall delete_slot1(std::uint32_t flags) = 0;
};

struct RenderSecondaryObject_295 {
    void __thiscall destroy_0059f1c0();
};

struct RenderBufferCell_00539eb0 {
    void* buffer;
    void __thiscall release_00539eb0();
};
static_assert(sizeof(RenderBufferCell_00539eb0) == 4);

struct RenderSubobject_00538d80 {
    void __thiscall destroy_00538d80();
};

struct RenderMovieBridge_00540420 {
    void __thiscall destroy_00540420();
};

struct RenderChannel_00466500 {
    void __thiscall destroy_00466500();
};

struct RenderVector12_295 {
    std::uint32_t begin;
    std::uint32_t end;
    std::uint32_t capacity_end;
};
static_assert(sizeof(RenderVector12_295) == 12);

extern std::uint32_t render_teardown_state_0065b398;
extern RenderSecondaryObject_295* render_secondary_object_0062810c;
extern void* render_registry_root_00628bac;

void __cdecl render_teardown_prefix_004b7140();
void __cdecl render_teardown_secondary_00465e20();
void __cdecl render_registry_item_noop_00514990(void* item);
void __cdecl render_teardown_registry_0047f190();

// Cluster 6: 00563d30 + 00564700 + 00564750 + 00563bd0 + 00563c70 + 00563c30 + 00563cc0
struct StreamSlot_295 {
    std::uint32_t id;
    StreamSlot_295* next;
    std::uint32_t reserved_08;
    std::uint32_t state_0c;
    std::uint32_t buffer_10;
    void (__cdecl* callback_14)(std::uint32_t);
    std::uint32_t operation_18;
    std::uint32_t reserved_1c[4];
};
static_assert(sizeof(StreamSlot_295) == 0x2c);

struct StreamQueue_295 {
    StreamSlot_295* head;
    StreamSlot_295* tail;
};
static_assert(sizeof(StreamQueue_295) == 8);

extern StreamSlot_295* stream_slots_006a5bc0;
extern StreamQueue_295 stream_completed_queue_006a5bc8;
extern StreamQueue_295 stream_free_queue_006a5bd0;
extern std::int32_t stream_slot_count_006a5be0;
extern void* stream_archive_handle_006a5be4;
extern void* stream_queue_lock_006a5be8;

void __cdecl file_operation_cancel_00567cf0(std::uint32_t operation);
StreamSlot_295* __cdecl stream_slot_resolve_00564750(std::uint32_t handle);
void __cdecl stream_slot_cancel_00564700(std::uint32_t handle);
StreamSlot_295* __cdecl stream_queue_pop_00563c70(StreamQueue_295* queue);
void __cdecl stream_queue_push_00563c30(StreamQueue_295* queue, StreamSlot_295* slot);
void __cdecl stream_slot_finalize_00563cc0(StreamSlot_295* slot);
std::uint32_t __cdecl stream_completion_pump_00563bd0(std::uint32_t a, std::uint32_t b);

} // namespace porsche
