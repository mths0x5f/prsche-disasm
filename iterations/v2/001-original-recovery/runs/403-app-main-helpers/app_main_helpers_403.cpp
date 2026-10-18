#include "app_main_helpers_403.hpp"

namespace porsche {

void __cdecl application_main_function_0048da60(std::uint32_t arg1, std::uint32_t arg2) {
    SubsystemContext_00628c70* sub = global_subsystem_00628c70;
    if (sub == nullptr || sub->active_handle_08 == nullptr || sub->suppress_flag_bf != 0u) {
        return;
    }

    SubsystemLockHandle* lock = sub->lock_obj_10;
    lock_acquire_005322b0(lock->handle);

    sub->event_target_0c->send_event_0048c870(0xb7u, arg1, arg2, 0u, 0u);
    global_subsystem_00628c70->dirty_flag_bd = 1u;

    lock_release_005322c0(lock->handle);
}

void __cdecl application_main_function_004acb80() {
    for (std::size_t c = 0; c < 2; ++c) {
        FrameContext_00656aa8* ctx = global_contexts_00656aa8[c];
        if (ctx == nullptr) {
            continue;
        }

        ctx->field_40 = 0u;
        ctx->field_2d3 = ctx->field_2d2;
        ctx->field_38 = -1;
        ctx->field_3c = -1;

        for (std::size_t i = 0; i < 32; ++i) {
            if (ctx->slots_45c[i].slot_a != -1) {
                slot_release_00565d60(ctx->slots_45c[i].slot_a);
            }
            if (ctx->slots_5dc[i].slot_a != -1) {
                slot_release_00565d60(ctx->slots_5dc[i].slot_a);
            }
            ctx->slot_flags_44[i] = 0u;
            ctx->slots_45c[i].slot_a = -1;
            ctx->slots_5dc[i].slot_a = -1;
        }
    }
}

void __cdecl application_main_function_00425780() {
    FrameItemVector* vec_f4 = global_frame_items_vector_0060c9f4;
    const std::size_t count = static_cast<std::size_t>(vec_f4->end - vec_f4->begin);
    for (std::size_t i = 0; i < count; ++i) {
        FrameItem_00425780* item = vec_f4->begin[i].item;
        if (item->is_active_00425780() != 0u) {
            vec_f4->begin[i].item->on_step_00425780(0u);
        }
    }

    FrameItemVector* vec_c4 = global_frame_items_vector_0060c9c4;
    FrameItemEntry* read_ptr = vec_c4->end;
    FrameItemEntry* write_ptr = vec_c4->begin;
    const std::size_t compact_count = static_cast<std::size_t>(vec_c4->end - read_ptr);
    if (compact_count > 0) {
        for (std::size_t i = 0; i < compact_count; ++i) {
            write_ptr[i] = read_ptr[i];
        }
    }
    const std::size_t removed = static_cast<std::size_t>(read_ptr - vec_c4->begin);
    vec_c4->end -= removed;
}

std::int32_t __cdecl application_main_function_004b4cd0(const std::uint32_t* packet) {
    const std::uint32_t opcode = packet[0];
    if (opcode >= 0x21eu) {
        return 3; // 12 bytes = 3 DWORDs
    }
    if (opcode >= 0x14eu) {
        return 2; // 8 bytes = 2 DWORDs
    }
    if (opcode >= 0x142u) {
        const std::uint32_t* base = (opcode >= 0x147u) ? (packet + 1) : packet;
        const std::uint32_t extra = base[1];
        return static_cast<std::int32_t>((base + extra + 2) - packet);
    }
    if (opcode >= 0x10eu) {
        const std::uint32_t* base = (opcode >= 0x13au) ? (packet + 1) : packet;
        const auto* cursor = reinterpret_cast<const std::uint8_t*>(base + 1);
        const auto* limit = reinterpret_cast<const std::uint8_t*>(base + 2);
        const std::uint32_t* dword_ptr = base;

        while (true) {
            const std::uint8_t b = *cursor;
            ++cursor;
            if (cursor > limit) {
                dword_ptr += 1;
                limit += 4;
            }
            if (b == 0u) {
                break;
            }
        }
        return static_cast<std::int32_t>((dword_ptr + 2) - packet);
    }
    return 2; // 8 bytes = 2 DWORDs
}

} // namespace porsche
